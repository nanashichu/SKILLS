# Claude Code Skills

我自己创建的 Claude Code Skills 集合。

## Skills

| Skill | 说明 | 触发词 |
|-------|------|--------|
| [conversation-refiner](conversation-refiner/) | 历史对话整理与笔记提炼，增量分析→逐日精读→写入Obsidian | "整理对话"、"提炼笔记"、"对话复盘" |

## 安装

将 skill 文件夹复制到 Claude Code 的 skills 目录下即可：

```bash
# Windows
cp -r <skill-name> "C:\Users\<用户名>\.claude\skills\"

# macOS/Linux
cp -r <skill-name> ~/.claude/skills/
```

## 约定

- 每个 skill 一个文件夹，包含 `SKILL.md`（必须）和 `references/`（可选）
- `SKILL.md` 定义触发词、流程、文件路径
- `references/` 放详细规则、模板等参考文件