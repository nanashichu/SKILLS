# Stata 实证方法详解

> 使用阶段：依据[SKILL.md后端规则](../SKILL.md)，以下命令仅用于最终研究版本确认后的do核对/复现，或用户直接要求的Stata操作。日常筛选、数据调整、全套结果重跑及导表使用Python；已有ado或现用do不触发原生重跑。高成本置换/bootstrap不自动重复，核对覆盖范围和未执行项须明确记录。

## 0. 默认回归规范（项目另有要求时以项目为准）

- 非0/1被解释变量用 `reghdfe`，固定效应写在 `absorb()`，不用 `i.year` 生成年份虚拟变量；0/1被解释变量用 `probit` 或面板 `xtprobit`（随机效应）。
- 控制变量统一用 01_统一设置.do 中的 `global CONTROLS`，全项目引用 `$CONTROLS`。
- 不使用 `capture`：不用它容错或掩盖报错；目录、日志、文件存在性检查用 01 的 `ensure_dir`、`next_log` 或 mata `fileexists()`。
- 基准回归默认四列：(1) 无控制无FE（`reg`）(2) 有控制无FE（`reg`）(3) 无控制有FE（`reghdfe`）(4) 有控制有FE（`reghdfe`，首选）。
- 统一样本：00 构建时标记 `_sample`（第4列所需全部变量非缺失），四列及后续机制、稳健、异质默认都用 `if _sample == 1`；偏离须用户说明。
- esttab 保留常数项和控制变量系数，不用 `keep()`、`drop(_cons)`；`reghdfe absorb()` 不生成年份系数，不写 `drop(yr_*)`。

```stata
reg     y x           if _sample == 1, vce(cluster $CLUSTER)
eststo col1
reg     y x $CONTROLS if _sample == 1, vce(cluster $CLUSTER)
eststo col2
reghdfe y x           if _sample == 1, absorb($ABSORB) vce(cluster $CLUSTER)
eststo col3
reghdfe y x $CONTROLS if _sample == 1, absorb($ABSORB) vce(cluster $CLUSTER)
eststo col4

* 导出段默认注释，用户明确授权本表RTF后启用
esttab col1 col2 col3 col4 using "$TABLE/YYYYMMDD_表X_基准回归.rtf", replace ///
    b(%9.4f) se(%7.4f) star(* 0.10 ** 0.05 *** 0.01) compress nogap ///
    stats(N r2, fmt(%9.0f %9.4f) labels("N" "R2")) varwidth(20) ///
    mtitles("无控制无FE" "有控制无FE" "无控制有FE" "有控制有FE") title("基准回归")
```

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

esttab using "$TABLE/YYYYMMDD_表X_基准回归.rtf", replace ///
    b(%9.4f) se(%7.4f) star(* 0.10 ** 0.05 *** 0.01) compress nogap ///
    stats(N r2, fmt(%9.0f %9.4f) labels("N" "R2")) title("基准回归结果")
```

### 1.2 控制变量组定义

```stata
* 控制变量组统一在 01_统一设置.do 中定义
global CONTROLS "L_size L_lev L_roa L_bm L_growth"
global CONTROLS_FULL "$CONTROLS L_cash L_age L_board"

* 使用
reghdfe y x $CONTROLS, absorb(firm year) vce(cluster firm)
```

---

## 2. 双重差分（DiD）

### 2.1 经典 2x2 DiD

```stata
gen post = (year >= treatment_year) if !missing(treatment_year)
replace post = 0 if missing(treatment_year)   // 从未处理组；按研究设计确认
gen treat_post = treated * post
reghdfe y treat_post $CONTROLS, absorb(firm year) vce(cluster firm)
```

### 2.2 事件研究法

```stata
* 方法1：生成交互项（变量名不能含负号；基期 -1 省略）
forvalues k = 2/3 {
    gen pre`k' = (rel_time == -`k') & treated == 1
}
gen cur = (rel_time == 0) & treated == 1
forvalues k = 1/3 {
    gen post`k' = (rel_time == `k') & treated == 1
}
reghdfe y pre3 pre2 cur post1 post2 post3, absorb(firm year) vce(cluster firm)

* 方法2：因子变量不接受负值，先平移相对期（-3…3 → 0…6，基期 -1 对应 2）
gen rel_s = rel_time + 3 if inrange(rel_time, -3, 3)
replace rel_s = 2 if missing(rel_s)    // 窗口外与从未处理组的处理方式按研究设计确认
reghdfe y ib2.rel_s#1.treated, absorb(firm year) vce(cluster firm)
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

### 3.1 一步法（默认）

只看 X 对当期机制变量 M 的影响；X 的时点、控制、FE、聚类和样本与基准回归一致，M 不放进基准回归。

