# Conversation Refiner — 历史对话整理与笔记提炼

定期整理 Claude Code 历史对话，提炼结构化笔记写入 Obsidian 知识库。

触发词："整理对话"、"提炼笔记"、"对话复盘"、"历史对话分析"、"conversation-refiner"

不适用于：非对话整理类任务、实时对话中的问题。

---

## 核心流程

三步流水线，每步依赖上一步的产出。

### Step 1: 增量分析

调用现有 Python 分析脚本，生成图表和分析报告。

**执行命令**：
```bash
cd "G:/【20260426】claude总文件夹" && /c/Users/29774/AppData/Local/Programs/Python/Python313/python.exe analyze_main.py
```

**产出**：
- 15 张 PNG 图表 → `G:\【20260401】paperread\历史对话\分析\charts\`
- CSV 数据文件 → `G:\【20260401】paperread\历史对话\分析\data\`
- 分析报告 → `G:\【20260401】paperread\历史对话\分析\分析报告.md`

**增量逻辑**：
- 首次运行：分析全部 JSONL 对话文件
- 后续运行：对比 `data/` 下已有 CSV 的时间范围，只处理新增日期的对话
- 如果 `analyze_main.py` 报错，检查 Python 路径和依赖（matplotlib, numpy）

**失败降级**：脚本无法运行时，Agent 直接用 Bash 读取 JSONL 文件，手动统计消息数量和日期范围。

---

### Step 2: 逐日精读提炼

扫描 JSONL 对话文件，按日期分组读取，提炼结构化笔记。

**2.1 确定日期范围**：

```python
# 扫描 C:/Users/29774/.claude/projects/ 下所有 JSONL 文件
# 按修改时间确定最新对话日期
# 与上次提炼记录对比，确定增量日期范围
```

上次提炼记录保存在 `G:\【20260401】paperread\历史对话\最后提炼日期.txt`（首次运行时创建）。

**2.2 逐日读取对话**：

对每个新增日期：
1. 扫描 `C:/Users/29774/.claude/projects/` 下所有子目录的 `*.jsonl`
2. 筛选修改时间（mtime）为目标日期的文件
3. 解析每条记录：`type=="user"` 的消息，提取 timestamp 和 message
4. message 可能是 string 或 dict（dict 中取 content，content 可能是 list 需遍历 `type=="text"` 的项）
5. 按时间排序，提取用户做了什么工作

**2.3 提炼笔记**：

按 `references/extraction-rules.md` 的规则提炼。核心原则：

- 去过程留结果：不记录「ls了什么目录」，只记录「发现了什么结论」
- 去重复留精华：同一问题反复调试压缩为最终方案
- 保留决策逻辑：为什么选这个控制变量，为什么固定这个效应
- 保留个人反思：用户的自我反思、踩坑感悟、工作节奏反思
- **不暴露研究内容**：不写具体研究话题名称，用模糊说法（如「某实证项目的变量构建方法」而非「数智化转型与股价崩盘风险的VaR计算」）

**2.4 分类写入**：

| 内容类型 | 目标文件夹 | 文件命名 | 模式 |
|---------|-----------|---------|------|
| 实证研究方法论/决策 | `实证研究/` | `YYYYMMDD_主题_对话提炼.md` | 新建 |
| 数据处理踩坑 | `数据资源/` | `YYYYMMDD_数据处理经验与踩坑.md` | 追加（如已有同名文件） |
| Claude Code 工具链 | `工具资源/` | `YYYYMMDD_Claude_Code工具链经验_对话提炼.md` | 追加 |
| 个人反思/工作节奏 | `生活杂记/` | `YYYYMMDD_AI协作与个人反思_对话提炼.md` | 追加 |
| vibe-coding/工具建设 | `工具资源/` | 合并到 Claude Code 工具链文件 | 追加 |

**追加规则**：如果目标日期的文件已存在，Read 后用 Edit 追加新内容，不覆盖。如果不存在，用 Write 新建。

**笔记格式**：
```markdown
# 主题 — 从对话中提炼

> 从历史对话（YYYY-MM-DD ~ YYYY-MM-DD）提炼

## 子主题

- 具体结论/决策/踩坑
- 保留决策理由

## 个人反思（如有）

> 引用原话 — 日期

反思内容
```

**2.5 更新提炼记录**：

写入 `G:\【20260401】paperread\历史对话\最后提炼日期.txt`，内容为本次提炼的最新日期（YYYY-MM-DD）。

---

### Step 3: 更新索引

更新 Obsidian 知识库索引文件。

**3.1 读取当前索引**：
```
Read: G:\【20260401】paperread\index.md
```

**3.2 添加新条目**：

在对应分类下添加新笔记的双链条目，格式：
```
- [[YYYYMMDD_主题_对话提炼]] — 一句话描述
```

**3.3 更新计数**：

更新顶部统计表中对应分类的数量和合计。

**3.4 更新最后更新日期**：

修改 `**最后更新**: YYYY-MM-DD` 行。

---

## 定期执行

用户可以设置定期任务自动触发：

```
"每周日整理对话" → 用 CronCreate 设置每周日触发
"每天下班前提炼笔记" → 用 CronCreate 设置工作日下班时间触发
```

CronCreate prompt 示例：
```
调用 conversation-refiner skill，整理历史对话并提炼笔记进 Obsidian
```

---

## 文件路径速查

| 用途 | 路径 |
|------|------|
| 分析脚本 | `G:\【20260426】claude总文件夹\analyze_main.py` |
| JSONL 对话源 | `C:\Users\29774\.claude\projects\` |
| 分析产出 | `G:\【20260401】paperread\历史对话\分析\` |
| Obsidian 知识库 | `G:\【20260401】paperread\` |
| 提炼记录 | `G:\【20260401】paperread\历史对话\最后提炼日期.txt` |
| 知识库索引 | `G:\【20260401】paperread\index.md` |
| Python 路径 | `/c/Users/29774/AppData/Local/Programs/Python/Python313/python.exe` |

---

## 注意事项

- **研究内容脱敏**：笔记中不写具体研究话题名称，用「某实证项目」「某研究」等模糊说法。vibe-coding/工具建设内容可以写具体
- **增量处理**：每次只处理上次提炼之后的新对话，不重复处理
- **追加不覆盖**：已有笔记文件用 Edit 追加，不用 Write 覆盖
- **index.md 用 Edit**：更新索引时用 Edit 增量修改，不用 Write 覆盖整个文件