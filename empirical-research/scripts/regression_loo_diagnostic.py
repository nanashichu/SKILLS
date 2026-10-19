"""通用排除自身回归：传入拟合函数，或用公式接口快速计算线性回归。

排序依据全样本逐观测排除后的目标系数；固定排序，各删除量分别重新拟合。
formula_linear 支持控制、交互、C(类别)固定效应、单维聚类；不吸收高维FE。
任意其他估计器通过 regression_diagnostic 的 fit 回调接入，逐行重估。
所有结果保留；删除后的普通p值未校正依据结果选择样本造成的选择偏差。
"""
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


def linear_loo_coefficient(coefficient, slope, residual, leverage):
    """可供吸收FE/压缩数据适配器复用的精确线性排除公式。"""
    residual, leverage = np.asarray(residual, float), np.asarray(leverage, float)
    change = np.divide(np.asarray(slope)*residual, 1-leverage,
                       out=np.full(residual.shape, np.nan), where=1-leverage>1e-10)
    return coefficient-change


def summarize(result, target):
    """回调可返回statsmodels结果，或含 b/se/p/N 的字典。"""
    if isinstance(result, dict):
        if 'params' in result:
            result = dict(result, b=float(result['params'][target]))
        if 'b' not in result:
            raise ValueError('拟合函数返回字典须有 b 或 params[target]')
        return dict(result, status=result.get('status', 'PASS'))
    names = getattr(result.params, 'index', result.model.exog_names)
    position = list(names).index(target)
    params = np.asarray(result.params)
    cov = np.asarray(result.cov_params())
    return {'status': 'PASS', 'b': float(params[position]),
            'se': float(np.asarray(result.bse)[position]),
            'p': float(np.asarray(result.pvalues)[position]), 'N': int(result.nobs),
            'params': dict(zip(names, params.tolist())), 'terms': list(names),
            'V': cov.tolist(), 'df_resid': float(result.df_resid),
            'r2': float(result.rsquared) if hasattr(result, 'rsquared') else None,
            'cov_type': getattr(result, 'cov_type', None)}


def regression_diagnostic(data, fit, target, drop_counts=(2, 120), loo=None):
    """fit(dataframe)->估计对象；loo可提供与原始行顺序对应的精确排除系数。

    loo=None时逐条删除后调用fit，兼容非线性估计器但大样本会很慢。
    drop_counts事先固定，不依显著性停止；每个阶段从同一原始排序删除。
    """
    data = data.reset_index(drop=True)
    counts = sorted(set([0] + list(drop_counts)))
    if any(not isinstance(k, (int, np.integer)) or k < 0 or k >= len(data) for k in counts):
        raise ValueError('删除数量必须为非负整数，且小于总行数')
    original = fit(data)
    before = summarize(original, target)
    failures = []
    if loo is None:
        loo = np.full(len(data), np.nan)
        for i in range(len(data)):
            try:
                loo[i] = summarize(fit(data.drop(index=i)), target)['b']
            except Exception as error:
                failures.append({'row': i + 1, 'error': str(error)})
    loo = np.asarray(loo, float)
    if loo.shape != (len(data),):
        raise ValueError('loo长度须等于输入行数')
    ranking = pd.DataFrame({'original_row': np.arange(1, len(data) + 1),
                            'loo_b': loo, 'delta_b': loo - before['b']})
    ranking = ranking.sort_values(['loo_b', 'original_row'], ascending=[False, True],
                                  na_position='last').reset_index(drop=True)
    ranking.insert(0, 'rank', np.arange(1, len(data) + 1))
    stages = []
    for k in counts:
        removed = ranking.original_row.iloc[:k].to_numpy() - 1
        try:
            result = before if k == 0 else summarize(fit(data.drop(index=removed)), target)
        except Exception as error:
            result = {'status': 'FAILED', 'error': str(error)}
        tie = bool(0 < k < len(data) and ranking.loo_b.iloc[k - 1] == ranking.loo_b.iloc[k])
        stages.append(dict(result, drop=k, boundary_tie=tie))
    return {'ranking': ranking, 'stages': stages, 'loo_failures': failures,
            'target': target, 'ranking_recomputed': False,
            'inference_note': '删除后p值未经样本选择校正，仅用于影响诊断与探索。'}


