"""用真实样本ID与全部解释变量独立FWL复核普通线性FE斜率；不核验SE/p。

python 核验固定效应系数_模板.py --panel 面板.csv --sample 实际样本.csv
  --native 原生斜率.csv --keys city_id year --y y --x did x1
  --fe city_id year --output 测试/分析类别/YYYYMMDD_任务/核验.json [--weight w] [--atol 1e-8]
原生斜率CSV必需term,b；传入一个模型对应的数据，stacked键自行包括stack。
加权交替去均值算法来自知识产权法庭项目未保留检验复查/code/02_汇总并核验.py。
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd


def residualize(values, groups, weights, tolerance=1e-11):
    z = np.asarray(values, dtype=float).copy()
    codes = [pd.factorize(g, sort=True)[0] for g in groups]
    for _ in range(3000):
        previous = z.copy()
        for code in codes:
            den = np.bincount(code, weights=weights)
            sums = np.zeros((len(den), z.shape[1]))
            np.add.at(sums, code, z * weights[:, None])
            z -= sums[code] / den[code, None]
        if np.max(np.abs(z - previous)) < tolerance:
            return z
    raise ValueError('固定效应投影未收敛')


def trial_root(path):
    path = path.resolve()
    category = next((p for p in [path, *path.parents] if p.parent.name == '测试'), None)
    if category is None or category.name not in ('特征化事实', '异质性分析', '机制', '基准', '稳健性检验', '进一步分析', '初稿整理'):
        return None
    parts = path.relative_to(category).parts
    if not parts or not re.fullmatch(r'\d{8}(?:_\d{6})?_.+', parts[0]):
        return None
    return category / parts[0]


def verify(args):
    if any('初稿' in p.parts for p in (args.output.absolute(), args.output.resolve())):
        raise ValueError('初稿默认只读，核验回执请放测试任务目录')
    folder = args.output.resolve().parent
    trial = trial_root(folder)
    if trial is None:
        raise ValueError('核验回执须放原测试任务包；采用后仍不使用根logs')
    if args.output.exists():
        raise ValueError('核验输出已存在，请先保留可恢复归档或使用独立任务路径')
    if not np.isfinite(args.atol) or args.atol < 0:
        raise ValueError('atol必须是有限非负数')
    paths = [args.panel, args.sample, args.native]
    if args.output.resolve() in {p.resolve() for p in paths}:
        raise ValueError('核验输出与来源路径冲突，禁止覆盖输入')
    fingerprints = {str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    # 不静默把001和1等字符串实体键认成同一主体。
    panel, sample, native = [pd.read_csv(p, encoding='utf-8-sig', dtype=str, keep_default_na=False) for p in paths]
    for frame in [panel, sample]:
        if frame[args.keys].apply(lambda s: s.str.strip().eq('')).any().any() or frame.duplicated(args.keys).any():
            raise ValueError('面板/样本主键缺失或不唯一')
    d = sample[args.keys].merge(panel, on=args.keys, how='left', validate='one_to_one', indicator=True)
    if d.empty or not d._merge.eq('both').all():
        raise ValueError('实际样本ID无法全部匹配面板')
    cols = [args.y] + args.x
    weights = np.ones(len(d)) if args.weight is None else pd.to_numeric(d[args.weight].replace('', np.nan), errors='raise').to_numpy(dtype=float)
    values = d[cols].replace('', np.nan).apply(pd.to_numeric, errors='raise').to_numpy(dtype=float)
    if not np.isfinite(values).all() or not np.isfinite(weights).all() or not (weights > 0).all():
        raise ValueError('实际样本有缺失/非有限值/非正权重，不能静默drop')
    if d[args.fe].apply(lambda s: s.str.strip().eq('')).any().any():
        raise ValueError('FE分组字段缺失')
    if native.term.duplicated().any() or not set(args.x).issubset(native.term):
        raise ValueError('原生斜率缺项或term重复')
    z = residualize(values, [d[c] for c in args.fe], weights)
    weighted = z * np.sqrt(weights[:, None])
    slopes, _, rank, _ = np.linalg.lstsq(weighted[:, 1:], weighted[:, 0], rcond=None)
    if rank != len(args.x):
        raise ValueError('FE内解释变量秩不足；检查吸收项，不能输出貌似一致的系数')
    expected = pd.to_numeric(native.set_index('term').loc[args.x, 'b'].replace('', np.nan), errors='raise').to_numpy(dtype=float)
    if not np.isfinite(expected).all():
        raise ValueError('原生斜率缺失或非有限值')
    difference = np.abs(slopes - expected)
    receipt = {'status': 'PASS' if np.all(difference <= args.atol) else 'FAIL', 'N': len(d),
               'keys': args.keys, 'fe': args.fe, 'weight': args.weight, 'atol': args.atol,
               'scope': '仅普通线性FE模型斜率的独立FWL核验；不核验SE/p或识别假设',
               'source_sha256': fingerprints,
               'coefficients': [{'term': t, 'native_b': float(b), 'FWL_b': float(f), 'absolute_difference': float(e)}
                                for t, b, f, e in zip(args.x, expected, slopes, difference)]}
    if not all(hashlib.sha256(p.read_bytes()).hexdigest() == fingerprints[str(p.resolve())] for p in paths):
        raise ValueError('来源在核验期间发生变化')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    if receipt['status'] != 'PASS':
        raise ValueError('FWL系数与原生系数不一致，见核验回执')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['panel', 'sample', 'native', 'output']:
        parser.add_argument('--' + name, type=Path, required=True)
    for name in ['keys', 'x', 'fe']:
        parser.add_argument('--' + name, nargs='+', required=True)
    parser.add_argument('--y', required=True)
    parser.add_argument('--weight')
    parser.add_argument('--atol', type=float, default=1e-8)
    args = parser.parse_args()
    if not np.isfinite(args.atol) or args.atol < 0:
        parser.error('--atol必须为有限非负数')
    print(json.dumps(verify(args), ensure_ascii=False, indent=2))
