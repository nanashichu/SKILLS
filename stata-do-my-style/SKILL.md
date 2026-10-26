---
name: "stata-do-my-style"
description: "写、改、整理任何 Stata do 文件时使用（导入清洗、合并、变量构造、描述统计、基准回归、异质性、机制、稳健性）：按我本人平铺直叙的写法，完整展示从原始数据到回归的全过程，不写封装助手和冗长说明头。"
---

# 按我的风格写 Stata do 文件

目标：别人打开 do 文件，从上往下读，就能看到**原始数据怎么导进来、怎么清洗、怎么合并成面板、怎么回归**。一行一步，平铺直叙，像我自己在 Stata 里一步步敲出来的。

## 一、总原则

1. **全流程可见**：从 `import excel` / `use 原始文件` 开始写，不要直接 `use 某某冻结输入.dta` 跳过清洗。每份原始数据单独一段：导入 → 清洗 → 标记 → `save`。
2. **能在 Stata 做的都在 Stata 做**：改名、取年份、筛选年末、去重、标记 A 股/ST/PT/金融、`egen` 分组统计、`merge`、`append`、`reshape`、`winsor2`、滞后项都用 Stata。只有 Stata 确实做不了的（如大规模文本分析、爬虫、复杂 NLP、超大文件拆分），才用 Python 处理，然后在 do 文件里**直接导入 Python 清洗后的结果**，并用一行注释说明这个文件是 Python 生成的、在哪个脚本里。
3. **少封装**：不写 `program define`、不写 `record_result`/`start_run`/`ensure_dir` 之类助手，不搞层层 `local` 拼接。`foreach` 只在真正重复的地方用（批量 destring、批量分组回归、批量导入同目录文件）。
4. **一行一步，注释说人话**：注释写变量含义、口径来源、为什么这样处理，用中文、用 `//`。不写"目的/步骤/时点/样本/处理/边界/运行/核验"那种大段说明。
5. **命令简短**：直接 `reghdfe`、`est store`、`esttab`，不要每条命令都加 `isid`、`assert`、`confirm` 等防御性检查（确有必要时只写一行 `duplicates report`）。

## 二、文件骨架（按这个顺序）

```stata
clear all
set more off 
/*==================================================
project:       【日期】论文名
Author:        
E-email:       
----------------------------------------------------
Creation Date:      
Modification Date:  
Do-file version:    01
References:       
Input:              
Output:             
==================================================*/

****************************************************
*论文名  xxxx
****************************************************

// 定义主目录路径
local mainDir "D:\xxx\【日期】项目名"  // 替换为你的实际路径
cap mkdir "`mainDir'\RAW"
cap mkdir "`mainDir'\TEMP"
cap mkdir "`mainDir'\FINAL"
cap mkdir "`mainDir'\代码"
cap mkdir "`mainDir'\输出"

global path1 "D:\xxx\【日期】项目名"
global DR "$path1\Raw"   // 原始文件
global DT "$path1\Temp"  // 临时文件
global DF "$path1\Final" // 最终文件

//研究思路、文献依据可以直接写几行注释放在这里
```

大节用五行横幅 + `**#` 书签；小节用等号框 + 缩进的 `**#` 书签，编号 1、1.1、4.2.1 这样往下：

```stata
/*-------------------------------导入数据----------------------------------*/
/*-------------------------------导入数据----------------------------------*/
/*-------------------------------导入数据----------------------------------*/
/*-------------------------------导入数据----------------------------------*/
/*-------------------------------导入数据----------------------------------*/
**#1导入数据

/*================================================================*/
	**#1.1导入解释变量
/*================================================================*/
```

固定的大节顺序：`**#1导入数据` → `**#2处理数据` → `**# 3回归分析`（3.1描述性统计、3.2基准回归）→ `**# 4异质性` → `**# 5机制` → `**#6稳健性检验`（培根分解、PSM、EBM、安慰剂等）→ 内生性/进一步分析按需加。再往下一级用 `**#4.2.1外部监督————媒体关注` 这种"大类————具体指标"的写法。

## 三、导入与清洗（每份原始数据一段）

数据库表用一行星号标题 + 缩进书签：

