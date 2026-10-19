"""Read-only data placement, do entry and small code checks; not a replication test."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import unquote


DATA_SUFFIXES = {'.dta', '.csv', '.tsv', '.txt', '.xlsx', '.xls', '.parquet', '.feather',
                 '.arrow', '.json', '.jsonl', '.ndjson', '.xml', '.npy', '.npz', '.pkl',
                 '.pickle', '.h5', '.hdf', '.hdf5', '.mat', '.sqlite', '.db', '.duckdb',
                 '.sas7bdat', '.sav', '.rds', '.rdata', '.ster', '.mdb', '.accdb'}
NON_DATA_SUFFIXES = {'.do', '.py', '.r', '.js', '.ts', '.ps1', '.bat', '.cmd', '.log',
                     '.smcl', '.md', '.rtf', '.docx', '.pdf', '.pptx', '.html', '.png',
                     '.jpg', '.jpeg', '.svg', '.eps', '.tif', '.tiff', '.webp', '.pyc'}
COMMON_GLOBALS = {'REPRO', 'ROOT', 'DATA', 'RAW', 'TEMP', 'FINAL', 'DO', 'CODE',
                  'RESULT', 'TABLE', 'FIGURE', 'LOGROOT', 'YEAR_MIN', 'YEAR_MAX',
                  'X', 'CONTROLS', 'PANEL', 'ENTITY', 'TIME', 'ABSORB', 'CLUSTER',
                  'HDFE', 'COEFLABELS', 'SAMPLE_IDS'}
LEGACY_GLOBALS = {'RUNROOT', 'RUNTEMP', 'RUNRESULT', 'RUNLOG', 'RUNPANEL', 'MASTER_RUNNING'}


def stata_commands(text):
    """Ignore comments and join /// lines for limited static command checks."""
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    text = re.sub(r'^\s*\*.*$', '', text, flags=re.M)
    text = text.replace('///\n', ' ')
    return text


