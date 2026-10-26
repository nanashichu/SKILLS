# 04 内生性

## 1 先写清内生性来源

管理学和会计顶刊的共同要求是：不笼统写“可能存在内生性问题”，而是写明来源（遗漏变量、反向因果、测量误差、样本选择、自选择），针对来源选方法，重点处理核心解释变量（《管理学季刊》网站发布的《管理研究中的内生性》，见案例卡库）。

| 来源 | 常用方法 | 关键前提 |
|---|---|---|
| 遗漏变量（不随时间变） | 个体 FE、更细 FE | FE 吸收的是不随时间变的部分 |
| 遗漏变量（时变） | 工具变量；准自然实验 DID；遗漏变量敏感性（Oster、sensemakr） | IV 排他性；平行趋势 |
| 反向因果 | X 滞后一期（弱）；IV；外生冲击 | 滞后 X 不能解决持续性遗漏变量 |
| 样本选择（只观察到部分样本的 Y） | Heckman 两阶段 | 需要可信的排除性变量 |
| 自选择进入处理 | PSM、熵平衡、IPW、DID、RDD | PSM/熵平衡只处理可观测变量 |
| 动态面板 | 差分/系统 GMM | AR(2)、Hansen 检验；工具数不宜过多 |

## 2 顶刊常见做法

### 中文

- X 滞后一期；
- 工具变量：同行业/同地区其他企业均值（剔除自身）、历史或地理变量、Bartik 份额-移动工具；报告第一阶段 F 与 Kleibergen-Paap 统计量；
- Heckman 两阶段（第一阶段 Probit 加入排除性变量，第二阶段加逆米尔斯比）；
- PSM（近邻 1:1 或 1:4、卡尺匹配）后回归，报告平衡性检验；熵平衡；
- 以外生政策构造 DID；
- 系统 GMM；
- 近年增加：Oster 系数稳定性检验、双重机器学习（DML）作为稳健性。

### 英文顶刊与方法文献要求

- **IV 强度与推断**：单内生变量时报告有效 F（Montiel Olea & Pflueger 2013, JBES）；传统“F > 10”规则下 t 检验仍会过度拒绝，可用 tF 调整临界值（Lee, McCrary, Moreira & Porter 2022, AER）或弱 IV 稳健的 AR 置信集（Andrews, Stock & Sun 2019, Annual Review of Economics 综述）。
- **IV 在实践中的问题**：IV 论文的 p 值操纵迹象最明显（Brodeur, Cook & Heyes 2020, AER）；已发表 IV 结果的推断常被少数簇或观测主导（Young 2022, European Economic Review）。
- **排他性**：允许工具对 Y 有小的直接效应时的敏感性分析（Conley, Hansen & Rossi 2012, REStat，“近似外生”）。同行均值类工具变量面临反射问题（Manski 1993, REStud），排他性需要专门论证。
- **Bartik/份额-移动工具**：识别来自份额外生（Goldsmith-Pinkham, Sorkin & Swift 2020, AER）或冲击外生（Borusyak, Hull & Jaravel 2022, REStud），需说明依赖哪一种并做对应检验。
- **会计研究中的 IV 与选择模型**：IV 在会计中的常见误用与报告要求（Larcker & Rusticus 2010, JAE）；Heckman 选择模型对排除性约束敏感，缺乏排除变量时结果不可靠（Lennox, Francis & Wang 2012, TAR）。
- **PSM 与熵平衡**：PSM 在会计研究中结果对设计选择敏感，应报告不同设计下结果（Shipman, Swanquist & Whited 2017, TAR）；熵平衡直接匹配协变量矩并保留样本（Hainmueller 2012, Political Analysis；在会计中的应用见 McMullin & Schonberger 2020, RAST）。
- **遗漏变量敏感性**：Oster (2019, JBES) 的 δ 与偏误调整系数（常用 R_max = 1.3 × 含控制模型 R²），思想来自 Altonji, Elder & Taber (2005, JPE)；Cinelli & Hazlett (2020, JRSSB) 的 sensemakr 给出推翻结论所需的混杂强度。
- **DML**：用机器学习灵活控制可观测混杂（Chernozhukov et al. 2018, Econometrics Journal），不处理不可观测混杂，不能当作解决内生性。

## 3 审稿人常挑的问题

- 内生性来源没说清，“一招解决所有”；
- 把 X 滞后一期当作解决反向因果；
- 工具变量排他性只有一句话；同行均值 IV 的排他性；
- 只报 Cragg-Donald F；弱 IV 下仍用常规 t；
- Heckman 没有排除性变量或排除变量不可信；
- PSM 后样本大幅缩小、只报一种匹配；
- 把 PSM/DML 说成解决了不可观测的内生性。

## 4 不显著时可借鉴

| 信号 | 做法 | 出处 | 风险 |
|---|---|---|---|
| 2SLS 不显著、OLS 显著 | 先看有效 F；报告 AR 置信集或 tF；说明 IV 估计方差大、功效低；**不换工具直到显著** | Lee et al. 2022；Andrews et al. 2019 | 🟢（报告）/🔴（换 IV 求显著） |
| OLS 不显著、2SLS 显著且远大于 OLS | 警惕弱 IV 与排他性违背；做近似外生敏感性；讨论 LATE 与 OLS 的差别 | Conley et al. 2012；Young 2022 | 🟡 |
| Heckman 第二阶段不显著 | 检查排除性变量是否真进第一阶段、逆米尔斯比与 X 是否高度共线 | Lennox et al. 2012 | 🟢 |
| PSM 后不显著 | 匹配丢样本致功效下降：熵平衡或 IPW 保留样本并报告平衡性；同时报告多种匹配设计 | Shipman et al. 2017；McMullin & Schonberger 2020 | 🟡 |
| 想证明遗漏变量不足以推翻结论 | Oster δ、sensemakr 稳健值 | Oster 2019；Cinelli & Hazlett 2020 | 🟢 |
| Bartik IV 不显著 | 检查依赖份额外生还是冲击外生、Rotemberg 权重集中在哪些行业 | Goldsmith-Pinkham et al. 2020；Borusyak et al. 2022 | 🟡 |

## 5 检索关键词

- 中文：内生性 工具变量 同行业均值；Heckman 两阶段 排除性约束；倾向得分匹配 熵平衡；Oster 检验 遗漏变量；双重机器学习 稳健性；Bartik 工具变量。
- 英文：weak instruments robust inference effective F；plausibly exogenous；shift-share instruments；selection models accounting research；propensity score matching accounting；entropy balancing；coefficient stability unobservable selection；sensemakr。
