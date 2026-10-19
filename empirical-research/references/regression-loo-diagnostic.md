# 通用回归排除自身诊断

当用户要求 rangestat 排除自身回归、逐观测影响诊断或复现按目标系数排序删除时使用。它是诊断工具；按结果排序不提供数据错误或合理样本剔除的实质依据。

入口：[../scripts/regression_loo_diagnostic.py](../scripts/regression_loo_diagnostic.py)。该文件可独立运行，不依赖知识产权法庭项目数据或代码。

## 线性回归公式接口

加载技能脚本后，调用：

```python
result = formula_linear(
    df,
    formula="y ~ did + x1 + x2 + C(firm_id) + C(year)",
    target="did", cluster="city_id", drop_counts=(2, 120, 240))
save_result(result, data_dir, log_dir)
```

- formula 写完整因变量、核心变量、控制、交互项和类别固定效应；target 是估计器中的完整目标系数名。
- cluster=None 为普通OLS；指定列名为单维聚类，采用估计器的有限样本修正和t推断。
- 公式类别FE使用显式虚拟变量，适合中小规模数据。大规模高维FE须使用保持原吸收规则的估计器或压缩适配器，不展开千万家企业虚拟变量。
- 数值完整案例由公式估计器处理；聚类键缺失、设计共线、删除后识别失败及排除窗口失败须记录。杠杆接近1的秩变化窗口标为不可计算，不能当作普通排序值。

## 自定义拟合函数：接入其他模型

```python
def fit(sample):
    return smf.logit("binary_y ~ did + x1 + x2", sample).fit(disp=False)

result = regression_diagnostic(
    df, fit=fit, target="did", drop_counts=(2, 120, 240))
```

fit 接收删后的DataFrame，返回 statsmodels 估计对象；其他估计器可返回含 b、se、p、N 的字典，或 params[target]。同时保留完整b/V、实际样本、失败信息。固定效应、聚类、权重、singleton、随机种子与有效样本规则由 fit 保持原设定。回调路径逐条重新估计，可用于非线性模型，计算成本为观测数次拟合。

线性快路径用精确OLS排除公式。已有高维FE/压缩实现可复用 linear_loo_coefficient(coefficient, slope, residual, leverage)，或传 regression_diagnostic(..., loo=精确逐行系数数组)。数组必须与传入数据原始行顺序一一对应。非线性影响近似不能冒充精确删除结果。

## 执行规则与输出

候选及现用输出数据统一指定到data/temp中的真实任务，日志与回执留原分类测试包；采用时复用数据，不再复制。调用者将数据路径指定到temp、回执路径指定到分类测试包；复用历史函数前检查其路径保护与本条是否一致，拒绝初稿、跨包拆分试验输出、正式data内的日志、输入冲突及已有固定目标；替换已有输出前先保留可恢复归档。程序不能自行判断用户是否采用，调用者登记候选/采用状态，不能仅因位于temp就视为采用。以上是保存路径保护，不改变诊断算法。

当前通用接口的排序使用重置后的原始行号，保存阶段b/V和N；它尚未自动保存每阶段估计器实际使用的实体键。正式项目必须在适配器中另存“原始行号—实体键”映射及每阶段实际样本，或登记该证据缺口；不能把删除行号或N称作完整实际样本ID。

1. 先固定原模型、目标系数、删除单位（本脚本是单条观测）和要比较的删除阶段。默认比较2、120条，样本不足时明确调整数量；删除数须小于样本行数。
2. 计算全样本排除每行后的目标系数，降序排序；并列按原始行号，缺失置末。
3. 各阶段从同一初始排序删除前k行，并按原模型重新拟合；不自动每轮重新排名，不按显著性决定停止。不把删单条企业年度偷换为删整家企业或整个城市。
4. 保存完整排序、所有阶段（包含不显著、反向、失败）、完整b/V和实际删除行号；大样本压缩排序必须保留频数、具体观测映射和总样本覆盖核验。
5. 删除依据使用了因变量与回归结果，删后普通p值未经样本选择校正，必须标为探索性诊断；各模型分别排序时明确样本不同。不得将该排序自动转为主样本规则或确认性因果结论。
6. 后续仍按技能的“先总结、用户要求才导出”规则工作。用户只要求导出已保存结果时，不重新估计。

## 命令行与加载

依赖 numpy、pandas、statsmodels、scipy、pyarrow、patsy。支持DTA、Parquet、CSV。

```powershell
python "<技能目录>/scripts/regression_loo_diagnostic.py" --input "数据.dta" --formula "y ~ did + x1 + x2 + C(firm_id) + C(year)" --target did --cluster city_id --drop 2 120 240 --data-dir "data/temp/YYYYMMDD_回归影响诊断" --log-dir "测试/分析类别/YYYYMMDD_回归影响诊断"
```

Python可用 importlib.util.spec_from_file_location 加载脚本，或用 runpy.run_path(脚本实际路径) 取得 formula_linear、regression_diagnostic、save_result。技能目录使用本轮实际SKILL.md所在目录；不能依赖原项目的56号脚本路径。

自测使用 --self-test 并指定 --data-dir、--log-dir。已验证三种线性规格共240个排除窗口（多变量、交互、企业/年份FE、城市聚类），及30个Logit回调窗口。该核验不启动Stata。

来源：2026-10-10知识产权法庭项目56号通用脚本，本轮仅增加保存路径及防覆盖检查，统计算法沿用；项目57号高维压缩适配器留在项目中，不把该项目样本和城市控制硬编码成通用默认。OLS影响定义参考 https://www.statsmodels.org/stable/generated/statsmodels.stats.outliers_influence.OLSInfluence.html 。代码复制指纹与技能更新核验保存在技能工作目录的通用回归排除自身诊断_20261010任务中。
