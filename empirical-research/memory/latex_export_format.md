---
name: latex_export_format
description: Python回归脚本直接导出LaTeX三线表的转义和格式化规范
type: reference
---

# LaTeX 表格导出格式规范

## escape_latex 顺序（关键！）

```python
def escape_latex(text):
    text = str(text)
    # 先处理反斜杠，避免 \_ 中的 \ 被提前转义
    text = text.replace('\\', r'\textbackslash{}')
    # 再处理其他特殊字符
    replacements = {
        '_': r'\_',
        '%': r'\%',
        '#': r'\#',
        '&': r'\&',
        '$': r'\$',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    for char, escaped in replacements.items():
        text = text.replace(char, escaped)
    return text
```

**错误顺序**（先转义 `_` 再转义 `\`）：
- `L_digital` → `L\\_digital`（错误）

**正确顺序**：
- `L_digital` → `L\_digital`（正确）

## export_latex 三线表模板

```python
def export_latex(df, tex_file, caption, label):
    lines = []
    lines.append(r'\begin{table}[htbp]')
    lines.append(r'\centering')
    lines.append(r'\caption{' + caption + r'}')
    lines.append(r'\label{' + label + r'}')
    lines.append(r'\begin{threeparttable}')
    lines.append(r'\begin{tabular}{l' + 'c' * (len(df.columns) - 1) + '}')
    lines.append(r'\toprule')
    header = [r'\textit{' + escape_latex(str(col)) + '}' for col in df.columns]
    lines.append(' & '.join(header) + r' \\')
    lines.append(r'\midrule')
    for idx, row in df.iterrows():
        row_values = []
        for i, val in enumerate(row):
            val_str = str(val)
            if i == 0:
                # 第一列：斜体 + 转义
                row_values.append(r'\textit{' + escape_latex(val_str) + '}')
            elif isinstance(val, str) and ('***' in val or '**' in val or '*' in val):
                # 带星号系数：数学模式
                row_values.append(f'${val_str}$')
            elif isinstance(val, str) and val.startswith('(') and val.endswith(')'):
                # 标准误括号：直接输出
                row_values.append(val_str)
            else:
                row_values.append(val_str)
        lines.append(' & '.join(row_values) + r' \\')
    lines.append(r'\bottomrule')
    lines.append(r'\end{tabular}')
    lines.append(r'\begin{tablenotes}')
    lines.append(r'\footnotesize')
    lines.append(r'\item 注：*** p<0.01, ** p<0.05, * p<0.10。括号内为聚类稳健标准误。')
    lines.append(r'\end{tablenotes}')
    lines.append(r'\end{threeparttable}')
    lines.append(r'\end{table}')
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
```

## 工作流

回归脚本（如 04_baseline_ols.py）直接输出 LaTeX，不需要 Excel/docx 中转：

```
04_baseline_ols.py → 基准回归.tex（一步到位）
```

## 需要的 LaTeX 包

```latex
\usepackage{booktabs}
\usepackage{threeparttable}
\usepackage{array}
```
