# 本项目交互与正式组间差异

依据知识产权法庭项目现用异质性do、主程序的正式差值保存，以及未保留检验复查02号汇总中的完整交互模型与lincom/Wald。保持原项目控制是否交互、FE、聚类、冻结分组尺度与实际样本。

## 连续M

`Y=βDID+γM+θ(DID×M)+X+FE+ε`，分别保存β、γ、θ的b/SE/p。

- M=m时政策效应：β+θm。
- DID=1时M斜率：γ+θ。
- θ检验的是M变化对政策效应的调节，不能用γ的方向代替。

```stata
reghdfe y did m did_m controls, absorb(city_id year) vce(cluster city_id)
estimates save "模型.ster", replace
* 此处按当前项目函数立即保存真实e(sample)ID。
lincom did + 1*did_m
* 立即读取r(estimate)、r(se)、r(p)、r(lb)、r(ub)。
lincom m + did_m
test did_m=0
```

这是表达式示例，变量名与参数取自当前项目，不能直接替换其真实do。lincom使用完整协方差，不能按两个SE平方和假定独立。

## 固定事前高组H

低组政策效应=β，高组=β+θ，组间差异=θ。项目未保留检验复查保留原完全交互规格、原阈值与尺度，重新估计新样本；用聚类Wald检验θ、高组lincom，保存正式差值结果。仅交互DID与完全交互控制的模型不是自动等价的分组比较，复查须保持原规格。

```stata
* 先按项目实际规格完成 pooled 估计。
lincom did
lincom did + did_h
test did_h=0
```

H固定时其主项可被城市FE吸收，要如实标注。一组显著另一组不显著不是正式组间差异；分组各自CI也不能代替差异CI。输出低/高/差异的b、SE、p、CI，及N/组支持、分组时点、FE与聚类。

## 术语与解释

用户所称“抑制性检验”若为DID×政策前连续变量，保留该术语并说明构造窗口与估计对象。政策对代理变量的影响、代理变量调节政策效应、完整中介链条是不同证据；不把一个显著交互直接写成机制已证实。

本次复查使用Wald/lincom，没有重新运行999次bdiff；不要沿用另一版结果的检验方法或p值。
