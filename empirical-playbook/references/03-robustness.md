# 03 稳健性检验

## 1 顶刊常见做法

### 中文常见清单

| 类别 | 具体做法 |
|---|---|
| 替换 Y 度量 | 会计：修正 Jones 模型 DA（Dechow, Sloan & Sweeney 1995, TAR）、业绩匹配 DA（Kothari, Leone & Wasley 2005, JAE）、真实盈余管理（Roychowdhury 2006, JAE）、应计质量（Dechow & Dichev 2002, TAR）；创新：申请/授权/被引；投资效率：Richardson 模型等 |
| 替换 X 度量 | 虚拟变量 ↔ 强度/连续变量；不同口径或来源 |
| 改变样本 | 剔除直辖市、特殊年份（如 2008、2015、2020）、受同期其他政策影响的样本；缩短或延长窗口；只保留某板块 |
| 改变估计方法 | Tobit/Logit/PPML；更严格 FE（行业 × 年份、省份 × 年份）；更高层级聚类或双向聚类 |
| 改变处理 | 缩尾 1%/5% 或不缩尾；X 滞后一期；加入更多控制（遗漏变量候选） |
| 安慰剂 | 随机生成处理组/处理时点，重复 500—1000 次，报告真实系数在安慰剂分布中的位置；伪政策时点 |
| 排除竞争性解释 | 控制或剔除同期政策、宏观冲击 |
| DID 专项 | 平行趋势事件研究图；PSM-DID；多时点 DID 的异质性稳健估计量；Bacon 分解 |

据二手统计，2022—2023 年《经济研究》使用 DID 的论文中多数为多时点 DID，但只有少数在稳健性中使用异质性稳健估计量（来源为公众号整理，作为趋势线索，用前核对）。

### 英文顶刊与方法文献要求

- **多时点 DID**：TWFE 在处理效应异质时把已处理组当对照，可能出现负权重（Goodman-Bacon 2021, JoE；de Chaisemartin & D'Haultfœuille 2020, AER）。稳健估计量（下列为 Stata 命令名；Python 实现按 empirical-research 的 python-methods，pyfixest 已有 `did2s`、wild bootstrap 与 PPML，其余缺接口时自行实现同一估计量，不用 TWFE 冒充）：
  - Callaway & Sant'Anna (2021, JoE)：`csdid`
  - Sun & Abraham (2021, JoE)：`eventstudyinteract`
  - Borusyak, Jaravel & Spiess (2024, REStud) 插补：`did_imputation`
  - Gardner 两阶段 DID：`did2s`
  - de Chaisemartin & D'Haultfœuille：`did_multiplegt`/`did_multiplegt_dyn`
  - 堆叠 DID（Cengiz, Dube, Lindner & Zipperer 2019, QJE）：`stackedev`
  - 合成 DID（Arkhangelsky et al. 2021, AER）：`sdid`
- 综述与实操指南：Roth, Sant'Anna, Bilinski & Poe (2023, JoE)；Baker, Callaway, Cunningham, Goodman-Bacon & Sant'Anna (2025, arXiv 2503.13323) 的实务指南（覆盖协变量、权重、多期与交错处理）。
- **平行趋势**：事前系数不显著不等于平行趋势成立，事前检验功效低且会造成选择偏误（Roth 2022, AER: Insights）；用 HonestDiD 做敏感性分析，报告允许一定偏离时效应仍成立的范围（Rambachan & Roth 2023, REStud；`honestdid`）。
- **连续/强度处理 DID**：平行趋势可识别处理组平均效应，但比较不同强度的效应需要更强假设（Callaway, Goodman-Bacon & Sant'Anna，NBER WP 32117）。
- **随机化推断**：置换检验比常规 SE 更可靠，尤其在少簇、杠杆点多时（Young 2019, QJE）。
- **规格曲线/多重宇宙**：把所有合理规格的结果一起展示（Simonsohn, Simmons & Nelson 2020, Nature Human Behaviour）。
- **p 值操纵证据**：IV 和 DID 论文在显著性阈值附近堆积更明显（Brodeur, Cook & Heyes 2020, AER），审稿人对这两类设计的稳健性尤其严格。

## 2 审稿人常挑的问题

- 稳健性只做最容易的几项，没有针对本文的主要威胁；
- 多时点 DID 只用 TWFE；
- 平行趋势只靠肉眼看图或事前系数不显著；
- 安慰剂只做一种、次数太少，或不报告经验 p 值；
- 不显著的稳健性项被删掉不报；
- 剔除样本的理由是事后找的。

## 3 不显著时可借鉴

| 信号 | 做法 | 出处 | 风险 |
|---|---|---|---|
| 多时点 DID：TWFE 不显著或反号 | Bacon 分解/dCDH 权重诊断 → CS、SA、插补、did2s、堆叠；两者都报告，以稳健估计量为主 | Goodman-Bacon 2021；Roth et al. 2023 | 🟢 |
| 平均效应不显著但事件研究后期显著 | 报告动态效应，解释为滞后出现；平均效应照报 | Roth et al. 2023 | 🟡 |
| 事前系数有偏离 | HonestDiD 敏感性；或寻找更可比的对照组（PSM/熵平衡后 DID），对照组构造须事前说明 | Rambachan & Roth 2023 | 🟡 |
| 某个替换度量下不显著 | 判断该度量是否更精确：若更精确仍不显著，坦白并讨论；若该度量噪音更大（如简单 Jones），说明原因并报告业绩匹配等更好度量 | Kothari et al. 2005 | 🟡 |
| 剔除某类样本后不显著 | 说明该类样本是否是效应的主要来源（转为异质性讨论），不删掉这项稳健性 | — | 🟢（报告） |
| 常规 SE 下边缘显著、簇少 | 随机化推断/wild bootstrap，照实报告 | Young 2019；MacKinnon et al. 2023 | 🟢 |
| 想展示整体稳健 | 规格曲线：全部合理规格一起展示，而非挑选 | Simonsohn et al. 2020 | 🟢 |

## 4 检索关键词

- 中文：多时点双重差分 异质性稳健估计量；交错双重差分 负权重；平行趋势 敏感性；安慰剂检验 随机处理组；盈余管理 稳健性 业绩匹配 真实盈余管理；PSM-DID。
- 英文：staggered difference-in-differences heterogeneous treatment effects；event study pre-trends HonestDiD；randomization inference；specification curve；performance-matched discretionary accruals。
- 中文方法文献线索（据二手来源，用前核对）：张征宇等（2024，管理世界）关于双重差分下固定效应估计量何时可信；刘冲等（2022，数量经济技术经济研究）交错双重差分与估计方法选择；黄炜、张子尧（2023，数量经济技术经济研究）事件研究法的实现与拓展。
