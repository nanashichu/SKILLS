/*==================================================
project: {{ROOT_PATH}}（生成时填写项目名称）
Author: 未记录（生成时填已确认作者）
E-email: 未记录（生成时填已确认邮箱）
Creation Date: {{DATE}}
Modification Date: {{DATE}}（生成后修改时更新）
Do-file version: v01（生成时按项目核定）
References: 项目README.md、CLAUDE.md；生成时补真实论文或来源
Input: 配置的各独立do及其输入
Output: 各子do实际生成的日志、数据、表与图
==================================================*/

**# 00 文件用途与运行说明
/* 主程序只按配置顺序调用；每个do本身也可独立运行。 */
do "{{ROOT_PATH}}/do/01_统一设置.do"
capture log close master
* 同一任务保留每次原生日志，使用未占用的运行编号；不新建运行目录。
local log_run = 1
local log_file "$LOGROOT/主程序_run`log_run'.log"
capture confirm file "`log_file'"
while _rc == 0 {
    local ++log_run
    local log_file "$LOGROOT/主程序_run`log_run'.log"
    capture confirm file "`log_file'"
}
log using "`log_file'", name(master) text

**# 01 按顺序调用各do
* 按需00构建，再02变量定义、03描述性统计和后续逐表do。
{{SELECTED_DO_BLOCKS}}

log close master
