# LaTeX 表格导出规范

## 1. 格式选择

| 格式 | 特点 | 适用场景 |
|------|------|----------|
| **booktabs** | 三线表样式（\toprule/\midrule/\bottomrule），更美观 | 学术论文标准格式 |
| **longtable** | 支持跨页分页，每页自动带表头 | 长表格（描述性统计、多列回归） |
| **threeparttable** | 支持表格下方注释（注释标记在表格内） | 需要星号解释的回归表 |

**默认组合**：
- 回归表：`booktabs` + `threeparttable`
- 描述性统计：`longtable` + `booktabs`

---

## 2. 必要宏包

```latex
\usepackage{booktabs}       % 三线表
\usepackage{longtable}      % 跨页表格
\usepackage{threeparttable} % 表格注释
\usepackage{array}          % 列格式扩展
\usepackage{multirow}       % 合并单元格
```

---

## 3. 回归结果表模板

```latex
\begin{table}[htbp]
\centering
\caption{基准回归结果}
\label{tab:baseline}
\begin{threeparttable}
\begin{tabular}{lccc}
\toprule
                    & \textit{CrashRisk} & \textit{CrashRisk} & \textit{CrashRisk} \\
                    & (1)                & (2)                & (3)                \\
\midrule
\textit{Digital}    & $-0.0065^{***}$    & $-0.0063^{***}$    & $-0.0047^{**}$     \\
                    & (0.0022)           & (0.0022)           & (0.0022)           \\
\textit{Lev}        & $0.0521^{***}$     & $0.0518^{***}$     & $0.0515^{***}$     \\
                    & (0.0048)           & (0.0048)           & (0.0048)           \\
\midrule
Controls            & Yes                & Yes                & Yes                \\
Firm FE             & No                 & Yes                & Yes                \\
Year FE             & No                 & No                 & Yes                \\
N                   & 37,414             & 37,414             & 37,414             \\
$R^{2}$             & 0.0821             & 0.0845             & 0.0867             \\
\bottomrule
\end{tabular}
\begin{tablenotes}
\footnotesize
\item 注：*** p<0.01, ** p<0.05, * p<0.10。括号内为聚类稳健标准误。
\end{tablenotes}
\end{threeparttable}
\end{table}
```

---

## 4. 描述性统计表模板（longtable）

```latex
\begin{longtable}{lcccccccc}
\caption{描述性统计} \label{tab:desc} \\
\toprule
\textit{Variable} & N & Mean & SD & Min & P25 & P50 & P75 & Max \\
\midrule
\endfirsthead
\toprule
\textit{Variable} & N & Mean & SD & Min & P25 & P50 & P75 & Max \\
\midrule
\endhead
\midrule
\multicolumn{9}{r}{\textit{续下页}} \\
\endfoot
\bottomrule
\endlastfoot

\textit{Digital}   & 37,414 & 0.2774 & 0.4477 & 0.0000 & 0.0000 & 0.0000 & 1.0000 & 1.0000 \\
\textit{Lev}       & 37,414 & 0.4387 & 0.2033 & 0.0523 & 0.2793 & 0.4365 & 0.5905 & 0.9976 \\
\textit{Size}      & 37,414 & 22.1532 & 1.2345 & 19.5678 & 21.3456 & 22.0123 & 22.9876 & 25.6789 \\
\end{longtable}
```

---

## 5. 异质性分析表模板

