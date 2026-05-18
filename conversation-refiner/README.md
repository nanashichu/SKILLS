# Conversation Refiner

定期整理 Claude Code 历史对话，提炼结构化笔记写入 Obsidian 知识库。

## 工作原理

**首次运行**：全量分析所有历史对话（`C:\Users\<用户名>\.claude\projects\` 下全部 JSONL 文件），提炼笔记写入 Obsidian。

**后续运行**：读取上次提炼日期，只处理新增对话，增量追加笔记。

## 三步流水线

1. **增量分析** — 调用 Python 脚本解析 JSONL 对话文件，生成图表和分析报告
2. **逐日精读** — 按日期分组读取对话，提炼结构化笔记，按主题分类写入 Obsidian
3. **更新索引** — 在 Obsidian 知识库索引中添加新笔记条目

## 提炼原则

1. **去过程留结果** — 不记录调试步骤，只记录最终结论
2. **去重复留精华** — 反复调试压缩为最终方案
3. **保留决策逻辑** — 记录为什么这么做，不只记做了什么
4. **保留个人反思** — 踩坑感悟、工作节奏反思
5. **研究内容脱敏** — 不暴露具体研究话题，用模糊说法替代

## 笔记分类

| 内容类型 | 目标文件夹 |
|---------|-----------|
| 实证研究方法论/决策 | `实证研究/` |
| 数据处理踩坑 | `数据资源/` |
| Claude Code 工具链 / vibe-coding | `工具资源/` |
| 个人反思/工作节奏 | `生活杂记/` |

## 触发词

- "整理对话"
- "提炼笔记"
- "对话复盘"
- "历史对话分析"

## 文件结构

```
conversation-refiner/
├── SKILL.md                    # 主流程定义
├── README.md                   # 本文件
└── references/
    └── extraction-rules.md     # 提炼规则详细说明
```

## 安装

将整个 `conversation-refiner/` 文件夹复制到 Claude Code 的 skills 目录：

```bash
# Windows
cp -r conversation-refiner "C:\Users\<用户名>\.claude\skills\"

# macOS/Linux
cp -r conversation-refiner ~/.claude/skills/
```

## 依赖

- Claude Code（CLI 或 IDE 扩展）
- Python 3.x + matplotlib + numpy（用于分析脚本）
- Obsidian 知识库（笔记写入目标）
