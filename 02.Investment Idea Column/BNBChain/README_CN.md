# 中心化交易所空投的分配不对称性与BNB Chain生态系统

[![SSRN: 6688740](https://img.shields.io/badge/SSRN-6688740-orange.svg)](https://ssrn.com/abstract=6688740)
[![Companion: SSRN 6632838](https://img.shields.io/badge/Companion-SSRN%206632838-orange.svg)](https://ssrn.com/abstract=6632838)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Data: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

> **多语言README**: [English](./readme.md) · [한국어](./README_KR.md) · [日本語](./README_JP.md)

---

## 概述

本仓库包含对2024-2025年币安中心化交易所(CEX)空投项目(Megadrop和HODLer Airdrop)*分配不对称机制* 进行实证与理论分析的**初步工作论文、源代码、数据和图表**。

**作者**: 金浩光 (Dennis Kim), Betalabs Inc.首席执行官
**状态**: 初步工作论文, 2026年5月
**SSRN**: [Abstract ID 6688740](https://ssrn.com/abstract=6688740)
**配套论文**: [Kim, H. (2026). *The 72-Hour Shock: Token Unlock Price Impact*. SSRN 6632838](https://ssrn.com/abstract=6632838)

---

## 研究问题

> **币安26亿美元规模空投项目中,谁实际获益,以谁为代价?**

2024-2025年期间,币安通过76个以上奖励项目向BNB持有者分配了约26亿美元,占全球CEX分配的约94%。代表性项目为*Megadrop* 和*HODLer Airdrop*,广泛宣传为:*"锁仓BNB即可免费获得新项目代币"*。

本研究形式化分析对三方参与者的差异化影响:

1. **BNB持有者** — 分配代币的接收者
2. **发行基金会** — 发行新代币的项目主体
3. **BNB Chain生态系统** — 区块链平台本身

---

## 核心发现

### 1. 基金会灾难 (Foundation Disaster)

平均分配比率α = 7.3%的Megadrop代币:
- **基金会成本 ≈ FDV的30.5%** (完全稀释估值)
- **不对称比率R = 4.18** (基金会损失 : 持有者收益)
- **价值毁灭D ≈ FDV的23%** (通过市场摩擦)

### 2. 数学稳健性

在合理参数范围内 (α: 2-15%, θ: 30-60%, d: 10-90%):
- 基金会成本始终 ≥ 12.75%
- 不对称比率始终 R ≥ 1.70
- **临界分配比率α* = 5.95% (R*=5)** — Megadrop典型5-8%范围处于爆发区域

### 3. 实证验证

自助法95%置信区间分析 (N = 10,000次迭代, 样本N = 21个代币):

| 类别 | N | 平均收益率 | 95% CI |
|------|---|-----------|--------|
| Megadrop | 5 | -76.0% | [-86.4%, -65.8%] |
| HODLer | 8 | -19.5% | [-67.8%, +39.6%] |
| Launchpool | 5 | -29.8% | [-50.4%, +0.0%] |
| Direct (Memecoin) | 2 | +81.5% | [+68.0%, +95.0%] |
| **Direct (含HYPE)** | 3 | **+384.3%** | **[+68.0%, +990.0%]** |

**Cohen's d (Megadrop vs. Direct, N=21) = -1.52** (非常大的效应量, 通过Hyperliquid HYPE反事实整合获得学术可信度)

### 4. 脱钩模式 (Decoupling Pattern)

Megadrop代币下跌时,BNB Chain生态系统朝*相反方向* 增长:

| 指标 | 2025年Q1→Q3变化 |
|------|-----------------|
| BNB Chain交易量 | **+171.4%** |
| BNB Chain DeFi TVL | **+47.2%** |
| BNB Chain活跃钱包 | **+91.6%** |
| BNB价格 | $629 → $1,030 (Q4 ATH $1,369) |
| Megadrop类别市值 | **-75%** |

### 5. 三方参与者绝对货币影响 (2024-2025)

| 参与者 | 估计影响 |
|--------|----------|
| BNB持有者 (收益) | **+$14亿-20亿** |
| 发行基金会 (损失) | **-$48亿** |
| BNB Chain市值 (增长) | **+$1,040亿** |

**核心洞见**: 基金会损失明确 (持有者收益的2.84倍), 但仅占BNB Chain市值增长的4.6% — *系统层面的脱钩模式*。

### 6. 理论贡献

七个定理形式化基金会成本函数并证明:

- **定理6**: *盈亏平衡不可能性* — d* = -α/(1-α-θ) < 0 (基金会仅在价格上涨时才能达到盈亏平衡)
- **定理7**: *纳什均衡* — 立即抛售为支配策略

本研究将Allen, Berg和Lane (2023) 关于*直接空投* 的分析扩展到*中心化交易所主导(CEX-led)空投* 的新类别,应用Schelling (1960) 的协调博弈理论和Morris与Shin (1998) 的全局博弈框架。

---

## 仓库结构

```
.
├── README.md                          # 英文版
├── README_KR.md                       # 韩文版
├── README_CN.md                       # 中文版 (本文件)
├── README_JP.md                       # 日文版
├── paper/                             # 论文交付物
│   ├── Distribution_Asymmetry_CEX_Airdrops.md
│   ├── Distribution_Asymmetry_CEX_Airdrops.pdf
│   ├── Distribution_Asymmetry_CEX_Airdrops_with_figures.docx
│   └── Distribution_Asymmetry_CEX_Airdrops_with_figures.pdf
├── figures/                           # 7张出版级可视化图表
├── scripts/                           # Python源代码
├── data/                              # 输入数据 (CSV, 英文)
├── results/                           # 分析结果输出
└── docs/                              # 文档
```

---

## 可重现性

### 快速开始

```bash
# 克隆仓库
git clone https://github.com/gameworkerkim/vibe-investing.git
cd vibe-investing/02.Investment\ Idea\ Column/BNBChain

# 安装依赖
pip install pandas numpy scipy matplotlib

# 运行所有分析 (输出到results/)
cd scripts/
python correlation_analysis.py
python robustness_analysis.py
python integrated_analysis_v10.py
python pair_trading_backtest.py

# 重新生成所有图表 (输出到figures/)
for f in generate_figure*.py; do python "$f"; done
```

---

## 注意事项与局限

本研究为**初步工作论文**。明确承认以下局限:

1. **样本量**: N=21个代币 (每类N=2-8) 不足以进行完整统计推断。后续版本将扩展至N≥100
2. **因果性**: 脱钩模式仅为**观察性证据**。完整的格兰杰因果检验需要日度数据,推迟至后续版本
3. **时间分辨率**: 季度数据限制短期因果方向推断
4. **选择偏差**: 通过纳入HYPE (N=2→N=3) 部分缓解Direct类别的Memecoin偏差,但选择效应无法完全排除
5. **交易策略**: 5.4节的BTC支配率模式仅为**观察性证据**,不建议用于交易策略
6. **预测**: 本研究产生过去上市的**描述性分析**。由于CEX政策不断演变,未来代币可能呈现不同模式

---

## 引用

如果在研究中使用本代码、数据或论文,请引用:

```bibtex
@misc{kim2026distribution,
  author = {Kim, HoKwang},
  title = {Distribution Asymmetry of Centralized Exchange Airdrops and the BNB Chain Ecosystem},
  year = {2026},
  publisher = {SSRN},
  doi = {10.2139/ssrn.6688740},
  url = {https://ssrn.com/abstract=6688740},
  note = {Preliminary working paper}
}
```

---

## 许可证

本仓库使用**双许可证**:

- **源代码** (`scripts/`中的Python脚本): [MIT许可证](https://opensource.org/licenses/MIT)
- **论文、数据和图表** (`paper/`, `data/`, `figures/`): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

---

## 作者

**金浩光 (Dennis Kim)** · 独立研究员
- Betalabs Inc.首席执行官 (区块链公司孵化器)
- 前Cyworld Z首席执行官
- 前Microsoft Azure MVP (9年)
- ORCID: [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175)
- GitHub: [@gameworkerkim](https://github.com/gameworkerkim)
- Email: gameworker@gmail.com

---

## 路线图

### v1.2 (当前 — 2026年5月)
- ✅ HYPE反事实整合 (N=2→N=3)
- ✅ 自助法95% CI (N=10,000次迭代)
- ✅ 三方参与者差异化影响量化
- ✅ 7张出版级图表 + 学术标题
- ✅ 5.2节相关系数值修正
- ✅ 按正文出现顺序重新编号图表

### v2.0 (计划 — 2027)
- 样本量N≥100代币
- 通过CoinGecko/Binance API获取日度OHLCV数据
- 完整的格兰杰因果检验
- 针对选择偏差的倾向得分匹配 (PSM)
- Heckman两步估计
- 多交易所比较 (Bybit, OKX, Coinbase)
- 提交至同行评议学术期刊的LaTeX版本

---

## 相关文献

- **配套论文**: Kim, H. (2026). *The 72-Hour Shock: Token Unlock Price Impact*. SSRN 6632838.
- **代币解锁文献**: Allen, F., Gu, X., & Li, J.Y. (2023). *Crypto Tokens and Token Offerings*. Annual Review of Financial Economics.
- **协整方法论**: Engle, R.F., & Granger, C.W.J. (1987). *Co-integration and Error Correction*. Econometrica.
- **协调博弈**: Schelling, T.C. (1960). *The Strategy of Conflict*. Harvard University Press.
- **全局博弈**: Morris, S., & Shin, H.S. (1998). *Unique Equilibrium in a Model of Self-Fulfilling Currency Attacks*. American Economic Review.

---

*最后更新: 2026年5月1日*
