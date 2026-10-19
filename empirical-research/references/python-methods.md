# Python 实证方法详解

## 默认执行阶段与批量计算

按[SKILL.md后端规则](../SKILL.md)，Python负责日常构建、筛选、全套重跑和Word/图表交付；Stata/do只在最终研究版本确认后或用户直接要求时核对。下面的软件对照是语义参考，不是启动Stata的要求。

- 先读取一次现有完整面板，只取当前模块必要列；按真实样本、FE和权重复用投影与矩阵分解。输入指纹、缩尾/变换、样本或模型设定变化时缓存失效。
- 置换可复用不变控制变量与FE的投影，并对每次变化的处理变量正确残差化；沿用约定置换向量/种子，保存每次估计、实际支持及失败，不只给一个经验p值。
- 聚类协方差、自由度、小样本修正、singleton、权重及总体/within R²显式记录。软件默认值不能作为与历史Stata口径相同的证据；必要时用独立Python实现核验b和SE。
- CS、SA、Stacked DID、did2s、dCDH等各自实现既定估计量与推断；缺少接口时实现或保留具体未估计原因，不自动换Stata或普通TWFE。
- 并行限制工作进程与BLAS线程总量；速度优化不能省略协方差、真实样本、失败状态、动态系数或文档逐格/视觉核验。

## 0. Python 代码质量检查（Quality Gates）

### 0.1 致命错误（直接 < 80 分）

| 错误 | 说明 | 正确做法 |
|------|------|----------|
| 面板数据未设置 MultiIndex | `PanelOLS` 无法识别面板结构 | `df.set_index(['firm_id', 'year'])` |
| 聚类标准误未指定 | 显著性推断无效 | `model.fit(cov_type='clustered', cluster_entity=True)` |
| 缺失值未处理 | 回归失败或结果错误 | `df.dropna()` 或 `df.fillna()` |
| 滞后变量未按实体与日历间隔 | 混淆个体或跨过年份缺口 | 按实体键与目标年份连接，或补齐时间索引后移位；直接groupby/shift仅适用于已验证连续的时间索引 |
| 未添加常数项 | 无截距项回归 | `sm.add_constant(X)` |

### 0.2 必检项

| 检查项 | 要求 | 扣分 |
|--------|------|------|
| 包导入 | 正确导入 `linearmodels.panel` | -5 |
| 数据索引 | `set_index(['firm_id', 'year'])` | -10 |
| 缺失值处理 | `dropna` 或 `fillna` | -10 |
| 注释完整 | 函数有 docstring | -5 |
| 结果提取 | 正确提取 `params`, `tstats`, `pvalues` | -10 |

### 0.3 Code-Theory Alignment 检查

```python
# 论文公式：Y_it = α + β·X_it + γ·Controls_it + μ_i + λ_t + ε_it

# ✅ 正确实现
df = df.set_index(['firm_id', 'year'])
X = sm.add_constant(df[x_vars])
model = PanelOLS(df['y'], X, entity_effects=True, time_effects=True)
result = model.fit(cov_type='clustered', cluster_entity=True)

# ❌ 错误示例 1：缺少固定效应
model = PanelOLS(df['y'], X)  # 无 entity_effects, time_effects

# ❌ 错误示例 2：缺少聚类标准误
result = model.fit()  # 无 cov_type='clustered'

# ❌ 错误示例 3：未设置面板索引
model = PanelOLS(df['y'], X, entity_effects=True)  # df 未 set_index
```

---

## 1. 面板回归（linearmodels）

### 1.1 环境配置

```python
import pandas as pd
import numpy as np
from linearmodels.panel import PanelOLS
import statsmodels.api as sm
from scipy import stats
```

### 1.2 面板回归函数

