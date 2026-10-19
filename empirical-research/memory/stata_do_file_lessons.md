---
name: stata_do_file_lessons
description: Stata do文件编写中犯过的错误和教训，博士实证研究专用
type: feedback
---

## Stata do文件编写规范（基于今天的错误）

### 1. 全局暂元PREFIX/日期前缀
- **不要**用 `${PREFIX}` 这种写法，在Windows Stata中可能不展开
- 直接写死日期前缀：`【20260406】` 或在文件开头定义 `global DATE "20260406"` 后用 `"${DATE}_xxx.dta"`
- 所有 save / use / merge 路径中，日期前缀必须**一致**

### 2. 变量名大小写问题
- Excel/CSV 原始文件列名可能是大小写混合（`D0`, `DIGITAL_INDEX_0_100`）
- 导入后**立即**用 `rename *, lower` 转小写
- 之后所有 rename/keep/destring 引用都用**小写**
- 常见错误：CSV 里是 `D0`（大写），代码写 `keep d0`（小写）→ 找不到变量

### 3. destring 转换时机
- 从 Stata dta 导入的字符串变量，需要 `destring varname, replace force` 转数值
- 从 Excel 导入的数值变量（代码如 `A100000`），其实是**字符串列名**，不需要 destring
- `destring` 只用于**变量值**的字符串转数值，不用于列名

### 4. labone 处理 Excel 中文表头
- Excel 文件前1-2行是中文表头说明，不能直接 `drop in 1/2`
- 先 `labone, nrow(1)` 把第一行转成变量标签，再 `drop in 1` 或 `drop in 1/2`
- 财务数据通常前两行都要删：`labone, nrow(1)` + `drop in 1/2`

### 5. 供应链数据筛选条件
- `statetypecode == "1"`（合并报表）**且**（上市公司 OR 关联公司）
- 关联公司判断：`!missing(isrelatedcompany)` — 只要 IsRelatedCompany 非空就保留
- IsRelatedCompany 值含义：1=联营公司，2=合营公司，3=子公司

### 6. 财务指标变量含义（必须查文档确认）
- `A100000` = 总资产（不是 `total_asset` 的别名，直接用）
- `D100000` = 经营活动产生的现金流量净额（不是负债！）
- `T30100` = 资产负债率（已经是比率，不需要再除）
- `T40401` = 资产收益率 ROA（已经是比率）
- `T40801` = 净资产收益率 ROE（已经是比率）
- 计算规模：`gen size = log(A100000)`（取对数）

### 7. merge 时的数据类型一致性
- merge 的 key 变量在 master 和 using 数据集中**必须同为数值型或同为字符串型**
- 常见错误：master 是 `long`，using 是 `str6`
- 解决：using 数据集 save 前确保 `destring stkcd, replace force`

### 8. 变量命名规则
- 所有 merge/use/save 路径中的文件名和变量名必须**严格对应**
- 写了 `save "【20260406】xxx.dta"` 就要写 `use "【20260406】xxx.dta"`
- 不能有的路径有日期前缀有的没有

### 9. 删除缺失值的时机
- 不要在数据清洗中间阶段大量 `drop if missing`
- 等 merge 完、变量生成完后再处理
- merge 后用 `keep if !missing(var)` 选择有效观测值

### 10. 时间戳更新
- 每次修改代码都要更新文件头的"最后更新"时间
- 精确到分钟：格式 `YYYY-MM-DD HH:MM`