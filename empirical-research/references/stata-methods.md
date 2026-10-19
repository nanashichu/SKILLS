# Stata 实证方法详解

> 使用阶段：依据[SKILL.md后端规则](../SKILL.md)，以下命令仅用于最终研究版本确认后的do核对/复现，或用户直接要求的Stata操作。日常筛选、数据调整、全套结果重跑及导表使用Python；已有ado或现用do不触发原生重跑。高成本置换/bootstrap不自动重复，核对覆盖范围和未执行项须明确记录。

## 1. 面板回归（reghdfe）

### 1.1 基准回归

```stata
* 单模型
reghdfe y x1 x2 x3, absorb(firm year) vce(cluster firm)
estimates store m1

* 多模型导出
eststo clear
eststo: reghdfe y x1, absorb(firm year) vce(cluster firm)
eststo: reghdfe y x1 x2, absorb(firm year) vce(cluster firm)
eststo: reghdfe y x1 x2 x3, absorb(firm year) vce(cluster firm)

esttab using "$tables/main.tex", replace ///
    se star(* 0.10 ** 0.05 *** 0.01) ///
    label booktabs title("基准回归结果")
```

### 1.2 控制变量组定义

```stata
* 定义控制变量组
local controls "L_size L_lev L_roa L_bm L_growth"
local controls_full "`controls' L_cash L_age L_board"

* 使用
reghdfe y x `controls', absorb(firm year) vce(cluster firm)
```

---

## 2. 双重差分（DiD）

### 2.1 经典 2x2 DiD

```stata
gen post = (year >= treatment_year)
gen treat_post = treated * post
reghdfe y treat_post `controls', absorb(firm year) vce(cluster firm)
```

### 2.2 事件研究法

```stata
* 方法1：生成交互项
forvalues i = -3/3 {
    gen t`i' = (rel_time == `i') * treated
}
reghdfe y t*, absorb(firm year) vce(cluster firm)

* 方法2：使用因子交互
reghdfe y ib(-1).rel_time##1.treated, absorb(firm year) vce(cluster firm)
```

### 2.3 交错 DiD（Callaway & Sant'Anna）

```stata
csdid y x1 x2, ivar(firm) time(year) gvar(first_treat) agg(event)
estat event, window(-3 3)
csdid_plot
```

### 2.4 Bacon 分解

```stata
bacondecomp y treat_post, ddetail
```

---

## 3. 机制检验

### 3.1 逐步回归法

```stata
* Step 1: X → Y（总效应）
reghdfe y x `controls', absorb(firm year) vce(cluster firm)
estimates store step1

* Step 2: X → M（中介变量）
reghdfe m x `controls', absorb(firm year) vce(cluster firm)
estimates store step2

* Step 3: X + M → Y（直接效应）
reghdfe y x m `controls', absorb(firm year) vce(cluster firm)
estimates store step3

* 导出
esttab step1 step2 step3 using "$tables/mechanism.tex", replace ///
    se star(* 0.10 ** 0.05 *** 0.01) booktabs
```

### 3.2 Sobel 检验

```stata
sgmediation y, mv(m) iv(x) cv(`controls')
```

---

## 4. 稳健性检验

```stata
* 1. 替换被解释变量
reghdfe y_alt x `controls', absorb(firm year) vce(cluster firm)

* 2. 替换解释变量
reghdfe y x_alt `controls', absorb(firm year) vce(cluster firm)

* 3. 滞后两期
gen L2_x = L2.x
reghdfe y L2_x `controls', absorb(firm year) vce(cluster firm)

* 4. 排除特定年份
reghdfe y x `controls' if year != 2020, absorb(firm year) vce(cluster firm)

* 5. 加入更多控制变量
reghdfe y x `controls_full', absorb(firm year) vce(cluster firm)

* 6. 改变聚类层级
reghdfe y x `controls', absorb(firm year) vce(cluster province)

* 7. PSM-DID
psmatch2 treat `controls', logit neighbor(1) ate
pstest `controls', both graph
reghdfe y treat_post `controls' if _weight != ., absorb(firm year) vce(cluster firm)
```

---

## 5. 异质性分析

### 5.1 分组回归

```stata
reghdfe y x `controls' if soe == 1, absorb(firm year) vce(cluster firm)
estimates store soe_yes
reghdfe y x `controls' if soe == 0, absorb(firm year) vce(cluster firm)
estimates store soe_no
```

### 5.2 组间系数差异检验

```stata
suest soe_yes soe_no
test [soe_yes_mean]x = [soe_no_mean]x
```

### 5.3 交互项

```stata
gen x_group = x * group_var
reghdfe y x group_var x_group `controls', absorb(firm year) vce(cluster firm)
```

---

## 6. 数据清洗

### 6.1 变量处理

```stata
* 重命名
rename *, lower

* 类型转换
destring income, replace force

* 缺失值检查
misstable summarize

* 异常值处理
winsor2 income, cuts(1 99) replace
```

### 6.2 滞后变量

```stata
* 设置面板
xtset firm_id year

* 生成滞后
gen L_x = L.x
gen L2_x = L2.x
gen F_x = F.x  // 前瞻
```

---

## 7. 致命错误清单

| 错误 | 错误示例 | 正确做法 |
|------|----------|----------|
| 缺失值排序 | `gen x = (y > 0)` | `gen x = (y > 0) if !missing(y)` |
| 赋值与比较混淆 | `if y = 1` | `if y == 1` |
| merge 后不检查 | 直接使用 | `tab _merge` |
| Local 少右引号 | `` `controls` `` | `` \`controls' `` |
| by 前未排序 | `by id:` | `bysort id:` |