def formula_linear(data, formula, target, cluster=None, drop_counts=(2, 120)):
    """多变量OLS精确快速排除系数；显式类别虚拟变量适合中小规模FE。"""
    data = data.reset_index(drop=True)
    if cluster is not None and data[cluster].isna().any():
        raise ValueError('聚类键缺失；请先明确并固定有效样本')

    def fit(frame):
        model = smf.ols(formula, data=frame)
        if np.linalg.matrix_rank(model.exog) < model.exog.shape[1]:
            raise ValueError('设计矩阵共线；请先固定可识别规格')
        if cluster is None:
            return model.fit()
        labels = model.data.row_labels
        return model.fit(cov_type='cluster', cov_kwds={'groups': frame.loc[labels, cluster],
                                                     'use_correction': True}, use_t=True)

    baseline = fit(data)
    X = baseline.model.exog
    target_position = baseline.model.exog_names.index(target)
    bread = np.asarray(baseline.normalized_cov_params)
    leverage = np.einsum('ij,jk,ik->i', X, bread, X)
    slope = X @ bread[:, target_position]
    estimated = float(baseline.params[target])
    values = linear_loo_coefficient(estimated, slope, baseline.resid, leverage)
    # 模型因缺失值未使用的行，排除后不改变有效回归样本。
    loo = np.full(len(data), estimated)
    loo[np.asarray(baseline.model.data.row_labels, int)] = values
    result = regression_diagnostic(data, fit, target, drop_counts, loo)
    result.update(formula=formula, cluster=cluster, method='精确OLS排除公式；各阶段重新拟合')
    return result


def check_output_paths(data_dir, log_dir, input_path=None):
    """Check all fixed targets before computation or writing; preserve prior evidence."""
    data_dir, log_dir = Path(data_dir), Path(log_dir)
    for folder in (data_dir, log_dir):
        if any('初稿' in p.parts for p in (folder.absolute(), folder.resolve())):
            raise ValueError('初稿默认只读，诊断非数据材料请放测试任务目录')
    parts = [p.casefold() for p in data_dir.resolve().parts]
    data_trial = next((p for p in [data_dir.resolve(), *data_dir.resolve().parents] if p.parent.name == '测试'), None)
    log_trial = next((p for p in [log_dir.resolve(), *log_dir.resolve().parents] if p.parent.name == '测试'), None)
    if data_trial is not None:
        if data_trial != log_trial:
            raise ValueError('试验数据和日志必须位于同一测试任务包')
    elif not any(parts[i:i + 2] == ['data', 'temp'] for i in range(len(parts) - 1)):
        raise ValueError('未采用数据须输出到测试任务包；已采用数据才使用data/temp')
    if log_trial is None:
        raise ValueError('诊断日志须放原测试任务包；采用后仍不使用根logs')
    targets = [data_dir / '逐观测排除系数与固定排序.parquet',
               data_dir / '全部删除阶段结果.csv',
               log_dir / '完整拟合与诊断记录.json', log_dir / '独立核验.json']
    if input_path is not None and Path(input_path).resolve() in {p.resolve() for p in targets}:
        raise ValueError('诊断输出与输入冲突，禁止覆盖来源')
    if any(p.exists() for p in targets):
        raise ValueError('诊断输出已存在，请先保留可恢复归档或使用独立任务路径')


