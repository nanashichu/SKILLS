# 02 异质性分析

## 1 顶刊常见做法

### 中文

- **常用分组维度（上市公司）**：产权性质（国企/非国企）；规模；地区（东中西、市场化指数高低）；行业（高科技、重污染、竞争程度 HHI）；融资约束（SA、KZ、WW 指数）；公司治理（两职合一、机构持股、分析师关注、是否“四大”审计）；生命周期；内部控制质量；所在城市特征。
- **两种写法**：
  1. 分组回归 + **组间系数差异检验**：Fisher 组合（置换）检验、SUR（似无相关，Stata `suest`）、全交互模型的交互项检验；近年中文顶刊普遍要求报告差异检验 p 值（方法梳理见连玉君、廖俊平 2017，用前核对卷期）。
  2. 交互项：X × 调节变量（连续或虚拟），解释为“给定 H 时 X 的效应”。
- 分组变量用**处理前或样本期初值**，按中位数、行业-年度中位数或制度类别划分。

### 英文

- 以交互项、三重差分（DDD）为主，分组回归时报告组间差异检验；
- “显著 vs 不显著”的差别本身未必显著，必须正式检验差异（Gelman & Stern 2006, The American Statistician）；
- 多个分组维度同时检验时做多重检验校正：Anderson (2008, JASA) 的锐化 q 值、Romano & Wolf (2005, Econometrica)、BH；
- 机器学习异质性：因果森林（Wager & Athey 2018, JASA）；基于机器学习代理的 BLP/GATES/CLAN 推断（Chernozhukov, Demirer, Duflo & Fernández-Val 2025, Econometrica，原文针对随机实验，用于观察数据须满足识别假设）。

## 2 本项目默认与已有工具

- S9：各组默认在统一样本 `sample == 1` 中划分；分组变量缺失导致样本缩小时须说明。
- 正式差异检验写法见 [empirical-research 组间差异](../../empirical-research/references/group-difference-test.md)：主效应、交互项、线性组合（高组效应 = 主项 + 交互项）与完整协方差下的差异检验。

## 3 审稿人常挑的问题

- 两组一显著一不显著就宣称有差异；
- 分组变量受处理影响（用了处理后的值）；
- 分组阈值事后挑选（中位数、三分位、某个特定值来回换）；
- 每组用各自样本，与基准样本不一致；
- 分组维度过多却不校正多重检验；
- 异质性方向与机制解释不呼应。

## 4 不显著时可借鉴

| 信号 | 做法 | 出处 | 风险 |
|---|---|---|---|
| 主效应不显著，理论预期只对部分群体有效应 | 事前写明分组理由与预期方向，用全交互模型 + 正式差异检验；全样本结果照报 | Gelman & Stern 2006 | 🟡 |
| 分组后两组都不显著（样本被切小） | 改用连续调节变量交互，保留全样本功效 | — | 🟡 |
| 分组系数方向对但差异不显著 | 如实报告差异检验；可考虑三重差分；**不换阈值** | — | 🟢（报告）/🔴（换阈值） |
| 想找新的异质性维度 | 先从机制推导“渠道越重要的群体效应越强”，再选分组；多个维度做多重检验校正 | Anderson 2008；Romano & Wolf 2005 | 🟡 |
| 想用机器学习找子群 | 因果森林/GATES 作探索，明确标“探索性”，主结论仍用事前分组 | Wager & Athey 2018；Chernozhukov et al. 2025 | 🟡 |

## 5 检索关键词

- 中文：异质性分析 组间系数差异检验 费舍尔组合检验；产权性质 异质性；融资约束 SA指数 分组；市场化指数 分组；三重差分。
- 英文：heterogeneous treatment effects interaction triple difference；difference between significant and not significant；multiple hypothesis testing Romano-Wolf；causal forest heterogeneity；GATES best linear predictor。
