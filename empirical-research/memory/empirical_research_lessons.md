**目录日期统一在前（2026-10-10用户约定）。** 任务、采用项、结果版本和归档目录用`YYYYMMDD_主题`，例如`测试/机制/20261010_VC新口径`、`data/temp/20261010_VC获投企业家数_采用`；同日独立任务重名时用`YYYYMMDD_HHMMSS_主题`。日期取任务实际开始日，继续原尝试沿用原日期，不能以整理日替代历史任务日期；没有可靠日期时先查日志/来源，仍不明则标为待确认，不编造日期。data、raw、temp、final、do、code、result、table、figure、测试、归档、初稿等固定用途目录及数据/程序等包内分类保持用途名称，不强加日期。文件名继续遵循各自规则，现用代码仍按两位序号开头。旧目录改名先登记准确映射、检查重名和依赖，同步现用程序、README和两张清单，核验原文件；历史日志与回执保留原字节，通过路径映射回查。

2026-10-10最新阶段规则：未采用前，新增小型数据、候选面板、回归底表、b/V与实际样本统一在data/temp；代码、日志和文档留分类测试包；共享大库只读引用。只有用户明确整项或某项可以用，才提取相应必要链：数据到data/temp，Python到code，Stata.do到do，排版表到result/table，图到result/figure。采用后的分析用最终数据默认temp，已有final保留；另存final需要用户明确冻结归档要求。部分采用不提升其他尝试、不触发整体Stata核对。下文历史来源说明服从本条。

---
name: 实证研究注意事项
description: 博士实证研究中所有关键注意事项，包括文档格式、回归报告、代码规范等
type: feedback
---

# 实证研究注意事项

> 历史经验优先级声明（2026-10-10）：本文件保留早期项目经验，不作为当前任务的默认目录、计算后端、导出授权或版式规则。冲突时以用户本轮明确要求、当前[SKILL.md](../SKILL.md)及已确认参考Word为准。初稿只读；候选及现用数据、底表和样本集中data/temp，代码与非数据任务材料留分类测试包，采用不重复复制数据。日常计算用Python，先总结、按需展开，文档仅在相应格式获明确授权后导出，整体研究版本确认或明确要求才do核对。下文固定字号、边距、表宽及Stata示例不得覆盖这些规则。

## 一、文档格式规范

### 1. 字体设置（必须同时设置中英文）
```javascript
// 正确做法
font: { name: 'Times New Roman', eastAsia: 'FangSong' }

// 错误做法（只设置中文）
font: 'FangSong'
```

**原因**：Word 文档需要同时指定中英文字体，否则英文可能显示为默认字体。

### 2. 表格宽度（必须用 PERCENTAGE）
```javascript
// 正确做法
width: { size: 100, type: WidthType.PERCENTAGE }

// 错误做法（DXA 在 Google Docs 中显示异常）
width: { size: 9360, type: WidthType.DXA }
```

**原因**：PERCENTAGE 在所有平台（Word、Google Docs、WPS）都能正确显示。

### 3. 三线表格式
- 顶线：粗线（size: 12）
- 表头底线：细线（size: 4）
- 底线：粗线（size: 12）
- 其他：无边框

### 4. 回归表格：系数+标准误双行
```
变量名        -0.0032***
             (0.0009)
```
**不要**把系数和标准误放在同一行。

### 5. 表格美观规范

**列数控制**：一个表格列数不宜过多（建议不超过5-6列），列数过多时应拆分为多个表格。

**系数与标准误对齐**：
```javascript
// 系数行：[变量名, 系数1, 系数2, ...]
// 标准误行：[空单元格, 标准误1, 标准误2, ...]
function regRow(coef, se, isLast = false) {
    const borderType = isLast ? 'last' : 'normal';
    return [
        new TableRow({
            children: coef.map((c, i) => i === 0 ? cellItalic(c, borderType) : cell(c, borderType))
        }),
        new TableRow({
            children: [cell('', borderType), ...se.map(s => cell(s, borderType))]  // 第一格为空
        })
    ];
}
```

**表格拆分示例**（异质性分析）：
- 表1：产权性质与行业类型（4列）
- 表2：企业规模与区域位置（4列）

**Why**：表格列数过多会导致内容拥挤、字号被迫缩小、难以阅读，且打印时可能超出页面边界。

---

## 八、实证分析规范

### 1. 描述性统计样本数
描述性统计表的样本数应与基准回归一致，而非全样本。若基准回归N=38,689，描述性统计也应为N=38,689。

