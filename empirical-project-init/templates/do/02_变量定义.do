/*==================================================
project: {{ROOT_PATH}}（生成时填写项目名称）
Author: 未记录（生成时填已确认作者）
E-email: 未记录（生成时填已确认邮箱）
Creation Date: {{DATE}}
Modification Date: {{DATE}}（生成后修改时更新）
Do-file version: v01（生成时按项目核定）
References: 项目README.md、CLAUDE.md；生成时补真实论文或来源
Input: $PANEL及已确认的变量来源
Output: $TABLE/变量定义表；必要的字典底表进$TEMP
==================================================*/

**# 00 文件用途与运行说明
/* 02_变量定义.do；对应论文表{{TABLE_ID}}，定义/来源按实际稿件配置。 */
do "{{ROOT_PATH}}/do/01_统一设置.do"
capture log close vardef
* 同一任务保留每次原生日志，使用未占用的运行编号；不新建运行目录。
local log_run = 1
local log_file "$LOGROOT/{{DO_STEM}}_run`log_run'.log"
capture confirm file "`log_file'"
while _rc == 0 {
    local ++log_run
    local log_file "$LOGROOT/{{DO_STEM}}_run`log_run'.log"
    capture confirm file "`log_file'"
}
log using "`log_file'", name(vardef) text
use "$PANEL", clear

describe {{DEP_VAR_LIST}} {{INDEP_VAR}} $X
**# 01 变量定义的来源或计算
* 如需计算表：中间字典写TEMP、最终RTF写TABLE。
* 若为人工文字表，登记人工来源，不伪造计算链路。
{{VARIABLE_DEFINITION_CODE_BLOCKS}}

log close vardef
