# 本地环境配置

计算默认用Python；下面的Stata路径、包和批量命令仅用于最终版本确认后的核对或用户直接要求的Stata任务，不能据此自动执行旧主程序。执行阶段以[SKILL.md](../SKILL.md)为准。

## 1. Stata 环境

| 项目 | 路径 |
|------|------|
| Stata 可执行文件 | `E:\app\STATA\StataMP-64.exe` |
| 官方 PDF 文档 | `E:\app\STATA\docs\` |
| 示例数据 | `E:\app\STATA\auto.dta` |

### 已安装包

| 包名 | 版本 | 用途 |
|------|------|------|
| reghdfe | v6.12.4 | 固定效应回归 |
| ftools | v2.49.1 | reghdfe 依赖项 |
| ivreghdfe | v1.1.3 | IV + 固定效应 |
| winsor2 | - | 缩尾处理 |
| estout | - | 表格导出 |
| psmatch2 | - | 倾向得分匹配 |

### 批量运行

```cmd
"E:\app\STATA\StataMP-64.exe" /e do "C:\path\to\analysis.do"
```

---

## 2. Python 环境

### 推荐环境

```bash
conda activate research
```

### 核心包

```python
import pandas as pd
import numpy as np
from linearmodels.panel import PanelOLS
import statsmodels.api as sm
from scipy import stats
```

### 安装依赖

```bash
pip install linearmodels pandas numpy scipy statsmodels
```

---

## 3. 参考文献

| 类型 | 路径 |
|------|------|
| 中文顶刊论文 | `G:/【20260401】paperread/中文顶刊论文/` |
| Stata 官方文档 | `E:\app\STATA\docs\` |
| Awesome-Agent-Skills | `G:\2026年博二下学期\【20260301】博士大论文\Awesome-Agent-Skills-for-Empirical-Research\` |