**Why**：描述性统计应反映实际回归样本的特征，便于读者理解回归结果。

### 2. 机制检验方法
现代实证研究多采用一步法：滞后一期解释变量对当期中介变量回归。

**核心逻辑**：
- 解释变量：L_digital_self（滞后一期）
- 中介变量：absacc、insthold、balance（当期）
- 检验X对M的影响，判断机制是否存在

**一步法优点**：
- 简洁明了，避免多重共线性问题
- 中介变量不应作为控制变量纳入基准回归
- 使用滞后一期解释变量有助于缓解反向因果

**表格格式**：
```
变量          信息透明度    外部监督    治理改善
              (absacc)     (insthold)  (balance)
L_digital    -0.0012*     -0.0821***   0.0015
             (-1.89)      (-4.12)      (1.15)
```

**注意**：被解释变量是当期中介变量，不是滞后一期中介变量。

### 3. 学术写作少用引号
学术概念、术语、固定表达不加引号，仅在直接引用原文时使用。

**正确**：本文考察了客户环境关注对供应商企业绿色创新的影响
**错误**：本文考察了"客户环境关注"对"供应商企业绿色创新"的影响

---

## 二、代码编写规范

### 1. JavaScript 中避免中文引号
```javascript
// 错误（会导致语法错误）
text: "本文研究表明"

// 正确
text: '本文研究表明'
// 或转义
text: "本文研究表明"
```

**原因**：中文引号 "" 在 JavaScript 中不是合法字符串分隔符。

### 2. 图片路径使用绝对路径
```javascript
// 正确
const imgFile = 'G:/项目/result/特征化事实/01_总体分布.png'

// 错误（相对路径可能找不到）
const imgFile = './result/特征化事实/01_总体分布.png'
```

### 3. ImageRun 必须指定 type
```javascript
// 正确
new ImageRun({
    type: 'png',  // 必须指定
    data: imgBuffer,
    transformation: { width: 500, height: 300 }
})

// 错误（缺少 type）
new ImageRun({
    data: imgBuffer,
    transformation: { width: 500, height: 300 }
})
```

---

本文保留历史经验；版式读取本轮参考稿，导出按需，初稿默认只读，Python/Stata执行条件及清理规则以当前SKILL.md为准，不执行历史默认值。

## 三、Stata 编程规范

### 1. merge 后必须检查 _merge
```stata
merge 1:1 id using other.dta
tab _merge              // 每次都要 tab
assert _merge == 3      // assert 前必须先 tab
drop _merge
```

**原因**：直接 assert 会静默失败，不报错但数据可能有问题。

### 2. 缺失值处理
```stata
// 错误（缺失值 > 所有数值）
gen high = (income > 50000)

// 正确
gen high = (income > 50000) if !missing(income)
```

### 3. by 需要先排序
```stata
// 错误
by id: gen first = (_n == 1)

// 正确
bysort id: gen first = (_n == 1)
```

---

## 四、Python 实证规范

### 1. 面板回归使用 linearmodels
```python
from linearmodels.panel import PanelOLS

# 设置多重索引
df = df.set_index(['firm_id', 'year'])

# 回归
model = PanelOLS(y, X, entity_effects=True, time_effects=True)
result = model.fit(cov_type='clustered', cluster_entity=True)
```

### 2. 聚类标准误
```python
# 正确（企业层面聚类）
result = model.fit(cov_type='clustered', cluster_entity=True)

# 错误（无聚类）
result = model.fit()
```

---

## 五、学术写作风格

### 1. 开篇模式
```
党的十八大以来.../近年来.../随着...政策的实施...
```

### 2. 结论表述
```
本文研究表明，X对Y具有显著的[正向/负向]影响...
实证检验发现，...
机制检验表明，...
```

### 3. 显著性报告
```
系数为-0.0032，在1%水平上显著（t=-3.56）
通过了1%水平上的显著性检验
```

---

## 六、变量命名规范

| 类型 | 前缀 | 示例 |
|------|------|------|
| 滞后一期 | L_ | L_digital_self |
| 滞后两期 | L2_ | L2_digital_self |
| 当期 | 无 | digital |
| 对数 | ln_ | ln_size |
| 比率 | _ratio | digital_ratio |

---

## 七、常见错误清单

| 错误 | 后果 | 解决方案 |
|------|------|----------|
| 中文引号 | JS 语法错误 | 用单引号或转义 |
| 表格用 DXA | Google Docs 显示异常 | 用 PERCENTAGE |
| 只设中文字体 | 英文显示异常 | 同时设置 eastAsia 和 name |
| merge 不检查 | 数据静默错误 | 必须 tab _merge |
| 缺失值不处理 | 结果错误 | 加 if !missing() |
| ImageRun 无 type | 报错 | 必须指定 type |

