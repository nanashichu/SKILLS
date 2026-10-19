/*==================================================
project: {{ROOT_PATH}}（生成时填写项目名称）
Author: 未记录（生成时填已确认作者）
E-email: 未记录（生成时填已确认邮箱）
Creation Date: {{DATE}}
Modification Date: {{DATE}}（生成后修改时更新）
Do-file version: v01（生成时按项目核定）
References: 项目README.md、CLAUDE.md；生成时补真实论文或来源
Input: 项目路径与已确认的研究设定；不读取DTA
Output: 公共宏与助手（ensure_dir、next_log、save_sample_ids）；不生成DTA
==================================================*/

**# 00 文件用途与运行说明
/* 01_统一设置.do：公共路径、参数和助手；不加载数据、不重置种子。
   全项目不使用 capture：目录、日志与文件存在性检查都用下方助手（mata）完成。 */
* 本模板的frame样本助手需要Stata16或以上；STATA_VERSION也须填写至少16。
if c(stata_version)<16 | real("{{STATA_VERSION}}")<16 {
    display as error "frame样本助手需要Stata16或以上。"
    exit 9
}
version {{STATA_VERSION}}
set more off
set varabbrev off

**# 01 公共助手（不使用capture）
* 每次加载先清空内存中的用户程序再定义，避免 capture program drop。
program drop _all

* 目录不存在才创建
program define ensure_dir
    args path
    mata: st_local("has", strofreal(direxists(st_local("path"))))
    if "`has'" == "0" mkdir "`path'"
end

* 返回未占用的运行编号日志路径 r(file)；同一任务保留每次原生日志
program define next_log, rclass
    syntax, Stem(string)
    local n = 1
    local f "$LOGROOT/`stem'_run`n'.log"
    mata: st_local("has", strofreal(fileexists(st_local("f"))))
    while "`has'" == "1" {
        local ++n
        local f "$LOGROOT/`stem'_run`n'.log"
        mata: st_local("has", strofreal(fileexists(st_local("f"))))
    }
    return local file "`f'"
end

* 真实样本ID：普通e(sample)模型的公共助手；特殊估计器按真实接口另行配置
program define save_sample_ids
    syntax, Model(name)
    tempname sample_frame
    frame put $SAMPLE_IDS if e(sample), into(`sample_frame')
    frame `sample_frame': isid $SAMPLE_IDS
    frame `sample_frame': save "$TEMP/`model'_sample_ids.dta", replace
    frame drop `sample_frame'
end

**# 02 公共路径与年份
if "$REPRO"=="" global REPRO "{{ROOT_PATH}}"
if "$REPRO"!="{{ROOT_PATH}}" {
    display as error "REPRO与本项目路径不一致；请清空REPRO后重新运行本do。"
    exit 198
}
global ROOT "$REPRO"
global DATA "$ROOT/data"
global RAW "$ROOT/data/raw"
global TEMP "$ROOT/{{TASK_DATA_PATH}}"
global FINAL "$ROOT/data/final"
global DO "$ROOT/do"
global CODE "$ROOT/code"
global RESULT "$ROOT/result"
global TABLE "$RESULT/table"
global FIGURE "$RESULT/figure"
* TASK_CATEGORY 按本任务内容归入七类之一（如异质性分析）；不是字面文件夹名。
global LOGROOT "$ROOT/测试/{{TASK_CATEGORY}}/{{TASK_NAME_DATE}}"
* TASK_STAGE填trial或adopted；TEMP始终用data/temp中的实际数据位置。
* 未采用的显式Stata试验，表图同样留在本测试包；导出仍需相应授权。
if "{{TASK_STAGE}}"=="trial" {
    global DO "$LOGROOT"
    global CODE "$LOGROOT"
    global RESULT "$LOGROOT"
    global TABLE "$LOGROOT"
    global FIGURE "$LOGROOT"
}

global YEAR_MIN {{YEAR_MIN}}
global YEAR_MAX {{YEAR_MAX}}
* TASK_DATA_PATH：各阶段均填data/temp/YYYYMMDD_数据主题，状态另行登记；PANEL_RELATIVE_PATH填实际输入或未占用的新输出。
* TASK_NAME_DATE填YYYYMMDD_主题（重名时YYYYMMDD_HHMMSS_主题），指原测试证据包；继续、采用或获授权重跑不换包名，不创建根logs。
* 仅准备本次计算实际写入的中间数据和日志位置，复用原任务包；不预建RAW/FINAL/RESULT。
ensure_dir "$DATA"
ensure_dir "$DATA/temp"
ensure_dir "$TEMP"
ensure_dir "$ROOT/测试"
ensure_dir "$ROOT/测试/{{TASK_CATEGORY}}"
ensure_dir "$LOGROOT"

**# 03 统一变量与回归设置
* 控制变量宏统一命名为 CONTROLS，全项目用 $CONTROLS 引用
global CONTROLS {{CONTROLS_LIST}}
global PANEL "$ROOT/{{PANEL_RELATIVE_PATH}}"
global ENTITY "{{ENTITY_VAR}}"
global TIME "{{TIME_VAR}}"
global ABSORB "{{FE_VARS}}"
global CLUSTER "{{CLUSTER_VAR}}"
global HDFE "{{HDFE_OPTIONS}}"
global COEFLABELS {{COEF_LABELS}}
global SAMPLE_IDS "{{SAMPLE_ID_VARS}}"

{{SHARED_SETUP_CODE}}
