---
name: stata回归代码规范
description: Stata回归代码规范：reghdfe、absorb、四列基准回归、esttab格式、统一样本量
type: feedback
---

## 回归方法规范

### 核心规则

1. **非01变量**：统一使用 `reghdfe`，固定效应用 `absorb(stkcd year)`
2. **01变量**：使用 `xtprobit`（面板Probit）或 `probit`
3. **禁止使用 `i.year`**：固定效应必须用 `absorb()` 而非 `i.year`
4. **禁止使用 `capture`**：代码中不要用 `capture` 容错

### 基准回归四列设定

| 列 | 控制变量 | 固定效应 | 方法 |
|----|----------|----------|------|
| (1) | 无 | 无 | OLS (`reg`) |
| (2) | 有 | 无 | OLS (`reg`) |
| (3) | 无 | 有 | `reghdfe` + `absorb(stkcd year)` |
| (4) | 有 | 有 | `reghdfe` + `absorb(stkcd year)` |

### 统一样本量

**问题**：四列回归因控制变量缺失值不同，样本量不一致

**解决方案**：先标记有效样本，四列统一使用

```stata
* 标记有效样本（基于m4所需所有变量非缺失）
gen _sample_Y = .
replace _sample_Y = 1 if !missing(Y, L_digital) ///
    & !missing(L_Y, L_sigma, L_ret, L_dturn, L_size, L_lev, L_roa, L_bm) ///
    & year >= $YEAR_MIN & year <= $YEAR_MAX

* 四列回归统一使用 _sample_Y == 1
reg Y L_digital if _sample_Y == 1, vce(cluster stkcd)
estimates store m1

reg Y L_digital $CONTROLS if _sample_Y == 1, vce(cluster stkcd)
estimates store m2

reghdfe Y L_digital if _sample_Y == 1, absorb(stkcd year) vce(cluster stkcd)
estimates store m3

reghdfe Y L_digital $CONTROLS if _sample_Y == 1, absorb(stkcd year) vce(cluster stkcd)
estimates store m4
```

### 控制变量设定

**规则**：当被解释变量是 DUVOL 时，控制变量中滞后崩盘风险仍用 `L_NCSKEW_Mdeq`，不用 `L_DUVOL_Mdeq`

```stata
global CONTROLS L_NCSKEW_Mdeq L_sigma L_ret L_dturn L_size L_lev L_roa L_bm
global CONTROLS_DUVOL L_NCSKEW_Mdeq L_sigma L_ret L_dturn L_size L_lev L_roa L_bm
```

### 01变量回归

```stata
* 面板Probit（随机效应）
xtprobit CRASH L_digital $CONTROLS if _sample_Y == 1, re vce(cluster stkcd)
```

### esttab 导出格式

```stata
esttab m1 m2 m3 m4 using "$TABLE/回归结果.rtf", ///
    replace star(* 0.1 ** 0.05 *** 0.01) ///
    r2(%9.4f) b(%9.4f) se(%7.4f) ///
    compress nogap ///
    drop(_cons) ///
    stats(Firm Year N r2, fmt(%3s %3s %9.0f %9.4f)) ///
    varwidth(20) ///
    mtitles("无控制无FE" "有控制无FE" "无控制有FE" "有控制有FE") ///
    title("回归结果标题")
```

### 后续回归样本限制

所有后续回归（机制检验、稳健性检验、异质性分析、分位数回归）必须使用 `_sample_Y == 1`，确保与基准回归样本量一致。

---

**Why:** 用户明确要求统一回归方法、esttab格式、四列样本量一致。
**How to apply:** 所有Stata实证代码必须遵循此规范。

**最后更新：** 2026-04-26