```latex
\begin{table}[htbp]
\centering
\caption{异质性分析}
\label{tab:hetero}
\begin{threeparttable}
\begin{tabular}{lcccc}
\toprule
                    & \textit{CrashRisk} & \textit{CrashRisk} & \textit{CrashRisk} & \textit{CrashRisk} \\
                    & 国企               & 非国企             & 高机构持股         & 低机构持股         \\
                    & (1)                & (2)                & (3)                & (4)                \\
\midrule
\textit{Digital}    & $-0.0090^{***}$    & $-0.0036$          & $-0.0058^{*}$      & $-0.0087^{***}$    \\
                    & (0.0029)           & (0.0035)           & (0.0034)           & (0.0034)           \\
\midrule
Controls            & Yes                & Yes                & Yes                & Yes                \\
Firm FE             & Yes                & Yes                & Yes                & Yes                \\
Year FE             & Yes                & Yes                & Yes                & Yes                \\
N                   & 15,214             & 22,200             & 18,707             & 18,707             \\
$R^{2}$             & 0.0821             & 0.0756             & 0.0789             & 0.0812             \\
\midrule
组间差异            & $-0.0054^{**}$     &                    & $0.0029$           &                    \\
(F值/p值)           & (4.12/0.042)       &                    & (0.85/0.356)       &                    \\
\bottomrule
\end{tabular}
\begin{tablenotes}
\footnotesize
\item 注：*** p<0.01, ** p<0.05, * p<0.10。组间差异采用Chow检验。
\end{tablenotes}
\end{threeparttable}
\end{table}
```

---

## 6. Python 实现示例

```python
def export_latex_table(df, table_type='regression', caption='', label=''):
    """
    导出 LaTeX 表格

    Parameters:
    -----------
    df : DataFrame
        表格数据
    table_type : str
        'regression' - 回归表（booktabs + threeparttable）
        'descriptive' - 描述性统计（longtable + booktabs）
        'heterogeneity' - 异质性分析
    caption : str
        表格标题
    label : str
        表格标签（用于交叉引用）
    """
    lines = []

    if table_type == 'regression':
        lines.append(r'\begin{table}[htbp]')
        lines.append(r'\centering')
        lines.append(f'\\caption{{{caption}}}')
        lines.append(f'\\label{{{label}}}')
        lines.append(r'\begin{threeparttable}')
        # ... 生成 tabular 内容
        lines.append(r'\end{threeparttable}')
        lines.append(r'\end{table}')

    elif table_type == 'descriptive':
        lines.append(r'\begin{longtable}{lcccccccc}')
        lines.append(f'\\caption{{{caption}}} \\label{{{label}}} \\\\')
        # ... 生成 longtable 内容
        lines.append(r'\end{longtable}')

    return '\n'.join(lines)


def format_coefficient(coef, se, stars=''):
    """格式化系数行"""
    coef_str = f'${coef:.4f}^{{{stars}}}$' if stars else f'${coef:.4f}$'
    se_str = f'({se:.4f})'
    return coef_str, se_str


def get_significance_stars(pvalue):
    """根据 p 值返回星号"""
    if pvalue < 0.01:
        return '***'
    elif pvalue < 0.05:
        return '**'
    elif pvalue < 0.10:
        return '*'
    return ''
```

---

## 7. Stata estout 导出 LaTeX

```stata
* 安装 estout（如未安装）
ssc install estout, replace

* 回归后导出 LaTeX 表格
esttab m1 m2 m3 using "baseline.tex", ///
    replace ///
    booktabs ///
    se ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(_cons) ///
    indicate("Controls = lev size roa" "Firm FE = *firm*" "Year FE = *year*") ///
    obslast ///
    r2 ///
    note("注：括号内为聚类稳健标准误。*** p<0.01, ** p<0.05, * p<0.10。")
```

---

## 8. 格式规范

| 元素 | 规范 |
|------|------|
| 变量名 | `\textit{变量名}` 斜体 |
| 系数 | `$数值^{星号}$` 数学模式 |
| 标准误 | `(数值)` 括号内，无星号 |
| 显著性 | `^{***}` / `^{**}` / `^{*}` 上标 |
| R² | `$R^{2}$` 数学模式 |
| 表注 | `tablenotes` 环境 |

---

## 9. 与 Word 格式对照

| 功能 | Word (docx) | LaTeX |
|------|-------------|-------|
| 三线表 | 手动设置边框 | booktabs 宏包 |
| 跨页表格 | 不支持 | longtable 宏包 |
| 表格注释 | 手动添加 | threeparttable 宏包 |
| 变量名斜体 | 手动设置 | \textit{} |
| 数学公式 | Equation Editor | $...$ |

---

**最后更新**：2026-04-24
