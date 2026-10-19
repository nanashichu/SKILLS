---
name: 年份限制规范
description: 实证研究中年份限制的处理方式
type: feedback
---

## 年份限制规范

**规则：设定年份限制时，不删除原始数据，只在回归代码中加条件。**

**Why：** 删除数据会导致数据丢失，无法回溯。保留完整数据，在分析时灵活筛选。

**How to apply：**
- ❌ 错误做法：在数据清洗阶段 `drop if year < 2012`
- ✅ 正确做法：在回归代码中加条件 `if year >= 2012 & year <= 2024`

**Stata 示例：**
```stata
* 在回归时限制年份
reghdfe ncskew L_digital $CONTROLS if year >= 2012 & year <= 2024, absorb(stkcd year) vce(cluster stkcd)
```

**Python 示例：**
```python
# 在回归时限制年份
reg_data = data[(data['year'] >= 2012) & (data['year'] <= 2024)]
```