```python
def run_panel_regression(data, y_var, x_vars, entity_fe=True, time_fe=True, cluster_entity=True):
    """
    运行面板回归

    Parameters:
    -----------
    data : DataFrame (已设置 MultiIndex)
    y_var : str, 被解释变量
    x_vars : list, 解释变量列表
    entity_fe : bool, 是否包含个体固定效应
    time_fe : bool, 是否包含时间固定效应
    cluster_entity : bool, 是否按个体聚类
    """
    reg_data = data[[y_var] + x_vars].dropna()
    y = reg_data[y_var]
    X = reg_data[x_vars]
    X = sm.add_constant(X)

    model = PanelOLS(y, X, entity_effects=entity_fe, time_effects=time_fe)
    result = model.fit(cov_type='clustered', cluster_entity=cluster_entity)
    return result
```

### 1.3 使用示例

```python
# 数据准备
df = pd.read_stata('data.dta')
df = df.set_index(['firm_id', 'year'])

# 运行回归
ctrl_vars = ['L_size', 'L_lev', 'L_roa', 'L_bm', 'L_growth']
x_vars = ['L_digital'] + ctrl_vars
result = run_panel_regression(df, 'crash_risk', x_vars)

# 提取结果
print(f"系数: {result.params['L_digital']:.4f}")
print(f"t值: {result.tstats['L_digital']:.2f}")
print(f"p值: {result.pvalues['L_digital']:.4f}")
print(f"观测数: {result.nobs}")
print(f"R²: {result.rsquared_within:.4f}")
```

### 1.4 结果汇总

```python
def results_to_df(results_dict):
    """将多个回归结果转为 DataFrame"""
    rows = []
    for name, res in results_dict.items():
        for var in res.params.index:
            if var == 'const':
                continue
            rows.append({
                'model': name,
                'variable': var,
                'coef': res.params[var],
                'tstat': res.tstats[var],
                'pval': res.pvalues[var]
            })
    return pd.DataFrame(rows)
```

---

## 2. 机制检验（Sobel）

```python
from scipy import stats

def sobel_test(a, b, se_a, se_b):
    """
    Sobel 检验

    Parameters:
    -----------
    a : float, X → M 的系数
    b : float, M → Y 的系数（控制 X 后）
    se_a : float, a 的标准误
    se_b : float, b 的标准误
    """
    z = a * b / np.sqrt(b**2 * se_a**2 + a**2 * se_b**2)
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return z, p

# 使用示例
result_step2 = run_panel_regression(df, 'mechanism', ['L_digital'] + ctrl_no_lag)
result_step3 = run_panel_regression(df, 'crash_risk', ['L_digital', 'mechanism'] + ctrl)

a_coef = result_step2.params['L_digital']
a_se = abs(a_coef / result_step2.tstats['L_digital'])
b_coef = result_step3.params['mechanism']
b_se = abs(b_coef / result_step3.tstats['mechanism'])

z_sobel, p_sobel = sobel_test(a_coef, b_coef, a_se, b_se)
```

---

## 3. 双重差分（DiD）

### 3.1 经典 2x2 DiD

```python
def did_2x2(data, y_var, treat_var, post_var, controls=None):
    """经典 2x2 DiD"""
    data = data.copy()
    data['treat_post'] = data[treat_var] * data[post_var]

    x_vars = [treat_var, post_var, 'treat_post']
    if controls:
        x_vars.extend(controls)

    return run_panel_regression(data, y_var, x_vars)
```

### 3.2 事件研究

```python
def event_study(data, y_var, treat_var, rel_time_var, base_period=-1, controls=None):
    """事件研究法"""
    for t in data[rel_time_var].unique():
        if t != base_period:
            data[f't_{int(t)}'] = (data[rel_time_var] == t) * data[treat_var]

    x_vars = [f't_{int(t)}' for t in sorted(data[rel_time_var].unique()) if t != base_period]
    if controls:
        x_vars.extend(controls)

    return run_panel_regression(data, y_var, x_vars)
```

---

## 4. 数据清洗

### 4.1 变量处理

```python
# 重命名
df.columns = df.columns.str.lower()
df.columns = df.columns.str.replace(' ', '_')

# 类型转换
df['income'] = pd.to_numeric(df['income'], errors='coerce')

# 缺失值
print(df.isnull().sum())
df = df.dropna(subset=['key_var'])
df['income'] = df['income'].fillna(df['income'].median())
```

