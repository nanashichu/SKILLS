/*==================================================
project: {{ROOT_PATH}}（生成时填写项目名称）
Author: 未记录（生成时填已确认作者）
E-email: 未记录（生成时填已确认邮箱）
Creation Date: {{DATE}}
Modification Date: {{DATE}}（生成后修改时更新）
Do-file version: v01（生成时按项目核定）
References: 项目README.md、CLAUDE.md；生成时补真实论文或来源
Input: 项目路径与已确认的研究设定；不读取DTA
Output: 公共宏和样本ID助手；不生成DTA
==================================================*/

**# 00 文件用途与运行说明
/* 01_统一设置.do：公共路径、参数和助手；不加载数据、不重置种子。 */
* 本模板的frame样本助手需要Stata16或以上；STATA_VERSION也须填写至少16。
if c(stata_version)<16 | real("{{STATA_VERSION}}")<16 {
    display as error "frame样本助手需要Stata16或以上。"
    exit 9
}
version {{STATA_VERSION}}
set more off
set varabbrev off
**# 01 公共路径与年份
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
* TASK_CATEGORY填七类中的真实名称；TASK_NAME_DATE填YYYYMMDD_主题（重名时YYYYMMDD_HHMMSS_主题），指原测试证据包；继续、采用或获授权重跑不换包名，不创建根logs；既有日志先留可恢复记录。
* 仅准备本次计算实际写入的中间数据和日志位置，复用原任务包。
* TASK_DATA_PATH若含更深层，生成时先核实该数据任务父目录；不逐轮新建日期包。
capture mkdir "$DATA"
capture mkdir "$DATA/temp"
capture mkdir "$TEMP"
capture mkdir "$ROOT/测试"
capture mkdir "$ROOT/测试/{{TASK_CATEGORY}}"
capture mkdir "$LOGROOT"
* 获授权导表/绘图时由相应输出段准备TABLE/FIGURE；不因加载设置预建RAW/FINAL/RESULT。

**# 02 统一变量与回归设置
global X {{CONTROLS_LIST}}
global PANEL "$ROOT/{{PANEL_RELATIVE_PATH}}"
global ENTITY "{{ENTITY_VAR}}"
global TIME "{{TIME_VAR}}"
global ABSORB "{{FE_VARS}}"
global CLUSTER "{{CLUSTER_VAR}}"
global HDFE "{{HDFE_OPTIONS}}"
global COEFLABELS {{COEF_LABELS}}
global SAMPLE_IDS "{{SAMPLE_ID_VARS}}"

**# 03 真实样本ID助手
* 普通e(sample)模型的公共助手；特殊估计器按真实接口另行配置。
capture program drop save_sample_ids
program define save_sample_ids
    syntax, Model(name)
    tempname sample_frame
    frame put $SAMPLE_IDS if e(sample), into(`sample_frame')
    frame `sample_frame': isid $SAMPLE_IDS
    frame `sample_frame': save "$TEMP/`model'_sample_ids.dta", replace
    frame drop `sample_frame'
end

{{SHARED_SETUP_CODE}}