def inspect(root, legacy_bundles=()):
    root = root.resolve()
    issues, warnings, duplicates = [], [], []
    if not root.is_dir():
        return {"root": str(root), "status": "MISSING_ROOT", "issues": ["项目目录不存在"],
                "warnings": [], "duplicates": [], "replication": "NOT_RUN", "modified_files": 0}
    # Fixed-purpose folders are created when needed, not to satisfy this checker.
    retained_bundles = set()
    for value in legacy_bundles:
        path = (root / value).resolve()
        parents = (root / 'data/raw', root / 'data/temp', root / 'code')
        if not path.is_dir() or not any(path != parent and path.is_relative_to(parent) for parent in parents):
            issues.append('历史源包登记无效，须为data/raw、data/temp或code内已有独立包：' + str(value))
        else:
            retained_bundles.add(path)
            warnings.append('已登记历史混合源包，保留内部相对布局；本检查不审其内部结构，仍需依赖/指纹核验：' + path.relative_to(root).as_posix())
    if (root / 'logs').exists():
        warnings.append('根logs属于旧目录约定；日志与追溯应留对应测试包，迁移前先查依赖，不自动删除')
    test = root / '测试'
    categories = {'特征化事实', '异质性分析', '机制', '基准', '稳健性检验', '进一步分析', '初稿整理'}
    if test.is_dir():
        for category in sorted(test.iterdir()):
            if not category.is_dir() or category.name not in categories:
                warnings.append('测试根只放七类目录；旧包迁移前先查依赖：' + category.relative_to(root).as_posix())
                continue
            for package in sorted(category.iterdir()):
                if not package.is_dir() or not re.fullmatch(r'\d{8}(?:_\d{6})?_.+', package.name):
                    warnings.append('分类下只放日期前置的完整任务包：' + package.relative_to(root).as_posix())
    data = root / "data"
    final = data / 'final'
    if final.is_dir():
        for path in final.iterdir():
            if path.is_dir():
                issues.append('final必须平铺，日期和版本写进DTA文件名：' + path.relative_to(root).as_posix())
            elif path.suffix.lower() != '.dta':
                issues.append('final只放各版本最终DTA：' + path.relative_to(root).as_posix())
    if data.is_dir():
        extras = sorted(p.name for p in data.iterdir() if p.name not in {"raw", "temp", "final"})
        if extras:
            issues.append("data直接子项不符合三类目录：" + ", ".join(extras))
        for current, folders, files in os.walk(data, followlinks=False):
            base = Path(current)
            if base.resolve() in retained_bundles:
                folders[:] = []
                continue
            for name in folders:
                if name.lower() in {'do', 'code', 'logs', 'result', 'paper', '__pycache__'}:
                    issues.append('data内不得嵌套程序/日志/结果目录：' + (base / name).relative_to(root).as_posix())
            for name in files:
                path = base / name
                relative = path.relative_to(root).as_posix()
                suffix = path.suffix.lower()
                if suffix in NON_DATA_SUFFIXES or name == '运行标记.txt':
                    issues.append('data只放数据，存在非数据产物：' + relative)
                elif suffix not in DATA_SUFFIXES:
                    warnings.append('需按实际内容确认是否数据文件：' + relative)
                if path.is_relative_to(data / 'final'):
                    if suffix == '.ster' or re.search(r'sample[_-]?ids|coefficients|样本ID|系数|底表|变量定义', name, re.I):
                        issues.append('final只放最终合成面板，中间数据应进temp：' + relative)
    manuscripts = root / '初稿'
    if manuscripts.is_dir():
        for path in sorted(manuscripts.iterdir()):
            if path.is_dir():
                warnings.append('初稿子目录需确认属于用户稿件；AI任务包应进测试：' + path.relative_to(root).as_posix())
        for current, folders, files in os.walk(manuscripts, followlinks=False):
            for name in files:
                path = Path(current) / name
                relative = path.relative_to(root).as_posix()
                if path.suffix.lower() not in {'.docx', '.doc', '.odt'}:
                    issues.append('初稿默认只放用户稿件，存在其他产物需审查去向：' + relative)
                elif re.search(r'汇编|结果汇总|完整结果|候选|诊断|导出|^表\d', name):
                    warnings.append('初稿中的结果文档需核实来源/授权，AI导出应进测试：' + relative)
    small_code = []
    settings_path = root / 'do/01_统一设置.do'
    settings = stata_commands(settings_path.read_text(encoding='utf-8-sig', errors='replace')) if settings_path.is_file() else ''
    shared_programs = {'save_sample_ids'} | set(re.findall(r'^\s*program\s+(?:define\s+)?(\w+)\b', settings, re.M))
    for folder in ("do", "code"):
        base = root / folder
        if not base.is_dir():
            continue
        for path in sorted(base.iterdir()):
            relative = path.relative_to(root).as_posix()
            if folder == "do" and path.is_file() and path.name == "README.md":
                continue
            if path.is_dir():
                if path.resolve() not in retained_bundles:
                    issues.append("现用目录需平铺；已有上游模块包应先登记依赖并显式保留：" + relative)
            elif folder == "do" and path.suffix.lower() != ".do":
                issues.append("do只放.do及唯一README.md入口说明：" + relative)
            elif folder == "do" and re.search(r"(?:^|_)(?:T\d+|表\d+|\d{2})\.do$", path.name, re.IGNORECASE):
                issues.append("逐表do文件名缺少具体表格主题：" + relative)
            elif folder == "do" and re.search(r"(?:^|_)T\d+_", path.name, re.IGNORECASE):
                issues.append("现用逐表do应按00_、01_、02_两位序号开头：" + relative)
            elif folder == 'do' and path.name != '主程序.do' and not re.match(r'^\d{2}_.+\.do$', path.name):
                issues.append('do需按两位工作序号开头并写明主题：' + relative)
            if folder == "code" and path.name.startswith("来源_"):
                warnings.append("来源副本需判断现用/历史，不能据文件名删除：" + relative)
            elif folder == "code" and path.is_file() and not re.match(r"^\d{2}_[^\.]+\.[^\.]+$", path.name):
                issues.append("code现用文件需按两位序号开头并写明用途：" + relative)
            if folder in {"do", "code"} and path.is_file() and path.stat().st_size <= 10 * 1024 * 1024:
                small_code.append(path)
                if path.suffix.lower() == '.py':
                    for lineno, line in enumerate(path.read_text(encoding='utf-8-sig', errors='replace').splitlines(), 1):
                        if re.match(r'^\s*(?:OUT|OUTPUT|OUTDIR|OUT_DIR)\s*=', line, re.I) and re.search(r'初稿(?:[/\\]|["\'])', line):
                            warnings.append(f'Python输出指向初稿，需核实具体稿件编辑授权；候选产物应改到测试：{relative}:{lineno}')
            if folder == 'do' and path.is_file() and path.suffix.lower() == '.do':
                commands = stata_commands(path.read_text(encoding='utf-8-sig', errors='replace'))
                prefix = r'^\s*(?:(?:capture|cap|quietly|qui|noisily|noi)\s+)*'
                for match in re.finditer(prefix + r'(preserve|restore)\b', commands, re.M | re.I):
                    issues.append('禁用数据现场命令' + match.group(1).lower() + '：' + relative)
                for match in re.finditer(r'^\s*(?:(?:quietly|qui|noisily|noi)\s+)*(capture|cap)\b', commands, re.M | re.I):
                    issues.append('do中不使用capture：' + relative)
                for macro in LEGACY_GLOBALS:
                    if re.search(r'\$\{?' + macro + r'\b|\bglobal\s+' + macro + r'\b', commands):
                        issues.append('不再使用运行状态宏' + macro + '：' + relative)
                if path.name in {'00_统一设置.do', '00_主程序.do'}:
                    issues.append('旧编号需改为01_统一设置.do或主程序.do：' + relative)
                if path.name != '01_统一设置.do':
                    setup = re.search(prefix + r'(?:do|run)\s+[^\n]*01_统一设置\.do', commands, re.M | re.I)
                    if path.name != '主程序.do' and not setup:
                        issues.append('独立do须先读取01_统一设置.do：' + relative)
                    if setup:
                        setup_path = re.sub(prefix + r'(?:do|run)\s+', '', setup.group(), flags=re.I)
                        if not re.match(r'^[\"\']?(?:[A-Za-z]:[\\/]|/|\\\\)', setup_path):
                            issues.append('首次读取统一设置须用绝对路径，不能依赖尚未定义的宏：' + relative)
                    data_input = re.search(prefix + r'(?:use|import\s+(?:delimited|excel|sas|spss|haver))\s+', commands, re.M | re.I)
                    if path.name != '主程序.do' and not data_input:
                        issues.append('独立do须显式读取数据（use/import）：' + relative)
                    if setup and data_input and setup.start() > data_input.start():
                        issues.append('须先读取统一设置再读取数据：' + relative)
                    regression = re.search(prefix + r'(?:reghdfe|regress|reg|xtreg|csdid|did2s|eventstudyinteract|did_multiplegt_dyn)\b', commands, re.M | re.I)
                    if data_input and regression and data_input.start() > regression.start():
                        issues.append('回归前须先显式读取输入数据：' + relative)
                    if re.search(r'\$\{?CONTROLS\b', commands) and not re.search(prefix + r'global\s+CONTROLS\b', settings, re.M):
                        issues.append('控制变量宏CONTROLS未在01统一设置定义：' + relative)
                    if re.search(r'\$\{?X\b', commands):
                        issues.append('控制变量宏统一为$CONTROLS，不再使用$X：' + relative)
                    for match in re.finditer(prefix + r'global\s+(\w+)\b', commands, re.M | re.I):
                        if match.group(1) in COMMON_GLOBALS:
                            issues.append('公共设置global ' + match.group(1) + '须集中01：' + relative)
                    for match in re.finditer(prefix + r'program\s+(?:define\s+)?(\w+)\b', commands, re.M | re.I):
                        if match.group(1) in shared_programs:
                            issues.append('共用程序' + match.group(1) + '须集中01：' + relative)
                elif re.search(prefix + r'(?:use|import|reghdfe|regress|xtreg)\b', commands, re.M | re.I):
                    issues.append('01统一设置不加载数据或估计模型：' + relative)
    result = root / "result"
    if result.is_dir():
        for path in sorted(result.iterdir()):
            if path.name not in {"table", "figure"} or not path.is_dir():
                issues.append("result只放table和figure目录：" + path.relative_to(root).as_posix())
        for folder, suffixes in (("table", {".rtf", ".docx", ".pdf"}), ("figure", {".png", ".jpg", ".jpeg", ".svg", ".pdf", ".eps", ".tif", ".tiff", ".webp"})):
            base = result / folder
            if base.is_dir():
                for path in sorted(base.iterdir()):
                    if folder == 'figure' and path.is_dir() and path.name == 'svg':
                        for svg in sorted(path.iterdir()):
                            if not svg.is_file() or svg.suffix.lower() != '.svg':
                                issues.append("SVG目录存在其他产物：" + svg.relative_to(root).as_posix())
                    elif not path.is_file() or path.suffix.lower() not in suffixes:
                        issues.append("最终图表目录存在其他产物：" + path.relative_to(root).as_posix())
    hashes = {}
    for path in small_code:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        hashes.setdefault(digest, []).append(path.relative_to(root).as_posix())
    for digest, paths in sorted(hashes.items()):
        if len(paths) > 1:
            duplicates.append({"sha256": digest, "paths": paths, "action": "核对引用后人工决定，未删除"})
    filenames = ["README.md", "CLAUDE.md"]
    readme_path = root / 'README.md'
    readme = readme_path.read_text(encoding='utf-8-sig', errors='replace') if readme_path.is_file() else ''
    links = re.findall(r'\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))\s*\)', readme)
    management_targets = {}
    for name in ('文件清单.csv', '图表对应.csv'):
        targets = set()
        for angled, plain in links:
            value = unquote(angled or plain).replace('\\', '/')
            if '://' in value or Path(value).name != name:
                continue
            path = (root / value).resolve()
            if path.is_relative_to((root / '测试').resolve()) and path.is_file():
                targets.add(path)
        if len(targets) != 1:
            warnings.append('README须以一个真实本地Markdown链接指向测试管理包内的' + name + '；当前有效目标数：' + str(len(targets)))
        else:
            management_targets[name] = next(iter(targets))
    if len(management_targets) == 2:
        parents = {path.parent for path in management_targets.values()}
        if len(parents) != 1 or next(iter(parents)).parent != (root / '测试/初稿整理').resolve():
            warnings.append('两张清单必须位于测试/初稿整理下的同一现用文件管理包')
    has_do = any((root / 'do').glob('*.do'))
    if has_do:
        filenames += ["do/00_导入原始数据与构建.do", "do/01_统一设置.do",
                      "do/02_变量定义.do", "do/03_描述性统计.do"]
    for filename in filenames:
        if not (root / filename).is_file():
            warnings.append("尚未建立或未使用新约定：" + filename)
    if has_do and not list((root / 'do').glob('04_*基准*.do')):
        warnings.append('尚未建立或未使用新约定：do/04_具体主题的基准回归.do')
    return {"root": str(root), "scope": "数据归位、初稿误放风险、常见Python输出变量的初稿字面路径、do静态入口及不超过10MiB的现用代码完全重复检查；不覆盖动态路径及显式登记历史源包内部，不要求预建未使用目录，不判断稿件作者/写入授权，不证明Stata独立运行",
            "status": "NEEDS_ATTENTION" if issues or warnings or duplicates else "STRUCTURE_PASS",
            "issues": issues, "warnings": warnings, "duplicates": duplicates,
            "replication": "NOT_RUN", "modified_files": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--legacy-bundle", action="append", default=[], help="已登记的历史混合源包或上游模块相对路径；须位于data/raw、data/temp或code内，可重复")
    args = parser.parse_args()
    print(json.dumps(inspect(args.root.resolve(), args.legacy_bundle), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