### 4.2 异常值处理

```python
from scipy.stats import mstats

# Winsorize
df['income_win'] = mstats.winsorize(df['income'], limits=[0.01, 0.01])

# IQR 方法
Q1 = df['income'].quantile(0.25)
Q3 = df['income'].quantile(0.75)
IQR = Q3 - Q1
outlier_mask = (df['income'] < Q1 - 1.5*IQR) | (df['income'] > Q3 + 1.5*IQR)
```

### 4.3 滞后变量

下列`groupby.shift/diff`示例仅适用于已经核验每个实体内时间索引唯一且按研究频率连续的面板。存在断年或缺期时，排序不等于补齐日历间隔；应按实体键与目标年份连接，或先补齐时间索引再移位，并据同一日历滞后计算差分，不能把物理上一行当成上一期。

```python
# 面板数据必须先排序
df = df.sort_values(['firm_id', 'year'])

# 滞后
df['L_x'] = df.groupby('firm_id')['x'].shift(1)
df['L2_x'] = df.groupby('firm_id')['x'].shift(2)

# 差分
df['D_x'] = df.groupby('firm_id')['x'].diff()
```

---

## 5. PyFixest（推荐：替代 Stata reghdfe）

> **重要**：PyFixest 是 Python 中最接近 Stata `reghdfe` 的工具，底层算法一致（迭代去均值），支持高维固定效应、聚类标准误、IV、DiD 等全套实证方法。

### 5.1 安装

```bash
pip install pyfixest
# Wild Bootstrap / Romano-Wolf 需要额外安装
pip install wildboottest
```

### 5.2 基础 OLS

```python
import pyfixest as pf
import pandas as pd
import numpy as np

# 简单 OLS
fit1 = pf.feols("Y ~ X1", data=data)
fit2 = pf.feols("Y ~ X1 + X2", data=data)
pf.etable([fit1, fit2])

# 查看结果
fit1.summary()       # 完整摘要
fit1.tidy()         # DataFrame（系数、标准误、t值、p值、置信区间）
fit1.coef()         # 系数向量
fit1.se()           # 标准误向量
fit1.tstat()        # t统计量
fit1.pvalue()       # p值
fit1.confint()      # 置信区间
fit1.resid()        # 残差
fit1.predict()      # 拟合值
```

### 5.3 高维固定效应

```python
# 单维固定效应
fit_fe1 = pf.feols("Y ~ X1 + X2 | f1", data=data)

# 双维固定效应（个体 + 年份）
fit_fe2 = pf.feols("Y ~ X1 + X2 | firm_id + year", data=data)

# 三维及更多固定效应
fit_fe3 = pf.feols("Y ~ X1 + X2 | firm_id + year + industry", data=data)
```

> **与 Stata 对照**：`reghdfe Y X1 X2, absorb(f1 f2)` 对应 `pf.feols("Y ~ X1 + X2 | f1 + f2", data=data)`

### 5.4 标准误完整菜单

| 类型 | PyFixest | Stata |
|------|----------|-------|
| 同方差 iid | `vcov="iid"` | 默认 |
| 异方差稳健 HC1 | `vcov="HC1"` | `vce(robust)` |
| 聚类稳健 CRV1 | `vcov={"CRV1": "firm"}` | `cluster(firm)` |
| 双维聚类 CRV1 | `vcov={"CRV1": "firm + year"}` | `cluster(firm year)` |
| CRV3 (jackknife) | `vcov={"CRV3": "firm"}` | 无直接等价 |

```python
# 单维聚类
fit = pf.feols("Y ~ X1 + X2 | f1", data=data, vcov={"CRV1": "f1"})

# 双维聚类（个体 + 时间）
fit = pf.feols("Y ~ X1 + X2 | firm + year", data=data, vcov={"CRV1": "firm + year"})

# 动态切换标准误（无需重新估计）
fit.vcov("iid").summary()                      # 同方差
fit.vcov("HC1").summary()                      # 异方差稳健
fit.vcov({"CRV1": "firm"}).summary()           # 聚类
fit.vcov({"CRV1": "firm + year"}).summary()    # 双维聚类
```