---

## 九、Skill 编写规范（Agent Skills 最佳实践）

### 1. SKILL.md 精简原则
- **行数限制**：SKILL.md < 500行，核心内容放主文件
- **渐进披露**：详细内容放入 references/ 子目录
- **结构清晰**：Step 1, Step 2... 编号明确

**示例结构**：
```
skill/
├── SKILL.md          # < 500行，核心规范
├── references/
│   ├── stata-methods.md
│   ├── python-methods.md
│   ├── report-generation.md
│   └── quality-gates.md
└── memory/
    └── lessons.md
```

**Why**：过长文件难以维护，渐进披露让用户快速找到核心内容。

### 2. 引用子文档方式
```markdown
**详细方法**：读取 `references/stata-methods.md`
```

---

## 十、异质性分析规范

### 1. 必须汇报组间系数差异检验

异质性分析表底部必须包含组间差异检验结果，不能只报告分组回归系数。

**表格格式**：
```
┌─────────────┬─────────────┬─────────────┐
│             │ 国企        │ 非国企      │
│             │ (1)         │ (2)         │
├─────────────┼─────────────┼─────────────┤
│ L_digital   │ -0.0090***  │ -0.0036     │
│             │ (0.0029)    │ (0.0035)    │
├─────────────┼─────────────┼─────────────┤
│ 组间差异    │ -0.0054**   │             │
│ (t值/p值)   │ (-2.52/0.012)│            │
└─────────────┴─────────────┴─────────────┘
```

### 2. 组间差异检验方法选择

| 方法 | 适用场景 | Python实现 |
|------|----------|------------|
| Chow检验 | 面板数据，大样本 | 构建交互项回归 |
| SUEST检验 | 横截面数据 | 日常按当前后端规则实现并核验，不能自动转Stata |
| Fisher组合检验 | 小样本，非参数 | 日常按当前后端规则实现并核验，不能自动转Stata |

**Python Chow检验实现**：
```python
def chow_test(panel, group_var, y_var, x_var, controls):
    """Chow检验：检验组间系数差异"""
    # 创建分组虚拟变量
    panel['group'] = (panel[group_var] == 1).astype(int)
    # 构建交互项
    panel['L_digital_x_group'] = panel['L_digital'] * panel['group']
    # 回归
    x_vars = ['L_digital', 'group', 'L_digital_x_group'] + controls
    result = run_panel_reg(panel, y_var, x_vars)
    # 交互项系数即为组间差异
    return extract_result(result, 'L_digital_x_group')
```

**Why**：仅报告分组系数无法判断组间差异是否统计显著，必须进行正式检验。

---

## 十一、Word 导出完整规范

### 1. 字体规范

| 元素 | 字体 | 字号 | 样式 |
|------|------|------|------|
| 中文 | 仿宋（FangSong） | 10pt | — |
| 英文/数字 | Times New Roman | 10pt | — |
| 变量名 | Times New Roman | 10pt | **斜体** |
| 字体颜色 | 黑色 | — | — |

### 2. 页面设置

| 设置 | 值 |
|------|-----|
| 左边距 | 1cm |
| 右边距 | 1cm |
| 上边距 | 2.54cm |
| 下边距 | 2.54cm |

### 3. 三线表格式

三线表只有三条横线：
1. **顶线**：表格最上方粗线（1.5pt）
2. **底线**：表格最下方粗线（1.5pt）
3. **表头线**：表头下方细线（0.75pt）

**注意**：无竖线，无其他横线。

### 4. Python 实现示例

```python
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.oxml.ns import qn

def set_font(run, chinese_font='FangSong', english_font='Times New Roman', size=10, italic=False):
    """设置字体：中文仿宋，英文Times New Roman，黑色"""
    run.font.size = Pt(size)
    run.font.name = english_font
    run.font.color.rgb = RGBColor(0, 0, 0)
    run.font.italic = italic
    run._element.rPr.rFonts.set(qn('w:eastAsia'), chinese_font)

def setup_page_margins(doc):
    """设置页边距：左右1cm，上下2.54cm"""
    for section in doc.sections:
        section.left_margin = Cm(1)
        section.right_margin = Cm(1)
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
```

**Why**：统一的文档规范确保所有表格风格一致，符合学术期刊投稿要求。
