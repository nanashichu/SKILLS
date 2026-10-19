"""汇总每个计划目标项一行的CSV，保留失败与空结果，计算模块/全局BH。

python 汇总规格检验_模板.py 原生结果.csv --output-dir data/temp/YYYYMMDD_数据主题 --receipt 测试/分析类别/YYYYMMDD_任务/运行ID_核验回执.json
输入必需model,module,term,b,se,p,rc，可选事前primary；保留其他来源/样本/规格字段。
BH函数提取自知识产权法庭项目未保留检验复查/code/02_汇总并核验.py。
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd


def bh(p):
    """与项目相同：只校正有限p，分母为有效p数，未估计项q保持缺失。"""
    p = np.asarray(p, float)
    q = np.full(len(p), np.nan)
    good = np.flatnonzero(np.isfinite(p))
    order = good[np.argsort(p[good], kind='stable')]
    if len(order):
        v = p[order] * len(order) / np.arange(1, len(order) + 1)
        q[order] = np.minimum(1, np.minimum.accumulate(v[::-1])[::-1])
    return q


def trial_root(path):
    path = path.resolve()
    category = next((p for p in [path, *path.parents] if p.parent.name == '测试'), None)
    if category is None or category.name not in ('特征化事实', '异质性分析', '机制', '基准', '稳健性检验', '进一步分析', '初稿整理'):
        return None
    parts = path.relative_to(category).parts
    if not parts or not re.fullmatch(r'\d{8}(?:_\d{6})?_.+', parts[0]):
        return None
    return category / parts[0]


def summarize(source, output, receipt_path):
    for path in (output, receipt_path):
        if any('初稿' in p.parts for p in (path.absolute(), path.resolve())):
            raise ValueError('初稿默认只读，汇总回执请放测试任务目录')
    parts = [p.casefold() for p in output.resolve().parts]
    receipt_folder = receipt_path.resolve().parent
    receipt_trial = trial_root(receipt_folder)
    if not any(parts[i:i + 2] == ['data', 'temp'] for i in range(len(parts) - 1)):
        raise ValueError('汇总CSV集中data/temp；测试包只保存回执与数据引用')
    if receipt_trial is None:
        raise ValueError('汇总回执须放原测试任务包；采用后仍不使用根logs')
    targets = [output / '全部规格结果.csv', output / '模块汇总.csv', receipt_path]
    if source.resolve() in {p.resolve() for p in targets}:
        raise ValueError('汇总输出与来源路径冲突，禁止覆盖输入')
    if any(p.exists() for p in targets):
        raise ValueError('汇总输出已存在；复用原data/temp数据目录，读取未变结果或先保留被替代记录后再更新，不为重跑另建任务包')
    raw = source.read_bytes()
    # 标识符/来源字段保持原字面值；0001和NA不能被自动改成1或缺失。
    d = pd.read_csv(source, encoding='utf-8-sig', dtype=str, keep_default_na=False)
    required = ['model', 'module', 'term', 'b', 'se', 'p', 'rc']
    if d.empty or not set(required).issubset(d.columns):
        raise ValueError('CSV必须非空并含字段: ' + ','.join(required))
    if d[['model', 'module', 'term', 'rc']].apply(lambda s: s.str.strip().eq('')).any().any() or d.duplicated(['model', 'term']).any():
        raise ValueError('计划ID缺失或model+term重复')
    for name in ['b', 'se', 'p', 'rc']:
        d[name] = pd.to_numeric(d[name].replace('', np.nan), errors='raise')
    if (d.p.notna() & (~np.isfinite(d.p) | ~d.p.between(0, 1))).any():
        raise ValueError('原生p值不在[0,1]')
    if (d.rc.mod(1).ne(0) | d.rc.lt(0)).any():
        raise ValueError('rc必须为非负整数')
    supplied = d[['b', 'se', 'p']].notna().sum(axis=1)
    if (d.rc.eq(0) & supplied.between(1, 2)).any():
        raise ValueError('成功项b/se/p记录不完整，先核实原生来源，不能携带部分p冒充未估计项')
    valid = d.rc.eq(0) & supplied.eq(3)
    if (valid & (~np.isfinite(d.b) | ~np.isfinite(d.se) | d.se.le(0))).any():
        raise ValueError('成功估计须有有限b和正SE')
    if (d.rc.ne(0) & d[['b', 'se', 'p']].notna().any(axis=1)).any():
        raise ValueError('失败项携带估计值，检查是否残留上一模型e()')
    d['status'] = d.rc.map({498: 'target_unidentified', 2000: 'no_complete_sample', 430: 'not_converged'}).fillna('failed')
    d.loc[d.rc.eq(0), 'status'] = np.where(valid[d.rc.eq(0)], 'estimated', 'target_unestimated')
    if 'primary' in d.columns:
        primary = d.primary.str.strip().str.lower().map({'true': True, 'false': False, '1': True, '0': False})
        if primary.isna().any():
            raise ValueError('primary须为事前指定的true/false或1/0，不能缺失')
        d['primary'] = primary.astype(bool)
    eligible_p = d.p.where(valid)
    d['q_bh_global'] = bh(eligible_p)
    d['q_bh_module'] = np.nan
    d['q_bh_module_primary'] = np.nan
    for _, idx in d.groupby('module', sort=False).groups.items():
        d.loc[idx, 'q_bh_module'] = bh(eligible_p.loc[idx])
        if 'primary' in d.columns:
            chosen = idx[d.loc[idx, 'primary'].to_numpy()]
            d.loc[chosen, 'q_bh_module_primary'] = bh(eligible_p.loc[chosen])
    d['direction'] = np.where(valid, np.where(d.b.gt(0), 'positive', np.where(d.b.lt(0), 'negative', 'zero')), '')
    counts = []
    for module, group in d.groupby('module', sort=False):
        estimated = group.status.eq('estimated')
        counts.append({'module': module, 'planned': len(group), 'estimated': int(estimated.sum()),
                       'failed': int(group.rc.ne(0).sum()),
                       'target_unestimated': int(group.status.eq('target_unestimated').sum()),
                       'nominal_p05': int((estimated & group.p.lt(.05)).sum()),
                       'positive_p05': int((estimated & group.b.gt(0) & group.p.lt(.05)).sum()),
                       'negative_p05': int((estimated & group.b.lt(0) & group.p.lt(.05)).sum()),
                       'bh_module_p05': int(group.q_bh_module.lt(.05).sum()),
                       'bh_module_primary_p05': int(group.q_bh_module_primary.lt(.05).sum()),
                       'bh_global_p05': int(group.q_bh_global.lt(.05).sum())})
    output.mkdir(parents=True, exist_ok=True)
    d.to_csv(output / '全部规格结果.csv', index=False, encoding='utf-8-sig')
    pd.DataFrame(counts).to_csv(output / '模块汇总.csv', index=False, encoding='utf-8-sig')
    receipt = {'planned': len(d), 'estimated': int(valid.sum()), 'unestimated_or_failed': int((~valid).sum()),
               'source': str(source.resolve()), 'source_sha256': hashlib.sha256(raw).hexdigest(),
               'family_rule': '与项目相同：模块/事前primary/全局分别只校正有限p，分母为对应family有效p数；失败项p/q缺失，另报计划/成功/失败数',
               'regressions_rerun': False}
    if source.read_bytes() != raw:
        raise ValueError('来源在汇总期间发生变化')
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(summarize(args.source, args.output_dir, args.receipt), ensure_ascii=False, indent=2))
