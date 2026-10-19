---
name: stkcd变量格式规范
description: stkcd变量格式处理规范
type: feedback
---

## stkcd 变量格式规范

**规则：合并数据用字符串，回归用数值型 stkcdcode。**

**Why：** 
1. 合并数据时字符串格式便于匹配（补零后如 "000001"）
2. Stata 的 `xtset` 命令要求面板标识变量为数值型

**How to apply：**

### Python 数据处理
```python
# 合并数据时：用字符串格式
panel['stkcd'] = panel['stkcd'].astype(str).str.zfill(6)

# 生成最终面板时：创建数值型 stkcdcode
panel['stkcdcode'] = panel['stkcd'].astype(int)
```

### Stata 回归分析
```stata
* 使用数值型 stkcdcode 设置面板
xtset stkcdcode year

* 回归时也用 stkcdcode 作为聚类变量
reghdfe y x $CONTROLS, absorb(stkcdcode year) vce(cluster stkcdcode)
```

**变量说明：**
- `stkcd`：字符串格式，如 "000001"，用于数据合并和显示
- `stkcdcode`：数值型，如 1，用于 Stata 面板设置和聚类