### 5.5 Wild Bootstrap 与随机化推断

```python
# Wild Bootstrap
fit = pf.feols("Y ~ X1", data=data, vcov={"CRV1": "group_id"})
fit.wildboottest(param="X1", reps=999)

# 随机化推断
fit.ritest(resampvar="X1=0", reps=1000, cluster="group_id")
```

### 5.6 工具变量估计 (IV/2SLS)

```python
# 有固定效应的 IV
iv_fit = pf.feols("Y2 ~ 1 | firm + year | X1 ~ Z1 + Z2", data=data)
iv_fit.summary()

# 查看第一阶段
pf.etable([iv_fit._model_1st_stage, iv_fit])

# 第一阶段 F 统计量
print(iv_fit._f_stat_1st_stage)

# Olea & Pflueger (2013) 有效 F 统计量
print(iv_fit._eff_F)
```

> **Stata 对照**：`ivreghdfe Y2 (X1 = Z1 Z2), absorb(firm year)`

### 5.7 泊松回归 (PPML)

```python
pois_fit = pf.fepois("Y ~ X1 | group_id", data=data, vcov={"CRV1": "group_id"})
pois_fit.summary()
```

> **Stata 对照**：`ppmlhdfe Y X1, absorb(group_id) cluster(group_id)`

### 5.8 GLM（Logit / Probit）

```python
# ⚠️ 注意：feglm() 当前版本不支持 | 吸收固定效应，需用 C() 生成哑变量

# Logit
fit_logit = pf.feglm("Y ~ X1 + X2 + C(f1)", data=data, family="logit")

# Probit
fit_probit = pf.feglm("Y ~ X1 + X2 + C(f1)", data=data, family="probit")

# 预测
fit_logit.predict(type="response")   # 概率尺度
fit_logit.predict(type="link")       # 线性预测值
```

### 5.9 分位数回归

```python
fit_qr = pf.quantreg("Y ~ X1 + X2", data=data, quantile=[0.1, 0.25, 0.5, 0.75, 0.9])
pf.qplot(fit_qr)  # 可视化
```

> **注意**：PyFixest 分位数回归目前不支持固定效应

### 5.10 多模型批量估计（杀手级特性）

```python
# csw0: 累积逐步加入变量（从空模型开始）
multi_fit = pf.feols("Y ~ X1 | csw0(f1, f2)", data=data, vcov="HC1")

# sw / sw0: 逐个替换变量
fit_sw = pf.feols("Y ~ X1 + sw(X2, C(f1))", data=data)

# 多因变量
fit_multi = pf.feols("Y + Y2 ~ X1 | firm", data=data)

# 按分组跑回归
fit_split = pf.feols("Y ~ X1", data=data, split="f1")

# 访问单个模型
multi_fit.all_fitted_models["Y ~ X1"]
multi_fit.fetch_model(0)
```

### 5.11 假设检验进阶

```python
# Wald 联合检验
fit.wald_test(R=np.eye(2))  # H0: X1=0 且 X2=0

# 自定义约束
R = np.array([[1, 2], [0, 1]])
q = np.array([2.0, 1.0])
fit.wald_test(R=R, q=q)

# Bonferroni 校正
pf.bonferroni([fit1, fit2], param="X1")

# Romano-Wolf 校正
pf.rwolf([fit1, fit2], param="X1", reps=9999, seed=1234)

# Westfall-Young 校正
pf.wyoung([fit1, fit2], param="X1", reps=9999, seed=1234)
```

### 5.12 DID 与事件研究

```python
# TWFE 事件研究
fit_twfe = pf.feols(
    "dep_var ~ i(rel_year, ref=-1.0) | state + year",
    data=df_het,
    vcov={"CRV1": "state"}
)

# Gardner's DID2S
fit_did2s = pf.did2s(
    df_het,
    yname="dep_var",
    first_stage="~ 0 | state + year",
    second_stage="~i(rel_year, ref=-1.0)",
    treatment="treat",
    cluster="state"
)

# 统一 API
fit_twfe = pf.event_study(data=df_het, yname="dep_var", idname="state",
                           tname="year", gname="g", estimator="twfe")

# 事件研究图
pf.iplot(fit_did2s, coord_flip=False, figsize=(900, 400), title="TWFE vs DID2S")

# 面板数据可视化
pf.panelview(df_het, unit="state", time="year", treat="treat")
```

