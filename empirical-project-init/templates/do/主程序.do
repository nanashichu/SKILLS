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
* 用01中的next_log取未占用的运行编号日志；同名日志若因上次中断仍开着，先手动 log close master
next_log, stem(主程序)
log using "`r(file)'", name(master) text

**# 01 按顺序调用各do
* 按需00构建，再02变量定义、03描述性统计和后续逐表do。
{{SELECTED_DO_BLOCKS}}

log close master