```stata
reghdfe m x            if _sample == 1, absorb(firm year) vce(cluster firm)
eststo mech1
reghdfe m x $CONTROLS  if _sample == 1, absorb(firm year) vce(cluster firm)
eststo mech2
```

### 3.2 逐步回归法（仅项目要求两步法时）

> 逐步回归只提供机制证据，不等于完整的中介因果链；解释边界见 CLAUDE_empirical_analysis §14。

```stata
reghdfe y x $CONTROLS, absorb(firm year) vce(cluster firm)
estimates store step1
reghdfe m x $CONTROLS, absorb(firm year) vce(cluster firm)
estimates store step2
reghdfe y x m $CONTROLS, absorb(firm year) vce(cluster firm)
estimates store step3
```

### 3.3 Sobel 检验（仅两步法）

```stata
sgmediation y, mv(m) iv(x) cv($CONTROLS)
```

---

## 4. 稳健性检验

```stata
* 1. 替换被解释变量
reghdfe y_alt x $CONTROLS, absorb(firm year) vce(cluster firm)

* 2. 替换解释变量
reghdfe y x_alt $CONTROLS, absorb(firm year) vce(cluster firm)

* 3. 滞后两期
gen L2_x = L2.x
reghdfe y L2_x $CONTROLS, absorb(firm year) vce(cluster firm)

* 4. 排除特定年份
reghdfe y x $CONTROLS if year != 2020, absorb(firm year) vce(cluster firm)

* 5. 加入更多控制变量
reghdfe y x $CONTROLS_FULL, absorb(firm year) vce(cluster firm)

* 6. 改变聚类层级
reghdfe y x $CONTROLS, absorb(firm year) vce(cluster province)

* 7. PSM-DID
psmatch2 treat $CONTROLS, logit neighbor(1) ate
pstest $CONTROLS, both graph
reghdfe y treat_post $CONTROLS if _weight != ., absorb(firm year) vce(cluster firm)
```

---

## 5. 异质性分析

### 5.1 分组回归

```stata
reghdfe y x $CONTROLS if soe == 1, absorb(firm year) vce(cluster firm)
estimates store soe_yes
reghdfe y x $CONTROLS if soe == 0, absorb(firm year) vce(cluster firm)
estimates store soe_no
```

### 5.2 组间系数差异检验

```stata
* suest 不支持 reghdfe；用完全交互的合并模型检验组间差异（详见 group-difference-test.md）
reghdfe y c.x##i.soe c.($CONTROLS)#i.soe, absorb(firm year#soe) vce(cluster firm)
lincom x                   // 非国企组效应
lincom x + 1.soe#c.x       // 国企组效应
test 1.soe#c.x = 0         // 组间差异
```

### 5.3 交互项

```stata
gen x_group = x * group_var
reghdfe y x group_var x_group $CONTROLS, absorb(firm year) vce(cluster firm)
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

### 6.3 导入与合并经验

- 导入 Excel/CSV 后立即 `rename *, lower`，之后所有 rename/keep/destring 都用小写变量名。
- Excel 前一两行是中文表头说明时，先 `labone, nrow(1)` 转成变量标签，再 `drop in 1/2`，不要直接删。
- `destring` 只用于把字符串**值**转数值；CSMAR 字段代码（如 `A100000`）是列名，不需要 destring。
- merge 的键在 master 和 using 中必须同为数值或同为字符串；save using 前先统一类型。
- 同一文件在 save/use/merge 中的文件名必须完全一致；路径用 01 的全局宏，不在文件名里另拼日期宏。
- 缺失值在 merge 完、变量生成完后再处理；构建面板可以 drop，但每步前后 `count`，并登记删除数。
- 每次修改 do 都更新文件头的 Modification Date，精确到分钟（`YYYY-MM-DD HH:MM`）。

### 6.4 变量命名前缀

| 类型 | 前缀/后缀 | 示例 |
|------|-----------|------|
| 滞后一期 | L_ | L_digital |
| 滞后两期 | L2_ | L2_digital |
| 差分 | D_ | D_digital |
| 对数 | ln_ | ln_size |
| 比率 | _ratio | digital_ratio |

## 7. 致命错误清单

| 错误 | 错误示例 | 正确做法 |
|------|----------|----------|
| 缺失值排序 | `gen x = (y > 0)` | `gen x = (y > 0) if !missing(y)` |
| 赋值与比较混淆 | `if y = 1` | `if y == 1` |
| merge 后不检查 | 直接使用或直接 assert | 先 `tab _merge` 看匹配比例，再按需 `assert` |
| 用 capture 容错 | `capture reghdfe ...` 掩盖报错 | 不用 capture，让错误暴露后修正 |
| local 引用少右引号 | `` `controls` `` | `` `controls' ``（项目控制变量用 `$CONTROLS`） |
| by 前未排序 | `by id:` | `bysort id:` |