```stata
**************************资产负债表1990--2024年**************************
	**# 资产负债表
import excel "D:\数据中心\原始数据_dta\原始数据\公司指标\...\FS_Combas.xlsx", sheet("sheet1") firstrow clear
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

//定义面板数据
encode stkcd,gen(id)
xtset id year

//标记A股
//A股股票的代码为0（深市A股、中小板）、6（沪市A股）、3（创业板）
gen A股=1  if substr(stkcd,1,1)=="0"|substr(stkcd,1,1)=="3"|substr(stkcd,1,1)=="6"

//标记ST、PT
gen ST=1  if strmatch(shortname,"*ST*")
gen PT=1  if strmatch(shortname,"*PT*")

//标记金融公司
gen 金融公司=1 if  substr(indcd,1,1)=="J"

cd $DR
save 上市公司资产负债表（1990-2023）_70281,replace
```

要点：
- CSMAR 表固定套路：`rename *,lower` → `labone, nrow(1)` → `drop in 1/2` → `keep if typrep=="A"` → 取 year → 只留 12 月。没有这些字段的数据就删掉对应行，或者用 `//` 注释掉保留在那里。
- 非 CSMAR 数据（自己整理的 Excel、Wind、企查查）：`import excel ..., firstrow clear` → `keep` 需要的列 → `rename 中文列名 英文名`（如 `rename 年份 year`、`rename 股票代码 stkcd`）→ `duplicates drop stkcd year,force` → `save`。
- 同一文件夹下一批 Excel：用 `local filelist: dir . files "*.xlsx"` + `foreach` 逐个导入存 dta，再 `foreach` 循环 `append using`。
- 存档文件名：`中文表名（起止年份）_观测数`，或 `【日期】中文名_观测数`，一律 `,replace`。
- 运行后有用的 `tab` 结果可以贴在命令下面，但**每行前面加 `//`**，保证 do 文件能整体跑通。

## 四、合并

```stata
cd $DT
use 【20250811】机构投资者抱团,clear
rename Code stkcd
rename Year year
destring year ,replace
cd F:\【20250807】常见控制变量合集\公司特征\dta
merge 1:1 year stkcd using 【20250531】公司层面控制变量生成（1990_2024）_894502
drop if _merge==2
drop _merge
```

- 每次 `merge` 后紧跟 `drop if _merge==2`（或按需要 `==1`）和 `drop _merge`，必要时 `tab _merge` 并把结果用 `//` 贴在下面。
- 多表连续合并就一行 `merge` 一行 `drop _merge` 往下排，不写循环。
- 行业、城市层面数据用 `merge m:1 year indcd using ...`。
- 合并完成后 `cd $DT` + `save 【日期】论文名面板,replace`。

## 五、变量构造

每个变量一个小标题，下面写原始字段含义，再写构造：

```stata
/*======资产负债率========*/
//a002000000负债合计
//a001000000资产总计
destring a002000000 a001000000,replace
gen LEV=a002000000/a001000000  //资产负债率

/*======股权性质========*/
gen Soe=1 if strmatch(equitynature,"*国企*")
replace Soe=0 if Soe!=1

/*======营业收入增长率========*/
xtset stk_id year
sort stk_id year
gen L_b001101000=L.b001101000
gen Growth = (b001101000-L_b001101000)/L_b001101000
```

- 0/1 变量用 `gen x=1 if ...` + `replace x=0 if x!=1` 两行写法。
- DID 变量：`bys indcd (year): egen first_year = min(cond(punished==1, year, .))` → `gen treat=!missing(first_year)` → `gen post=(year>=first_year)` → `gen did=treat*post`，每步下面一行注释解释含义。
- 百分数统一换成小数：`replace Top1=Top1/100`。
- 缩尾一行写完：`winsor2 变量1 变量2 ... ,cuts(1,99)`，后续都用 `_w` 后缀变量。
- 控制变量用中文 global：`global 控制变量 "LEV_w SIZE_w ROA_w AGE_w TobinQ_w CF_w Boardsize_w Top1_w Mashare_w"`。

## 六、回归与输出

```stata
/*================================================================*/
**# 3.2基准回归
/*================================================================*/
cd $DT
use 【日期】论文名（全样本）,clear
reghdfe Y_w X_w                if year>=2004&year<=2022&A股==1&ST!=1&PT!=1&金融公司!=1&LEV<1,absorb(stk_id year)  vce(cluster stk_id)
est store r1
reghdfe Y_w X_w $控制变量       if year>=2004&year<=2022&A股==1&ST!=1&PT!=1&金融公司!=1&LEV<1,absorb(stk_id year)  vce(cluster stk_id)
est store r2
gen sample=1 if e(sample)==1

cd $DF
esttab r1 r2 using "基准回归.rtf", replace star(* 0.1 ** 0.05 *** 0.01) r2(%9.4f)   b(%9.4f) se(%7.4f)  compress nogap stats(Firm Year N r2, fmt(%3s %3s %3s %9.4f)) varwidth(20) title("基准回归") order(X_w)
```