### 5.13 表格输出与可视化

```python
# 发表级回归表
pf.etable(
    [fit1, fit2],
    labels={"Y": "Log Wage", "X1": "Experience", "X2": "Education"},
    felabels={"f1": "Industry FE"},
    caption="Baseline Regression Results"
)

# 描述性统计表
pf.dtable(data, vars=["Y", "X1", "X2"], stats=["mean", "sd", "min", "max", "count"])

# 系数图
fit.coefplot()
pf.coefplot([fit1, fit2])
```

### 5.14 PyFixest 与 Stata 结果对比检查点

| 检查项 | Python阶段须记录 | 最终核对要求 |
|--------|------------------|--------------|
| HC2/HC3 | 杠杆值定义、FE处理、有限样本修正及包版本 | 读取既定Stata命令的实际定义并比较；不依据默认值推断一致 |
| 多维聚类 | 各维度簇数、交集项、小样本修正及检验自由度 | 对照完整协方差与t/z分布，明确自由度规则 |
| CRV1 / HC1 | N、有效参数数、吸收FE自由度、singleton、权重与修正因子 | 显式匹配既定口径；同名协方差类型不能证明SE/p相同 |

### 5.15 常见踩坑

| 坑 | 错误做法 | 正确做法 |
|----|----------|----------|
| feglm() 固定效应 | `feglm("Y ~ X1 \| f1", ...)` | 用 `C(f1)` 代替 |
| HC2/HC3 与 FE | `vcov="HC3"` 报错 | 用 `vcov={"CRV3": "f1"}` |
| 聚类变量有缺失值 | 静默错误 | `df.dropna(subset=["f1"])` |
| C() 嵌套 sw() | `sw0(X2, C(f1))` 报错 | 预先生成哑变量 |
| IV 无外生变量 | `"Y ~ \| f1 \| X1 ~ Z1"` | `"Y ~ 1 \| f1 \| X1 ~ Z1"` |
| i() 的 ref 类型 | `ref=-1` (int) | `ref=-1.0` (float) |

### 5.16 速查对照表

| 任务 | Stata | PyFixest |
|------|-------|----------|
| OLS | `reghdfe Y X1 X2, noabsorb` | `pf.feols("Y ~ X1 + X2", data=df)` |
| 稳健标准误 | `reghdfe Y X1, noabsorb vce(robust)` | `pf.feols("Y ~ X1", data=df, vcov="HC1")` |
| 聚类标准误 | `reghdfe Y X1, noabsorb vce(cluster id)` | `pf.feols("Y ~ X1", data=df, vcov={"CRV1": "id"})` |
| 单维 FE | `reghdfe Y X1, absorb(id)` | `pf.feols("Y ~ X1 \| id", data=df)` |
| 双维 FE | `reghdfe Y X1, absorb(id year)` | `pf.feols("Y ~ X1 \| id + year", data=df)` |
| IV/2SLS | `ivreghdfe Y (X1=Z1 Z2), absorb(id)` | `pf.feols("Y ~ 1 \| id \| X1 ~ Z1 + Z2", data=df)` |
| Poisson | `ppmlhdfe Y X1, absorb(id)` | `pf.fepois("Y ~ X1 \| id", data=df)` |
| Logit w/ FE | `logit Y X1 i.id` | `pf.feglm("Y ~ X1 + C(id)", data=df, family="logit")` |
| Wild Bootstrap | `boottest X1, reps(999)` | `fit.wildboottest(param="X1", reps=999)` |
| 逐步加变量 | 手动写多个 reghdfe | `pf.feols("Y ~ X1 \| csw0(f1, f2)", data=df)` |
| 回归表 | `esttab m1 m2` | `pf.etable([fit1, fit2])` |
