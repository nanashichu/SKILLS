# 期刊清单与检索指南

## 1 期刊范围（经济 + 金融 + 会计）

| 类别 | 中文 | 英文 |
|---|---|---|
| 经济综合 | 经济研究、管理世界、中国工业经济、经济学（季刊）、世界经济、中国社会科学（经济类文章） | AER、QJE、JPE、Econometrica、REStud；补充 AER: Insights、AEJ: Applied/Policy、REStat |
| 金融 | 金融研究；补充 经济学（季刊）、管理世界中的金融类文章 | JF、JFE、RFS；补充 JFQA、Review of Finance |
| 会计与公司治理 | 会计研究、南开管理评论、审计研究、管理科学学报 | JAR、JAE、TAR；补充 RAST、CAR |
| 管理综合 | 管理世界、管理科学学报 | Management Science |
| 方法文献来源 | 数量经济技术经济研究（方法综述多，非应用顶刊）、计量经济学报 | Journal of Econometrics、JBES、Annual Review of Economics、Stata Journal |

应用案例以上表顶刊为准；方法类结论优先引用方法期刊原文，不以应用论文的写法替代方法要求。

## 2 检索式模板

把 `{设计}` 换成 DID/多时点DID/工具变量/断点回归/PSM 等，`{Y}` 换成研究结果变量，`{对象}` 换成上市公司、城市等。

| 部分 | 中文 | 英文 |
|---|---|---|
| 基准 | `{Y} {设计} 固定效应 聚类 管理世界`；`{Y} 影响因素 上市公司 经济研究` | `{Y} fixed effects firm-year clustering Journal of Accounting Research` |
| 异质性 | `{Y} 异质性 产权性质 组间差异 检验`；`{设计} 三重差分 {Y}` | `{Y} cross-sectional variation triple difference` |
| 稳健性 | `{设计} 稳健性 安慰剂 {Y}`；`多时点双重差分 异质性稳健 {Y}` | `{Y} staggered difference-in-differences robustness`；`{Y} alternative measures` |
| 内生性 | `{Y} 工具变量 内生性 {对象}`；`{Y} Heckman 熵平衡` | `{Y} instrumental variable exclusion restriction`；`{Y} entropy balancing` |
| 机制 | `{Y} 机制检验 渠道 {X}`；`{X} 影响 {M} 机制` | `{X} {Y} mechanism channel` |
| 进一步分析 | `{X} 经济后果 {Y} 溢出效应` | `{X} real effects spillover peers` |

技巧：先用 2—4 个词宽泛检索，再加期刊名或年份收窄；同一主题中英文各检索至少一次；方法问题加 `综述/指南` 或 `guide/review/practitioner`。

## 3 可访问来源（2026-10 实测）

| 来源 | 状态 | 用法 |
|---|---|---|
| CNKI（cnki.com.cn）| 自动抓取被拒（robots） | 只能从检索结果拿标题线索；全文请用户提供 |
| 中国工业经济官网（ciejournal.ajcass.com）| 要求验证码 | 同上；或用户在已登录/已验证的浏览器中打开 |
| 维普、掌桥、期刊官网目录页 | 部分可读摘要 | 核对标题、作者、期号 |
| 作者主页、学校网站 PDF | 常可读全文 | 优先使用 |
| arXiv、NBER、SSRN | 可读摘要，多数可读全文 | 英文方法与工作论文 |
| IDEAS/RePEc | 可读摘要与卷期页码 | 核对英文文献卷期 |
| 上财学术速递（academicnewsletter.sufe.edu.cn）| 可读英文顶刊摘要 | 快速了解近期论文 |
| 公众号、知乎、CSDN、课程广告 | 部分可读，知乎常被拒 | 只作线索，入库前找一手来源核对 |

读不到全文时：请用户上传 PDF 或粘贴相关章节；有用户已登录的浏览器时可在其中阅读（按浏览器 skill 的规则）。

## 4 读一篇论文时提取什么

按六部分逐一记录（没有的部分写“无”），重点是**可迁移**的做法：

1. 识别设计与核心假设；处理/对照如何构造；
2. 基准：FE、聚类层级、控制变量集合、样本筛选、缩尾；
3. 异质性：分组维度、划分方法、是否做差异检验及用什么方法；
4. 稳健性：逐项列出，并注明各项针对哪种威胁；
5. 内生性：来源表述、方法、关键检验统计量的报告方式；
6. 机制：一步法还是三步法、M 的代理、如何排除竞争性渠道；
7. 进一步分析：做了哪些、与主线的关系；
8. 有没有报告不显著或失败的结果，怎么写的。

## 5 来源可信度

一手全文 > 一手摘要 > 期刊官网目录 > 二手综述（公众号/知乎/课程）。案例卡标注“全文/仅摘要/二手线索”。卷期、作者、年份只写核对过的；没核对的写“待核对”。