- 样本筛选直接写在 `if` 里（`A股==1&ST!=1&PT!=1&金融公司!=1&LEV<1`），或基准回归后 `gen sample=1 if e(sample)==1`，后面统一 `if sample==1`。
- 先不加控制、再加控制，`r1 r2 r3 ...` 依次排，`if` 前用空格对齐。
- 描述性统计：`estpost summarize 变量 if sample==1, detail` + `esttab using 描述性统计.rtf,replace cells("count mean(fmt(4)) sd(fmt(4)) min(fmt(4)) p25(fmt(4)) p50(fmt(4)) p75(fmt(4)) max(fmt(4))")`。
- 异质性（分组回归）套路：每个分组变量一节，`use` 全样本 → `merge` 分组数据 → `bysort year: egen mid=median(var) if sample==1` → `gen high=1 if var>mid&var!=.&sample==1` → `replace high=0 if high!=1&var!=.&sample==1` → `tab high` → 两组 `reghdfe` → `esttab` → `bdiff, group(high) model(reghdfe ...) reps(40) bs first detail seed(10)` 检验组间差异。
- 机制：每个机制变量一节，`use` 全样本 → `merge` 机制数据 → `winsor2` → `reghdfe 机制变量 X` → `esttab`；构造口径的文献出处用 `//[1]作者.题目[J].期刊,年份` 注释写在节开头。
- 结果判断（"负的不显著""低组更显著"）可以用 `//` 一行记在回归旁边。

## 七、不要这样写（Codex 式繁琐写法）

下面都是之前 Codex 生成的代码里真实出现过、我不想要的写法，左边是反例，右边是我的写法：

| 不要 | 要 |
|---|---|
| 文件头在作者信息后面再加"TABLE_ID/目的/步骤/时点/样本/处理/边界/运行/核验"十几行 | 只留标准文件头 + `*论文名` 星号框，研究思路写几行 `//` |
| 开头堆 `version 16.0`、`set varabbrev off`、`program drop _all`、`sysdir set PLUS ...` | `clear all` + `set more off` 就够 |
| `program define ensure_dir / next_log / start_run / record_result / save_sample_ids / finish_run`，用 mata、frame、postfile 记录结果 | 不写 program；结果就是 `est store` + `esttab using xxx.rtf` |
| 一个项目拆成 `01_统一设置.do`…`13_xxx.do` 加一个只会挨个 `do` 的主程序，每个文件又 `do 01_统一设置.do` | 一个项目一个主 do 文件，从导入写到稳健性，用 `**#` 书签分节跳转 |
| `use "$INPUT/基准与远期_冻结输入.dta"`，变量早已算好，看不到来源 | 从原始 Excel/dta 导入，清洗、构造、合并都写出来 |
| `isid`、`assert r(N)==40293`、`assert !missing(...) if s001==1` 一检查几十行 | 必要时一行 `duplicates report stkcd year` 或 `tab _merge` |
| `s001 s002 ... s042` 这种预存样本标记、`record_result, model(T01_A_C01) sample(s001) expected(40293) groups(4838) params(2)` | 基准回归后 `gen sample=1 if e(sample)==1`，后面 `if sample==1` |
| 保存 `.ster`、全部 b/V 协方差、与 Python 参考值的差值 | 不需要 |
| 英文全大写 global：`$ROOT $REPRO $RAW $CONTROLS $ABSORB $CLUSTER $SAMPLE_IDS $YEAR_MIN` | `$path1 $DR $DT $DF $控制变量`，固定效应和聚类直接写在命令里 |
| `* 来源模型：PUB:CORE_NCSKEW_C1；真实N=40293，企业G=4838` 这种技术备注 | 注释写变量含义、口径来源文献、结果判断 |

## 八、交付时

- 先给完整 do 文件，再用两三句话说明：用了哪些原始文件、哪一步用了 Python 结果（如有）、需要我改的路径。
- 原始文件路径不知道就写成 `"D:\数据中心\原始数据_dta\原始数据\...\文件名.xlsx"` 占位，并在注释里写"改成实际路径"。