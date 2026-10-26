# 01 基准回归

## 1 顶刊常见做法

### 中文（经济研究、管理世界、中国工业经济、金融研究、会计研究等）

- **逐步加入控制与 FE**：本项目默认 S9 四列（无控制无FE → 有控制无FE → 无控制有FE → 有控制有FE），以第 4 列为首选。
- **FE**：企业（或城市）+ 年份双向 FE 为常规；要求更严时加行业 × 年份、省份 × 年份 FE 吸收行业/地区层面的时变冲击。
- **聚类**：企业层面最常见；处理在城市/省份/行业层面分配时聚类到该层级。
- **上市公司常规控制**：规模、杠杆、盈利能力、成长性、董事会规模、独立董事比例、两职合一、第一大股东持股、产权性质、上市年限、托宾 Q/账面市值比等（字段与合理范围见 empirical-research 的 listed-firm-data）；连续变量 1%/99% 缩尾；剔除金融业、ST/*ST。
- **经济显著性**：系数 × X 标准差 ÷ Y 均值（或 Y 标准差），写进正文。

### 英文（JF、JFE、RFS、JAR、JAE、TAR、AER 等）

- **FE 结构要有制度理由**：FE 改变的是“和谁比较”，会改变样本与变量含义，需说明为何选这一层级并透明报告（Breuer & deHaan 2024, JAR）。
- **用 FE 而非对 Y 做行业调整**：对 Y 先减行业均值再回归会产生偏误，应在回归中放 FE（Gormley & Matsa 2014, RFS）。
- **残差不宜直接当 Y**：两步法（先估计正常水平取残差，再对残差回归）会使系数和 t 值有偏；把第一步的回归元放进第二步，或一步估计（Chen, Hribar & Melessa 2018, JAR）。盈余管理 DA、超额投资、异常收益都适用。
- **控制变量宁少而准**：只放处理前决定、影响 Y 且不受 X 影响的变量；坏控制会把无偏模型变成有偏（Whited, Swanquist, Shipman & Moon 2022, TAR）。
- **聚类按设计**：取决于处理分配与抽样，而不是哪种 SE 更小（Abadie, Athey, Imbens & Wooldridge 2023, QJE）；面板中企业与时间两个维度的相关都要考虑（Petersen 2009, RFS）；DID 序列相关会大幅低估 SE（Bertrand, Duflo & Mullainathan 2004, QJE）。

## 2 较新做法与方法文献

- 测量误差与高维 FE 共同作用会放大系数、提高假阳性概率，建议在多个代理、多种 FE 结构下对照（Jennings, Kim, Lee & Taylor 2024, RAST）。
- 少簇推断：wild cluster bootstrap（Cameron, Gelbach & Miller 2008, REStat；MacKinnon, Nielsen & Webb 2023, JoE 指南；Stata `boottest`）。
- 零值较多的 Y：log(1+y) 的估计依赖单位，结果不可解释为百分比（Chen & Roth 2024, QJE）；计数或非负 Y 用 PPML（Santos Silva & Tenreyro 2006, REStat；高维 FE 用 `ppmlhdfe`）。

## 3 审稿人常挑的问题

- 只在最严格一列显著，或只在无 FE 列显著却按“稳健”表述；
- 控制变量包含受处理影响的变量或机制变量；
- 聚类层级低于处理分配层级；
- DA 等残差型 Y 的两步法；
- 没报告经济显著性，或经济显著性大得不合理（提示测度或样本问题）。

## 4 不显著时可借鉴

| 信号 | 做法 | 出处 | 风险 |
|---|---|---|---|
| 加 FE 后不显著 | 计算 X 被 FE 吸收后的残余变异；若识别变异过小，说明设计识别力弱。可对照报告几种有制度理由的 FE 结构，**不能为显著去掉 FE** | Breuer & deHaan 2024 | 🟡 |
| 加控制后不显著 | 逐个检查控制是否处理后决定/是否机制变量；改用处理前值或基期值 × 年份 | Whited et al. 2022 | 🟢（确属坏控制时） |
| 残差型 Y（DA、超额投资）不显著 | 改一步法：第一步回归元放入第二步 | Chen, Hribar & Melessa 2018 | 🟢 |
| SE 大、簇少 | 检查聚类层级是否与处理一致；簇少用 wild bootstrap（结果可能更不显著） | Abadie et al. 2023；MacKinnon et al. 2023 | 🟢 |
| Y 高度偏态或大量零 | 计数/非负 Y 用 PPML；比率型 Y 检查分母是否随处理变化 | Santos Silva & Tenreyro 2006；Chen & Roth 2024 | 🟡 |
| 效应有滞后 | X 滞后一期或事件研究看各期；须有制度时点依据 | — | 🟡 |
| 测量误差大 | 换文献公认更精确的代理，原代理照报 | Jennings et al. 2024 | 🟡 |

## 5 检索关键词

- 中文：基准回归 固定效应 选择；控制变量 选择 坏控制；聚类标准误 层级；经济显著性。
- 英文：fixed effects interpretation accounting；bad controls；residuals as dependent variables；clustering standard errors design-based；few clusters wild bootstrap。
