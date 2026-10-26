clear all
set more off
/*==================================================
project:       【{{OUTPUT_DATE}}】{{PROJECT_TITLE}}
Author:
E-email:
----------------------------------------------------
Creation Date:      {{DATE}}
Modification Date:
Do-file version:    01
References:
Input:
Output:
==================================================*/


****************************************************
*论文名  {{PROJECT_TITLE}}
****************************************************

// 定义主目录路径
local mainDir "{{ROOT_PATH}}"  // 替换为你的实际路径

cap mkdir "`mainDir'\RAW"
cap mkdir "`mainDir'\TEMP"
cap mkdir "`mainDir'\FINAL"
cap mkdir "`mainDir'\代码"
cap mkdir "`mainDir'\输出"


global path1 "{{ROOT_PATH}}"
global DR "$path1\Raw"   // 原始文件
global DT "$path1\Temp"  // 临时文件
global DF "$path1\Final" // 最终文件

//研究思路、文献依据写在这里



/*-------------------------------导入数据----------------------------------*/
/*-------------------------------导入数据----------------------------------*/
/*-------------------------------导入数据----------------------------------*/
/*-------------------------------导入数据----------------------------------*/
/*-------------------------------导入数据----------------------------------*/
**#1导入数据

/*================================================================*/
	**#1.1导入解释变量
/*================================================================*/
import excel "$DR\{{INDEP_VAR_SOURCE_FILE}}", sheet("Sheet1") firstrow clear
rename 年份 year
rename 股票代码 stkcd
duplicates drop stkcd year,force
cd $DT
save 【{{OUTPUT_DATE}}】解释变量,replace


/*================================================================*/
	**#1.2导入被解释变量
/*================================================================*/
**************************CSMAR表名**************************
import excel "$DR\{{DEP_VAR_SOURCE_FILE}}", sheet("sheet1") firstrow clear
//csmar
rename *,lower
labone, nrow(1)
drop in 1/2
//保留合并报表
keep if typrep=="A"
//提取年份,保留年末数据
gen year=substr(accper,1,4)
destring  year,replace
gen month=substr(accper,6,2)
keep if month=="12"
drop month
cd $DT
save 【{{OUTPUT_DATE}}】被解释变量,replace


/*================================================================*/
	**#1.3合并数据
/*================================================================*/
cd $DT
use 【{{OUTPUT_DATE}}】解释变量,clear
merge 1:1 stkcd year using 【{{OUTPUT_DATE}}】被解释变量
drop if _merge==2
drop _merge
//控制变量库，改成实际路径
cd {{CONTROLS_DATA_DIR}}
merge 1:1 stkcd year using {{CONTROLS_DATA_FILE}}
drop if _merge==2
drop _merge



/*-------------------------------处理数据----------------------------------*/
/*-------------------------------处理数据----------------------------------*/
/*-------------------------------处理数据----------------------------------*/
/*-------------------------------处理数据----------------------------------*/
/*-------------------------------处理数据----------------------------------*/
**#2处理数据

destring stkcd,gen(stk_id)

//标记A股
//A股股票的代码为0（深市A股、中小板）、6（沪市A股）、3（创业板）
gen A股=1  if substr(stkcd,1,1)=="0"|substr(stkcd,1,1)=="3"|substr(stkcd,1,1)=="6"

//标记ST、PT
gen ST=1  if strmatch(shortname,"*ST*")
gen PT=1  if strmatch(shortname,"*PT*")

//标记金融公司
gen 金融公司=1 if  substr(indcd,1,1)=="J"

/*======{{DEP_VAR}}========*/
//原始字段含义写在这里
// gen {{DEP_VAR}}=

/*======{{INDEP_VAR}}========*/
//原始字段含义写在这里
// gen {{INDEP_VAR}}=

replace Top1=Top1/100

winsor2 {{DEP_VAR}} {{INDEP_VAR}} {{CONTROLS_RAW}},cuts(1,99)

global 控制变量 "{{CONTROLS_LIST}}"

cd $DT
save 【{{OUTPUT_DATE}}】{{PROJECT_TITLE}}面板,replace



/*-------------------------------回归分析----------------------------------*/
/*-------------------------------回归分析----------------------------------*/
/*-------------------------------回归分析----------------------------------*/
/*-------------------------------回归分析----------------------------------*/
/*-------------------------------回归分析----------------------------------*/
**# 3回归分析

/*================================================================*/
**# 3.1基准回归（表{{TABLE_ID}}）
/*================================================================*/
cd $DT
use 【{{OUTPUT_DATE}}】{{PROJECT_TITLE}}面板,clear
//统一样本：第4列所需变量都不缺失，再加样本筛选条件
egen nmiss=rowmiss({{DEP_VAR}}_w {{INDEP_VAR}}_w $控制变量)
gen sample=1 if nmiss==0&year>={{YEAR_MIN}}&year<={{YEAR_MAX}}&A股==1&ST!=1&PT!=1&金融公司!=1
drop nmiss
tab sample

