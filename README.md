# Claude Code Skills

我自己创建的 Claude Code Skills 集合。

## Skills

| Skill | 说明 | 触发词 |
|-------|------|--------|
| [daily-todo-manager](./) | 个人日周月待办任务管理系统，13项核心功能：打卡/项目管理/任务追踪/每日总结+跨对话搜索/风险预警+Guard/周报生成 | "早上好"、"开始工作"、"结束工作"、"更新日志"、"生成周报"、"检查风险" |
| [conversation-refiner](conversation-refiner/) | 历史对话整理与笔记提炼，增量分析→逐日精读→写入Obsidian | "整理对话"、"提炼笔记"、"对话复盘" |

---

## daily-todo-manager

个人日周月待办任务管理系统 — 为 Claude Code 设计的 AI 原生任务管理 Skill。

### 核心理念

任务管理应该零摩擦。你不需要切换到另一个 app，不需要手动填表——和 AI 说话的同时，任务管理就完成了。

### 13 项核心功能

| # | 功能 | 触发方式 |
|---|------|---------|
| §0 | 打卡记录 | "上班"/"下班"/"暂停"/"继续" |
| §1 | 未来事件 | "X月X日要XXX" |
| §2 | 创建项目 | "项目：[名称]" |
| §3 | 添加任务 | "添加任务" |
| §4 | 开始任务+时间预测 | "现在开始 [任务]" |
| §5 | 完成任务 | "完成了" |
| §6 | 临时任务 | "临时任务" |
| §7 | 今日待办 | "早上好"/"开始工作" |
| §8 | 自动感悟 | "结束工作"时自动触发 |
| §9 | 经验总结 | "结束工作"时自动触发 |
| §10 | 每日总结+跨对话搜索 | "结束工作"/"更新日志" |
| §11 | 风险预警+Guard | 自动+"检查风险" |
| §12 | 周报生成 | "生成周报"/周日自动 |

### 快速开始

**前提条件**：Claude Code + Python 3.8+

```bash
# 1. 克隆仓库
git clone https://github.com/nanashichu/SKILLS.git

# 2. 设置环境变量（在 Claude Code settings.json 中）
# "env": { "TODO_DIR": "/your/path/to/todos" }

# 3. 初始化数据目录
python scripts/init_todo_dir.py

# 4. 在 Claude Code 中说：早上好
```

### 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| `TODO_DIR` | ✅ | 任务数据存储目录 |
| `CLAUDE_TRANSCRIPT_DIR` | 可选 | 对话记录目录，用于跨对话搜索（默认 `~/.claude/projects/`） |

### 设计亮点

- **AI 原生**：自然语言交互，不学命令、不记快捷键
- **零摩擦**：写代码时顺带打卡、完成任务，不打断心流
- **跨对话搜索**：多个并行 Claude Code 会话自动汇总
- **缓存驱动**：生成今日待办只需读 2 个文件
- **Git 友好**：所有数据都是 Markdown，可版本管理
- **平台无关**：纯文本+Python，Windows/macOS/Linux 通用

### 文件结构

```
daily-todo-manager (根目录)
├── SKILL.md              # Skill 主文件
├── references/           # 参考文档（功能/格式/智能模块/陷阱）
├── scripts/              # Python 辅助脚本
│   ├── init_todo_dir.py           # 初始化数据目录
│   ├── scan_projects.py           # 扫描项目并重建缓存
│   └── search_recent_sessions.py  # 跨对话搜索
└── evals/evals.json      # 测试用例
```

详细文档见 [references/](references/) 目录。

---

## conversation-refiner

历史对话整理与笔记提炼 Skill。详见 [conversation-refiner/README.md](conversation-refiner/README.md)。

---

## 安装

将 skill 文件夹复制到 Claude Code 的 skills 目录下：

```bash
# Windows
cp -r <skill-name> "%USERPROFILE%\.claude\skills\"

# macOS/Linux
cp -r <skill-name> ~/.claude/skills/
```

---

## 约定

- 每个 skill 包含 `SKILL.md`（必须）和 `references/`（可选）
- `SKILL.md` 定义触发词、流程、文件路径
- `references/` 放详细规则、模板等参考文件
- root 级别的文件属于 daily-todo-manager，其他 skill 放在各自子目录下
