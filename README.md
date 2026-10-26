# Claude Code Skills

我自己创建的 Claude Code Skills 集合。

## Skills

| Skill | 说明 | 触发词 |
|-------|------|--------|
| [daily-todo-manager](daily-todo-manager/) | 个人日周月待办任务管理系统：打卡/项目管理/任务追踪/每日总结/跨对话搜索/风险预警/周报生成 | "早上好"、"结束工作"、"检查风险" |
| [conversation-refiner](conversation-refiner/) | 历史对话整理与笔记提炼，增量分析→逐日精读→写入Obsidian | "整理对话"、"提炼笔记"、"对话复盘" |
| [empirical-research](empirical-research/) | 实证研究计算与结果：Python估计并全量保存，先在对话总结显著组合与下一步；明确要求才导出Word；研究版本确认后才用Stata核对最终do | "跑回归"、"机制/异质性/稳健性"、"导出结果表" |
| [empirical-playbook](empirical-playbook/) | 实证顶刊做法库与不显著诊断：检索中英文经济/金融/会计顶刊六部分做法并入库；结果不显著时按诊断树排查，列出可借鉴做法、出处与风险等级；只读，不改代码不跑回归 | "不显著怎么办"、"顶刊怎么做"、"更新方法库" |
| [empirical-project-init](empirical-project-init/) | 实证项目初始化与文件管理：唯一现用入口、data/raw temp final、主do、测试分类包、两张现用清单、归档验收与安全清理 | "初始化实证项目"、"整理项目文件"、"归档验收" |
| [stata-do-my-style](stata-do-my-style/) | 按我的写法写 Stata do：一个主 do 从原始数据导入、清洗、合并写到回归，`**#` 书签分节、中文注释，不写 program 助手和冗长说明头 | "写do"、"整理do文件"、"最终do" |

## 安装

将 skill 文件夹复制到 Claude Code 的 skills 目录下：

```bash
# Windows
cp -r <skill-name> "%USERPROFILE%\.claude\skills\"

# macOS/Linux
cp -r <skill-name> ~/.claude/skills/
```

## 约定

- 每个 skill 一个文件夹，包含 `SKILL.md`（必须）和 `references/`（可选）
- `SKILL.md` 定义触发词、流程、文件路径
- `references/` 放详细规则、模板等参考文件