reg     {{DEP_VAR}}_w {{INDEP_VAR}}_w              if sample==1, vce(cluster stk_id)
est store r1
reg     {{DEP_VAR}}_w {{INDEP_VAR}}_w $控制变量     if sample==1, vce(cluster stk_id)
est store r2
reghdfe {{DEP_VAR}}_w {{INDEP_VAR}}_w              if sample==1,absorb(stk_id year)  vce(cluster stk_id)
est store r3
reghdfe {{DEP_VAR}}_w {{INDEP_VAR}}_w $控制变量     if sample==1,absorb(stk_id year)  vce(cluster stk_id)
est store r4

// cd $DF
// esttab r1 r2 r3 r4 using "基准回归.rtf", replace star(* 0.1 ** 0.05 *** 0.01) r2(%9.4f)   b(%9.4f) se(%7.4f)  compress nogap stats(N r2, fmt(%9.0f %9.4f)) varwidth(20) title("基准回归")

cd $DT
save 【{{OUTPUT_DATE}}】{{PROJECT_TITLE}}面板,replace

/*================================================================*/
**# 3.2描述性统计（用基准第4列样本）
/*================================================================*/
cd $DT
use 【{{OUTPUT_DATE}}】{{PROJECT_TITLE}}面板,clear
estpost summarize {{DEP_VAR}}_w {{INDEP_VAR}}_w $控制变量 if sample==1, detail
// cd $DF
// esttab using 描述性统计.rtf,replace cells("count mean(fmt(4)) sd(fmt(4)) min(fmt(4)) p25(fmt(4))  p50(fmt(4))  p75(fmt(4)) max(fmt(4))")



/*=====================================================================*/
**# 4异质性
/*=====================================================================*/
/*======================================================*/
	**#4.1大类————具体分组指标
/*======================================================*/
cd $DT
use 【{{OUTPUT_DATE}}】{{PROJECT_TITLE}}面板,clear
bysort year :egen mid=median(分组变量) if sample==1
gen high=1 if 分组变量>mid&分组变量!=.&sample==1
replace high=0 if high!=1&分组变量!=.&sample==1
tab high

reghdfe {{DEP_VAR}}_w {{INDEP_VAR}}_w $控制变量    if high==1&sample==1,absorb(stk_id year)  vce(cluster stk_id)
est store r1
reghdfe {{DEP_VAR}}_w {{INDEP_VAR}}_w $控制变量    if high==0&sample==1,absorb(stk_id year)  vce(cluster stk_id)
est store r2
// esttab r1 r2 using "异质性_分组变量.rtf", replace star(* 0.1 ** 0.05 *** 0.01) r2(%9.4f)   b(%9.4f) se(%7.4f)  compress nogap varwidth(20)

bdiff , group(high) model(reghdfe {{DEP_VAR}}_w {{INDEP_VAR}}_w $控制变量 ,absorb(stk_id year)  vce(cluster stk_id))   reps(500) bs first detail seed(10)



/*=====================================================================*/
**# 5机制
/*=====================================================================*/
/*================================================================*/
	**#5.1机制变量
/*================================================================*/
//机制变量口径出处：[1]作者.题目[J].期刊,年份.
cd $DT
use 【{{OUTPUT_DATE}}】{{PROJECT_TITLE}}面板,clear
// merge 1:1 stkcd year using 机制变量数据
// drop if _merge==2
// drop _merge
winsor2 机制变量,cuts(1,99)
reghdfe 机制变量_w {{INDEP_VAR}}_w              if sample==1,absorb(stk_id year)  vce(cluster stk_id)
est store r1
reghdfe 机制变量_w {{INDEP_VAR}}_w $控制变量     if sample==1,absorb(stk_id year)  vce(cluster stk_id)
est store r2
// esttab r1 r2 using "机制_机制变量.rtf", replace star(* 0.1 ** 0.05 *** 0.01) r2(%9.4f)   b(%9.4f) se(%7.4f)  compress nogap varwidth(20)



/*=====================================================================*/
**#6稳健性检验
/*=====================================================================*/
/*================================================================*/
	**#6.1替换被解释变量
/*================================================================*/
cd $DT
use 【{{OUTPUT_DATE}}】{{PROJECT_TITLE}}面板,clear
reghdfe 替代Y_w {{INDEP_VAR}}_w $控制变量     if sample==1,absorb(stk_id year)  vce(cluster stk_id)
est store r1
