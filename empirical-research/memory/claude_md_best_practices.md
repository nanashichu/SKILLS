**目录日期统一在前（2026-10-10用户约定）。** 任务、采用项、结果版本和归档目录用`YYYYMMDD_主题`，例如`测试/机制/20261010_VC新口径`、`data/temp/20261010_VC获投企业家数_采用`；同日独立任务重名时用`YYYYMMDD_HHMMSS_主题`。日期取任务实际开始日，继续原尝试沿用原日期，不能以整理日替代历史任务日期；没有可靠日期时先查日志/来源，仍不明则标为待确认，不编造日期。data、raw、temp、final、do、code、result、table、figure、测试、归档、初稿等固定用途目录及数据/程序等包内分类保持用途名称，不强加日期。文件名继续遵循各自规则，现用代码仍按两位序号开头。旧目录改名先登记准确映射、检查重名和依赖，同步现用程序、README和两张清单，核验原文件；历史日志与回执保留原字节，通过路径映射回查。

2026-10-10日志补充：**日志与追溯统一留测试包。** 项目根不新建或保留`logs/`。采用前后，运行日志、诊断、核验回执、渲染预览、来源和采用记录始终留在原`测试/分析类别/YYYYMMDD_主题/`；采用不迁走证据。对采用项获授权重跑时沿用原包，必要时在包内设运行日期子目录，先保留被替代记录。LOGROOT只指该包或其子目录。项目两张现用清单放一个明确的文件管理测试包，README用真实本地Markdown链接指向文件清单.csv和图表对应.csv，不为每次尝试复制导航。迁移历史logs先查依赖、记录映射与指纹，同步现用引用；保留原字节，删除仍须明确授权。

# CLAUDE.md 编写最佳实践

来源：咸鱼学术计量《怎样写一个好的 CLAUDE.md》
日期：2026-03-16
链接：https://mp.weixin.qq.com/s/UnRXVvXHNpZTCzojY-RPlg

---

## 核心原则

CLAUDE.md 是协作契约，不是知识库。控制 2000-3000 tokens，越短、越硬、越可执行越好。

---

## 必放内容（优先级顺序）

1. **build/test/run 流程** — 永远第一条
2. **目录结构 + 边界** — 防止乱改 raw data
3. **代码风格 & 命名规范** — 变量含义清晰
4. **NEVER 列表** — 红线：数据窥探、p-hacking、手动舍入
5. **Compact Instructions** — 上下文压缩时保留的核心
6. **验证标准** — 任务完成必须出 replication package

---

## NEVER 列表（红线）

- 永远不要手动删除/修改任何观测（用 `if` 或新变量标记）
- 禁止 p-hacking：不报告所有规格就报告"最显著"结果
- 禁止手动舍入 p-value / 系数
- 绝不直接覆盖 raw data 文件
- 禁止 regression 前不检查平行趋势 / 平衡性
- robustness check 必须在 master 脚本显式调用

---

## 推荐目录结构

```
project/
├── data/
│   ├── raw/           # 只读
│   └── processed/
├── scripts/
│   ├── 00_master.*
│   ├── 01_clean.*
│   ├── 02_analysis.*
│   └── 99_replication.*
├── paper/
├── results/
└── 测试/分析类别/YYYYMMDD_主题/  # 含全部运行日志，采用后仍留本包
```

---

## 验证闭环

任务完成后返回：
- replication.do 执行摘要
- 改动文件 + git diff
- LaTeX 编译状态
- doctor.sh 检查结果

---

## 实用技巧

1. 让 Claude 自己维护：发现错误后说 "Update your CLAUDE.md so you don't make that mistake again"
2. 配合 Git：任何改动前 git add + commit
3. 写 doctor.sh：检查 seed、文件完整性、p-value 格式