def save_result(result, data_dir, log_dir):
    data_dir, log_dir = Path(data_dir), Path(log_dir)
    check_output_paths(data_dir, log_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    result['ranking'].to_parquet(data_dir / '逐观测排除系数与固定排序.parquet', index=False)
    rows = [{k: v for k, v in a.items() if k not in ['V', 'params', 'terms']} for a in result['stages']]
    pd.DataFrame(rows).to_csv(data_dir / '全部删除阶段结果.csv', index=False, encoding='utf-8-sig')
    report = {k: v for k, v in result.items() if k != 'ranking'}
    (log_dir / '完整拟合与诊断记录.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf-8')


def self_test():
    rng = np.random.default_rng(20261010)
    n = 80
    df = pd.DataFrame({'x': rng.normal(size=n), 'z': rng.normal(size=n),
                       'firm': np.repeat(np.arange(20), 4), 'year': np.tile(np.arange(4), 20)})
    df['city'] = df.firm % 5
    df['y'] = .2 * df.x - .4 * df.z + rng.normal(size=n) + df.firm * .03 + df.year * .04
    checks = []
    for formula in ['y ~ x', 'y ~ x + z + x:z', 'y ~ x + z + C(firm) + C(year)']:
        fast = formula_linear(df, formula, 'x', cluster='city', drop_counts=(2, 5))

        def slow_fit(frame):
            return smf.ols(formula, frame).fit(cov_type='cluster',
                    cov_kwds={'groups': frame.city, 'use_correction': True}, use_t=True)

        slow = regression_diagnostic(df, slow_fit, 'x', drop_counts=(2, 5))
        a = fast['ranking'].set_index('original_row').loo_b.sort_index()
        b = slow['ranking'].set_index('original_row').loo_b.sort_index()
        error = float(np.max(np.abs(a - b)))
        assert error < 1e-9
        assert fast['ranking'].original_row.tolist() == slow['ranking'].original_row.tolist()
        for f, s in zip(fast['stages'], slow['stages']):
            assert np.allclose([f['b'], f['se'], f['p']], [s['b'], s['se'], s['p']])
        checks.append({'formula': formula, 'loo_windows': n, 'max_b_error': error})
    logistic = df.iloc[:30].copy()
    logistic['binary'] = (rng.uniform(size=30) < 1 / (1 + np.exp(-.2 * logistic.x))).astype(int)
    def logit_fit(frame):
        return smf.logit('binary ~ x + z', frame).fit(disp=False)
    nonlinear = regression_diagnostic(logistic, logit_fit, 'x', drop_counts=(2,))
    assert not nonlinear['loo_failures'] and all(a['status'] == 'PASS' for a in nonlinear['stages'])
    return {'status': 'PASS', 'linear': checks, 'logit_windows': 30,
            'callback_Logit': 'PASS', 'Stata_executed': False}, fast


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path)
    parser.add_argument('--formula')
    parser.add_argument('--target')
    parser.add_argument('--cluster')
    parser.add_argument('--drop', nargs='+', type=int, default=[2, 120])
    parser.add_argument('--data-dir', type=Path, required=True)
    parser.add_argument('--log-dir', type=Path, required=True)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    check_output_paths(args.data_dir, args.log_dir, args.input)
    if args.self_test:
        qa, result = self_test()
        save_result(result, args.data_dir, args.log_dir)
        (args.log_dir / '独立核验.json').write_text(json.dumps(qa, ensure_ascii=False, indent=2), 'utf-8')
        print(json.dumps(qa, ensure_ascii=False))
        return
    if not all([args.input, args.formula, args.target]):
        parser.error('指定--input、--formula、--target，或用--self-test')
    readers = {'.dta': lambda p: pd.read_stata(p, convert_categoricals=False),
               '.parquet': pd.read_parquet, '.csv': pd.read_csv}
    data = readers[args.input.suffix.lower()](args.input)
    result = formula_linear(data, args.formula, args.target, args.cluster, args.drop)
    save_result(result, args.data_dir, args.log_dir)
    print(pd.DataFrame(result['stages'])[['drop', 'status', 'N', 'b', 'se', 'p']].to_string(index=False, float_format=lambda x: f'{x:.4f}'))


if __name__ == '__main__':
    main()
