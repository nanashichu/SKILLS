/*==================================================
project: {{ROOT_PATH}}（生成时填写项目名称）
Author: 未记录（生成时填已确认作者）
E-email: 未记录（生成时填已确认邮箱）
Creation Date: {{DATE}}
Modification Date: {{DATE}}（生成后修改时更新）
Do-file version: v01（生成时按项目核定）
References: 项目README.md、CLAUDE.md；生成时补真实论文或来源
Input: $PANEL；生成时补本表额外输入与样本条件
Output: $TABLE/本表RTF；估计对象和样本ID进$TEMP
==================================================*/

**# 00 文件用途与运行说明
/*==============================================================================
文件名：{{DO_STEM}}.do
创建日期：{{DATE}}
论文表号：{{TABLE_ID}}（独立于工作序号）；输入PANEL，RTF输出TABLE，数据输出TEMP
目的：基准回归（默认四列；项目另有要求时以项目为准）

【硬约束 — 违反必出bug】
1. 滞后变量用 L./L2. 算子，禁止 bysort[_n-1]
2. esttab 不用 keep()、不用 drop(_cons)
3. reghdfe absorb() 后不写 drop(yr_*)
4. estimates store name 不超32字符
5. merge 后必须 tab _merge 确认匹配
6. bysort 后必须重新 xtset 再用 L. 算子
7. 适用的样本筛选在00构建完成，下游不重复剔除
8. 不使用 capture
9. 默认各列统一使用 _sample == 1 样本；偏离须由用户说明并在表注写明
10. esttab 保留常数项和控制变量系数

【文件管理约定】
1. 00构建、01设置、02变量定义、03描述统计，04起逐表；工作序号与论文表号分别登记
2. 本do先读取01设置，再明确读取输入；不依赖主程序或上一个do的会话
3. 候选与现用面板、底表、对象和样本均集中data/temp；未采用代码留原测试包，旧final保留
4. TEMP始终指data/temp；未采用TABLE/FIGURE在原包，采用后按授权进入result；LOGROOT始终在原包
5. 禁用preserve/restore与capture；数据切换明确save/use；estimates store/restore允许
6. 共用宏及助手集中01；替换正式产物前留归档；已有文件按确认清单清理

【本文件额外约束】
- 默认四列：(1)无控制无FE（reg） (2)有控制无FE（reg） (3)无控制有FE（reghdfe） (4)有控制有FE（reghdfe），列4为首选
- 四列统一使用 _sample == 1；reghdfe剔除单例可使3、4列N略小，实际样本以保存的真实ID为准
- 如实保存各列结果，包括与预期（{{EXPECTED_SIGN}}）不同或不显著的结果
- 如果方向不一致，先检查数据和变量构造，不要直接改模型

【esttab 标准格式】
esttab ... using "$TABLE/{{OUTPUT_DATE}}_{{TABLE_ID}}_主题.rtf", replace ///
    b(%9.4f) se(%7.4f) star(* 0.10 ** 0.05 *** 0.01) compress nogap ///
    stats(N r2, fmt(%9.0f %9.4f) labels("N" "R2"))

【变量命名】
滞后前缀 L_  差分前缀 D_  对数前缀 ln_
缺失值判断 if !missing(var)
==============================================================================*/

do "{{ROOT_PATH}}/do/01_统一设置.do"
* 用01中的next_log取未占用的运行编号日志；同名日志若因上次中断仍开着，先手动 log close step03
next_log, stem({{DO_STEM}})
log using "`r(file)'", name(step03) text

* ============================================================================
**# 01 读取数据
* 1. 读取数据
* ============================================================================
use "$PANEL", clear
xtset $ENTITY $TIME

* ============================================================================
**# 02 基准回归
* 2. 基准回归
* ============================================================================

* 列1: 无控制、无固定效应
reg {{DEP_VAR}} {{INDEP_VAR}} if _sample == 1, vce(cluster $CLUSTER)
eststo col1
estimates save "$TEMP/{{DO_STEM}}_col1.ster", replace
save_sample_ids, model(T{{TABLE_ID}}_col1)

* 列2: 有控制、无固定效应
reg {{DEP_VAR}} {{INDEP_VAR}} $CONTROLS if _sample == 1, vce(cluster $CLUSTER)
eststo col2
estimates save "$TEMP/{{DO_STEM}}_col2.ster", replace
save_sample_ids, model(T{{TABLE_ID}}_col2)

* 列3: 无控制、有固定效应
reghdfe {{DEP_VAR}} {{INDEP_VAR}} if _sample == 1, ///
    absorb($ABSORB) vce(cluster $CLUSTER) $HDFE
eststo col3
estimates save "$TEMP/{{DO_STEM}}_col3.ster", replace
save_sample_ids, model(T{{TABLE_ID}}_col3)

* 列4: 有控制、有固定效应（首选）
reghdfe {{DEP_VAR}} {{INDEP_VAR}} $CONTROLS if _sample == 1, ///
    absorb($ABSORB) vce(cluster $CLUSTER) $HDFE
eststo col4
estimates save "$TEMP/{{DO_STEM}}_col4.ster", replace
save_sample_ids, model(T{{TABLE_ID}}_col4)

* ============================================================================
**# 03 导出结果
* 3. 导出结果
* ============================================================================
/* RTF导出示例默认停用。
最终研究版本确认或Stata/do核对不授权生成RTF。
仅在用户明确授权本表RTF导出后，由生成器核实格式、输出范围和旧版归档，再启用下列示例。
核对已有结果时保留估计、样本与日志，不为启用导出另跑回归。
esttab col1 col2 col3 col4 using "$TABLE/{{OUTPUT_DATE}}_{{TABLE_ID}}_基准回归.rtf", replace ///
    b(%9.4f) se(%7.4f) star(* 0.10 ** 0.05 *** 0.01) compress nogap ///
    stats(N r2, fmt(%9.0f %9.4f) labels("N" "R2")) ///
    title("基准回归") ///
    mtitles("无控制无FE" "有控制无FE" "无控制有FE" "有控制有FE")
*/

eststo clear

log close step03
