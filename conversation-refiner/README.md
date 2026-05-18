# Conversation Refiner

定期整理 Claude Code 历史对话，提炼结构化笔记写入 Obsidian 知识库。

## 功能

- 增量分析历史对话（Python 脚本生成图表 + 分析报告）
- 逐日精读提炼笔记（去过程留结果、保留决策逻辑、保留个人反思）
- 按主题分类写入 Obsidian（实证研究 / 数据资源 / 工具资源 / 生活杂记）
- 自动更新知识库索引

## 触发词

- "整理对话"
- "提炼笔记"
- "对话复盘"
- "历史对话分析"

## 文件结构

```
conversation-refiner/
├── SKILL.md              # 主流程定义
├── README.md             # 本文件
└── references/
    └── extraction-rules.md   # 提炼规则详细说明
```

## 安装

将整个 `conversation-refiner/` 文件夹复制到 Claude Code 的 skills 目录：

```bash
# Windows
cp -r conversation-refiner "C:\Users\<用户名>\.claude\skills\"

# macOS/Linux
cp -r conversation-refiner ~/.claude/skills/
```

## 核心原则

1. **去过程留结果** — 不记录调试步骤，只记录最终结论
2. **去重复留精华** — 反复调试压缩为最终方案
3. **保留决策逻辑** — 记录为什么这么做，不只记做了什么
4. **保留个人反思** — 踩坑感悟、工作节奏反思
5. **研究内容脱敏** — 不暴露具体研究话题，用模糊说法替代
