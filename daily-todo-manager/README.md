# daily-todo-manager

> 个人日周月待办任务管理系统 — 为 Claude Code 设计的 AI 原生任务管理 Skill

`daily-todo-manager` 是一个运行在 Claude Code 中的任务管理 Skill，通过自然语言交互管理你的每日待办、项目进度、打卡记录和工作总结。它不是传统的独立应用，而是直接嵌入你的 AI 编程助手，让你在写代码、做研究的同时，无缝记录和管理工作。

**核心理念**：任务管理应该零摩擦。你不需要切换到另一个 app，不需要手动填表——和 AI 说话的同时，任务管理就完成了。

---

## 目录

- [核心特性](#核心特性)
- [系统架构](#系统架构)
- [快速开始](#快速开始)
- [环境配置](#环境配置)
- [目录结构](#目录结构)
- [功能详解](#功能详解)
  - [§0 打卡记录](#0-打卡记录)
  - [§1 未来事件](#1-未来事件)
  - [§2-3 项目管理](#2-3-项目管理)
  - [§4-5 任务追踪](#4-5-任务追踪)
  - [§7 每日待办](#7-每日待办)
  - [§10 每日总结 + 跨对话搜索](#10-每日总结--跨对话搜索)
  - [§11 风险预警 + Guard](#11-风险预警--guard)
  - [§12 周报生成](#12-周报生成)
- [文件格式规范](#文件格式规范)
- [脚本说明](#脚本说明)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 核心特性

### 13 项核心功能

| # | 功能 | 触发方式 | 说明 |
|---|------|---------|------|
| §0 | 打卡记录 | "上班"/"下班"/"暂停"/"继续" | 按上午/下午/晚上分时段记录，自动计算有效时长，防重复写入 |
| §1 | 未来事件 | "X月X日要XXX" | 快速在指定日期创建待办事项 |
| §2 | 创建项目 | "项目：[名称]" | 在 projects/ 下创建项目文件，支持元数据（截止/优先级/状态） |
| §3 | 添加任务 | "添加任务" | 向项目追加新任务，自动更新缓存 |
| §4 | 开始任务 | "现在开始 [任务]" | 记录开始时间，基于历史数据预测用时和置信区间 |
| §5 | 完成任务 | "完成了" | 自动计算用时、更新时间线、更新项目进度、记录历史 |
| §6 | 临时任务 | "临时任务" | 管理不成项目的零散任务，活跃/历史自动拆分 |
| §7 | 今日待办 | "早上好"/"开始工作" | 生成今日任务概览，自动检查风险，输出激励内容 |
| §8 | 自动感悟 | "结束工作"时自动触发 | 从对话中提取非工作内容，分类生成生活感悟 |
| §9 | 经验总结 | "结束工作"时自动触发 | 从已完成任务提炼经验教训，按类别+标记体系展示 |
| §10 | 每日总结 | "结束工作"/"更新日志" | 跨对话搜索所有会话→时间统计→双向同步daily和projects |
| §11 | 风险预警 | 自动+手动 | 截止风险/效率风险/习惯中断/缓存过期，多级预警 |
| §12 | 周报生成 | "生成周报"/周日自动 | 汇总本周所有项目的daily和projects变化 |

### 设计亮点

- **AI 原生**：所有交互通过自然语言，不需要学命令、记快捷键
- **零摩擦**：写代码时顺带就能打卡、完成任务，不打断心流
- **跨对话搜索**：多个并行 Claude Code 会话的工作自动汇总，不遗漏
- **缓存驱动**：生成今日待办只需读 2 个文件，不会逐个扫描项目
- **数据积累**：任务用时、时段效率、习惯数据随时间沉淀，越用越智能
- **Git 友好**：所有数据都是 Markdown 文本文件，可以纳入版本管理
- **平台无关**：纯文本+Python 脚本，Windows/macOS/Linux 都能用

---

## 系统架构

```
┌─────────────────────────────────────────────┐
│              用户 (自然语言)                  │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│           Claude Code Agent                  │
│  ┌───────────────────────────────────────┐  │
│  │        SKILL.md (Skill 主逻辑)         │  │
│  │  触发词匹配 → 读取文件 → 增量编辑     │  │
│  │  → 同步缓存 → 输出结果                │  │
│  └───────────────────────────────────────┘  │
└────────┬────────────────────┬───────────────┘
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌──────────────────────┐
│  $TODO_DIR      │  │  scripts/             │
│                 │  │                       │
│  daily/         │  │  scan_projects.py     │
│    YYYY-MM-DD   │  │    → 重建缓存         │
│  projects/      │  │                       │
│    项目名.md    │  │  search_recent_       │
│  memory/        │  │   sessions.py         │
│    cache.json   │  │    → 跨对话搜索       │
│  weekly/        │  │                       │
│  reviews/       │  │  init_todo_dir.py     │
│  config.md      │  │    → 初始化目录       │
└─────────────────┘  └──────────────────────┘
```

---

## 快速开始

### 前提条件

- 已安装 [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview)
- Python 3.8+（用于运行辅助脚本）

### 安装

```bash
# 1. 克隆仓库
git clone https://github.com/nanashichu/SKILLS.git

# 2. 复制到 Claude Code skills 目录
# Windows
cp -r SKILLS/daily-todo-manager "%USERPROFILE%\.claude\skills\daily-todo-manager\"

# macOS/Linux
cp -r SKILLS/daily-todo-manager ~/.claude/skills/daily-todo-manager/
```

### 初始化

```bash
# 1. 设置环境变量（在 Claude Code settings.json 中）
# "env": { "TODO_DIR": "/your/path/to/todos" }

# 2. 创建数据目录结构
export TODO_DIR="/your/path/to/todos"
python scripts/init_todo_dir.py

# 3. （可选）设置跨对话搜索路径
# "env": { "CLAUDE_TRANSCRIPT_DIR": "/home/user/.claude/projects" }
```

### 第一次使用

在 Claude Code 中说：

```
早上好
```

系统会自动：
1. 检查缓存是否过期
2. 生成今日待办模板
3. 显示可用的功能指令
4. 检查风险预警

---

## 环境配置

### 环境变量

在 Claude Code 的 `settings.json` 中配置：

```json
{
  "env": {
    "TODO_DIR": "G:/你的路径/每日待办/",
    "CLAUDE_TRANSCRIPT_DIR": "C:/Users/你的用户名/.claude/projects/"
  }
}
```

| 变量 | 必需 | 说明 |
|------|------|------|
| `TODO_DIR` | ✅ | 任务数据存储目录 |
| `CLAUDE_TRANSCRIPT_DIR` | 可选 | Claude Code 对话记录目录，用于跨对话搜索。不设置则默认使用 `~/.claude/projects/` |
| `PYTHON_BIN` | 可选 | Python 可执行文件路径，默认 `python3` |

### 配置文件

首次运行 `init_todo_dir.py` 后，会在 `$TODO_DIR` 下生成 `config.md`，可以自定义：

- **固定任务**：每日自动提醒的习惯任务（如"读论文30分钟"）
- **任务类型关键词**：用于时间预测中的任务分类
- **风险阈值**：紧急天数、停滞天数、低效天数的自定义值

---

## 目录结构

### Skill 文件

```
daily-todo-manager/
├── SKILL.md                  # Skill 主文件（Claude Code 加载入口）
├── README.md                 # 本文档
├── LICENSE                   # MIT 许可证
├── references/               # 参考文档
│   ├── features.md           # 13项功能详细实现说明
│   ├── file-formats.md       # 所有文件格式模板
│   ├── intelligence.md       # 智能模块（搜索/缓存/预测/预警）
│   └── pitfalls.md           # 常见错误与预防检查清单
├── scripts/                  # Python 辅助脚本
│   ├── init_todo_dir.py      # 初始化数据目录
│   ├── scan_projects.py      # 扫描项目并重建缓存
│   └── search_recent_sessions.py  # 跨对话搜索用户消息
└── evals/
    └── evals.json            # 评估测试用例（13个）
```

### 数据文件（$TODO_DIR，由 init_todo_dir.py 创建）

```
$TODO_DIR/
├── config.md                 # 系统配置
├── CLAUDE.md                 # Agent 操作规则（可选）
├── daily/                    # 每日日志
│   └── YYYY-MM-DD.md
├── weekly/                   # 周报存档
├── projects/                 # 项目文件
│   ├── YYYY-MM-DD-项目名.md
│   └── 临时任务.md
├── reviews/                  # 复盘记录
└── memory/                   # 运行时数据
    ├── project-tasks-cache.json  # 项目任务缓存
    ├── task-time-history.json    # 任务用时历史
    ├── session-context.json      # 会话上下文
    └── guard-config.json         # Guard 配置
```

---

## 功能详解

### §0 打卡记录

**触发词**：`上班` / `下班` / `暂停` / `继续`

按上午/下午/晚上三个时段记录打卡时间，自动计算有效时长（扣除暂停时间）。

```
## 🕰️ 打卡记录

### 上午
- 上班：09:00
- 下班：12:00
- 暂停：10:30-10:45（15分钟）
- 有效时长：2小时45分钟

**今日总工作时长**：X小时X分钟
```

**防重复机制**：写入前检查已有时段区块，同时段更新、不同时段追加，杜绝重复。

### §1 未来事件

**触发词**：`X月X日要XXX`

快速在指定日期创建待办事项。系统自动解析日期（默认当年），如果该日期的 daily 文件不存在则自动创建。

### §2-3 项目管理

**创建项目**：`项目：博士大论文 截止日期：2026-12-31 优先级：高`

在 `projects/` 下创建项目文件，自动填充元数据模板。

**添加任务**：`添加任务 写文献综述 到 博士大论文`

向项目任务列表追加新任务，同时更新缓存。

项目文件支持声明**子项目**关系（在元数据中加 `**子项目**：子项目1, 子项目2`），扫描时自动关联。

### §4-5 任务追踪

**开始任务**：`现在开始 跑基准回归`

1. 记录到 `session-context.json`
2. 从 `task-time-history.json` 读取同类任务历史用时
3. 输出时间预测：`预计用时：1.5小时（80%置信区间：1.2-2.0小时）`

**完成任务**：`完成了`

1. 计算实际用时
2. 写入每日时间线和已完成列表
3. 更新项目文件的任务状态、进度、项目日志
4. 写入 `task-time-history.json` 供将来预测使用

### §7 每日待办

**触发词**：`早上好` / `开始工作` / `开工`

输出示例：

```
🌅 早上好！今天是 2026年05月25日 周一

📋 今日待办提醒

⚠️ 紧急任务（3天内）：
- [博士大论文] - 修改第四章（截止：05-27，还剩2天）

📌 今日重点：
- [第二篇实证] - 跑主回归
- [公众号] - 写AI工作流文章

✅ 已完成：0 个
⏳ 待办：5 个

💡 今日可用功能
• "上班/下班" — 打卡记录
• "现在开始 [任务]" — 开始任务+时间预测
• "完成了" — 完成任务
• "结束工作" — 生成今日总结
```

### §10 每日总结 + 跨对话搜索

**触发词**：`结束工作` / `更新日志`

这是系统最核心的功能。执行流程：

1. **跨对话搜索**：运行 `search_recent_sessions.py` 扫描所有 Claude Code 会话的 JSONL 文件，提取今日用户消息
2. **去重合并**：与当前已有时间线合并，不重复添加
3. **双向同步**：工作内容同时写入 daily 和 projects
4. **自动触发 §8+§9**：生成生活感悟和经验教训

**为什么必须跑跨对话搜索？** Claude Code 可以同时开多个窗口/会话。如果只凭当前会话判断，必然会遗漏并行会话中的工作。脚本是唯一可靠的数据源。

### §11 风险预警 + Guard

四级预警体系：

| 级别 | 条件 | 标识 |
|------|------|------|
| 极紧急 | 截止日期 = 今天 | 🚨 |
| 紧急 | 截止 ≤ 1天 | ⚠️ |
| 提醒 | 截止 ≤ 3天 | 📌 |
| 逾期 | 截止 < 今天 | 🔴 |

Guard 系统（可在 `memory/guard-config.json` 中配置）：

- **no_overdue (Critical)**：检查逾期任务
- **efficiency_floor (Warning)**：连续低效天数超阈值警告
- **habit_continuity (Warning)**：习惯任务中断提醒

### §12 周报生成

**自动触发**：每周日 21:00  |  **手动触发**：`生成周报`

自动汇总本周所有 daily/*.md 和 projects/*.md 的变化，生成结构化周报。

---

## 文件格式规范

### 每日日志区块顺序（严格固定）

```
1. 🕰️ 打卡记录
2. 🕐 时间线记录
3. 📝 经验教训（AI生成）
4. 💭 今日感悟（AI提取）
5. 📋 今日待办
6. ✅ 今日已完成
7. 📋 明日待办
8. 📓 今日日记（用户手写，AI不碰）
```

### 日志详细程度标准（五要素）

每条日志必须包含：**目的 + 对象 + 操作 + 数据/文件 + 结果**

```
✅ 正确：
15:00-16:00 [第二篇实证] - 论文§5.2 H2（数智化→缓解融资约束→降低尾部风险）。
回归：基准DiD基础上加入SA×Digital×Post三重交互项。
数据：3src_mech.dta。代码：05_机制检验.do §3.3。
结果：SA×Digital×Post系数=-0.032, t=-2.15, 5%显著，支持融资约束渠道。

❌ 错误：
跑机制检验  ← 缺假设/设定/结果
```

完整格式规范见 [references/file-formats.md](references/file-formats.md)。

---

## 脚本说明

### `init_todo_dir.py` — 初始化数据目录

```bash
python scripts/init_todo_dir.py                      # 使用 $TODO_DIR
python scripts/init_todo_dir.py --todo-dir ~/mytodos # 指定目录
```

创建目录结构、默认配置文件、Guard 配置、临时任务文件。

### `scan_projects.py` — 重建项目缓存

```bash
python scripts/scan_projects.py
```

扫描 `projects/*.md` 所有文件，提取元数据、进度、未完成任务，写入 `memory/project-tasks-cache.json`。Agent 生成今日待办时只读这个缓存，不逐个扫描项目文件。

### `search_recent_sessions.py` — 跨对话搜索

```bash
python scripts/search_recent_sessions.py --days 7                    # 最近7天
python scripts/search_recent_sessions.py --today                     # 只搜今天
python scripts/search_recent_sessions.py --from 2026-05-20 --to 2026-05-25
python scripts/search_recent_sessions.py --days 7 --transcript-dir /custom/path
```

扫描 `$CLAUDE_TRANSCRIPT_DIR` 下所有 JSONL 文件，提取用户消息，按日期分组，自动检测项目关联。

---

## 常见问题

### Q: 和 Todoist / Notion / 飞书任务有什么区别？

daily-todo-manager 不是独立应用，它嵌入在你的 AI 工作流中。你在和 Claude Code 讨论代码时，顺带说一句"完成了"，任务就标记完成，时间线就记录好了。**零额外操作成本**。

### Q: 数据安全吗？会不会丢失？

所有数据都是本地 Markdown 文件。建议将 `$TODO_DIR` 纳入 Git 版本管理或云同步（OneDrive/iCloud）。

### Q: 跨对话搜索是怎么工作的？

Claude Code 把所有对话记录成 JSONL 文件。`search_recent_sessions.py` 扫描这些文件，提取用户消息，按日期和关键词归类。"结束工作"时自动汇总所有会话。

### Q: 支持哪些平台？

Windows / macOS / Linux 都支持。Skill 本身是纯文本（Markdown），辅助脚本是 Python 3.8+。

---

## 贡献指南

欢迎提交 Issue 和 PR。

### 贡献方向

- 🐛 **Bug 修复**：日志格式错误、跨对话搜索遗漏等
- ✨ **新功能**：新的 Guard 规则、报告格式、数据可视化
- 📝 **文档改进**：补充使用场景、添加多语言支持
- 🔧 **平台适配**：改进跨平台兼容性

### 开发规范

- Skill 逻辑在 `SKILL.md` 中，遵循 Claude Code Skill 规范
- Python 脚本保持单文件、无外部依赖（标准库 only）
- 新增功能先在 `references/` 中补充文档，再修改 SKILL.md
- 测试用例在 `evals/evals.json` 中添加

---

## 许可证

[MIT License](LICENSE)

---

**版本**：v6.3
**最后更新**：2026-05-25
