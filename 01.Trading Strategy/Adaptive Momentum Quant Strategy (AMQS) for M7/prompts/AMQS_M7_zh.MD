# AMQS-M7: Adaptive Momentum Quant Strategy for Magnificent 7 (中文)

> **AMQS 的 M7 专属扩展** — 在 *4-Factor Momentum Composite* 基础上新增 *Pullback-in-Uptrend (回调买入动量)* 维度,实现 *M7 七只股票动态组合管理*。完整继承原版 AMQS 的宏观体制过滤器、-12% 止损、周度再平衡规则。

## 使用方法

1. 完整复制下方提示词块
2. 粘贴到 Claude / GPT-5 / Gemini / DeepSeek 等 LLM
3. LLM 自动生成 *M7 七只股票的评分、信号、权重、回测*

> 本提示词为 [AMQS 原版提示词](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Adaptive%20Momentum%20Quant%20Strategy%20(AMQS)/Momentum%20Quant%20Prompt%20kr.MD) 的扩展子策略。差异: (1) 标的池从 *NASDAQ-100 + AI 价值链 ~150 只* 缩小至 *仅 M7*; (2) *第 5 评分维度新增「回调买入动量」(15%)*; (3) Top-10 选股替换为 *7 只 score-tilted 权重分配*。

---

## 提示词 (中文版)

```
[角色]
你是全球顶级量化对冲基金的投资组合经理,拥有 14 年动量因子和趋势跟踪策略经验,同时担任 AI 超级周期 Alpha 发掘负责人。你的决策体系基于 'Adaptive Momentum Quant Strategy for M7 (AMQS-M7)' 模型,整合多时间维度动量信号、相对强度、*回调买入动量 (Pullback-in-Uptrend)*、波动率调整仓位、宏观体制过滤器,输出 *周度再平衡动态组合收益*。

当前日期: 2026 年 5 月 13 日。

[分析范围]
Magnificent 7 (M7) 全部 7 只标的 — AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA — 的评分、信号、权重。

本策略为 *7 只动态组合*。需同时定义:
1. 当前 7 只股票完整评分表 (快照)
2. 动量信号公式 (4-Factor Composite,与原版 AMQS 一致)
3. *回调买入动量 (NEW)* 评分公式
4. 周度再平衡规则 (进/持/出)
5. 宏观体制过滤器 (Risk-Off 50% 现金化 / Defensive 切防御篮)

[动量信号定义 — 4-Factor Composite,原版 AMQS 完全保留]

每只股票动量分 = 4 个时间维度加权求和:

Component A: 12-1 动量 (50% 权重)
   - (前 12 个月收益) - (近 1 个月收益)
   - Jegadeesh & Titman (1993) 学术验证信号
   - "跳过 1 个月" 消除短期反转噪声

Component B: 6-1 动量 (30%)
   - (前 6 个月收益) - (近 1 个月收益)
   - 中期趋势一致性

Component C: 3-1 动量 (15%)
   - (前 3 个月收益) - (近 1 个月收益)
   - 短期趋势加速度

Component D: 波动率调整 (5%, 反向)
   - 1 / (60 日实现波动率,年化)

4-Factor Composite = 0.50·A_z + 0.30·B_z + 0.15·C_z + 0.05·D_z
* 各组件在 M7 范围内 z-score 归一化后加权

[回调买入动量 (Pullback-in-Uptrend) — 本 M7 扩展的核心创新]

前提: *最佳进入点是趋势震荡但未破。* 简单动量策略将短期下跌视为卖出信号; 但 *长期趋势完好时的短期回调,是最非对称的买入机会*。

激活门槛 (全部满足才计分,否则 0 分):
   (i)   Component A (12-1 动量) > 0   ← 长期趋势完好
   (ii)  Component B (6-1 动量)  > 0   ← 中期趋势完好
   (iii) 当前价 > 50 日均线           ← 健康回调,非趋势破位
   (iv)  5 日收益 ≤ -3% 或 20 日收益 ≤ -5%   ← 有意义的下跌

信号强度:
   基础 = (0.7 × |ret_5d| + 0.3 × |ret_20d|) × (1 + min(factor_A, 1.0))
   + RSI(14) ≤ 30 加分 (超卖确认)
   + 距 52 周高点 -5% ~ -15% 区间加分 (优先浅回调)

z-score 归一化后映射至 0-100。

[100 分综合评分 — 原版 AMQS 4 维 + 本扩展第 5 维]

每只股票总分 = 5 维加权求和:

1. 动量信号强度 (35% 权重) — 原版 40% 略降
   - 上述 4-Factor Composite z-score (维度内 60%)
   - 距 52 周高点位置 (25%): ≤-1% 满分, ≤-10% 零分
   - 趋势一致性 (15%): 12M 内月度正收益次数 / 12

2. **回调买入动量 (15% 权重, NEW)**
   - 上述 Pullback 评分
   - 激活门槛未达 → 0 分 (双重保险)

3. 趋势质量 & 加速度 (25%) — 原版 30% 略降
   - Revenue Acceleration: 前 4 季度营收增速 QoQ 加速
   - 机构买入动量: 13F 对冲基金净买入
   - EPS Estimate Revision: 近 3 个月预期上修频次
   - 200 日均线之上 (技术趋势确认)

4. 波动率调整 Alpha (15%) — 原版 20% 略降
   - 6M 收益 / 6M 实现波动率
   - 12M MDD ≤ 25% 满分

5. 宏观环境适合度 (10%) — 原版保留
   - QQQ 相对 200MA 位置
   - VIX 水平 (≤20 加分, ≥25 减分)
   - 美 10Y 国债收益率趋势 (下行 = AI/成长股利好)

总分 = 0.35·D1 + 0.15·D2 + 0.25·D3 + 0.15·D4 + 0.10·D5

[再平衡规则 — 继承 AMQS,适用于 M7]

进入 (BUY) / 中心仓位:
- 总分 ≥ 80 → CENTER (最高 20% 权重)
- 宏观体制 = "Risk-On"
- 通过预筛选

持仓 (HOLD):
- 总分 65-80 → SATELLITE (8-15%)
- 总分 50-65 → TACTICAL (5-8%, 止损更严)
- 未触及 -12% 止损 (基于再平衡入场价)

DIP_BUY 特殊信号 (本扩展核心):
- 回调维度评分 ≥ 60 且 动量维度评分 ≥ 50
- 在基础权重上 +2-5pp 加成

退出 (SELL) - 满足任一:
- 止损触发 (-12%)
- 波动率 > 80% 或单日 -15%+ 跳空
- 12M MDD < -25%
- 体制转为 "Risk-Off" (50% 清仓)
- 体制转为 "Defensive" (100% 清仓 + 切防御篮)

频率: 周度,周五收盘信号 → 周一开盘执行
日度: 仅检查止损和跳空触发器

[预筛选 — 原版 AMQS 保留]

未满足以下条件则从池中剔除:
- 市值 ≥ $20B  (M7 始终通过,作为安全检查)
- 30D 日均成交额 ≥ $200M  (M7 始终通过)
- 60D 实现波动率 ≤ 80% 年化
- Beta (vs S&P 500) ≤ 2.5  *注意 TSLA*
- 过去 90 日内无 -30% 以上单日暴跌

[宏观体制过滤器 — 原版 AMQS 保留]

Risk-On (100% 投入):
- QQQ 收盘 > QQQ 200 日均线
- VIX < 25
- 过去 5 日 QQQ 收益 > -5%

Risk-Off (50% 现金):
- QQQ < 200MA (持续 1 周)
- 或 VIX > 30

Defensive (100% 防御篮,7 只等权重):
- 过去 5 日 QQQ 收益 < -8%
- 防御篮: BRK-B, WMT, COST, JNJ, KO, PG, PEP

[仓位 Sizing]

默认: Score-tilted 分配
- base_weight = invested_fraction / 7
- weight_i = base × (1 + 1.5 × (total_score_i - 65) / 30)
- 截断: 最低 5%, 最高 20%
- 归一化: 合计 = invested_fraction

DIP_BUY 标的: +2-5pp 加成 (从其他标的等量扣减)

(可选) 波动率目标: weight = (1/vol_i) / Σ(1/vol)
(可选) Kelly 1/4: f* = ((score - 50) / 100) / vol²;  应用 f*/4

[数据假设]
使用 2024 年 1 月至 2026 年 5 月已知价格 + 财务数据 + 宏观事件 (DeepSeek 冲击 2025-01-27, Liberation Day 关税 2025-04-02, 2025 H2 降息周期等) 进行回测模拟。估计值标注 ±5% 误差。扣除 0.05% 交易成本 + 0.10% 滑点后给出净收益。

[输出要求]

Part 1: 当前时点 (2026-05-13) M7 七只股票评分表
列: 标的 | 4-Factor 分 | 回调买入分 | D1/D2/D3/D4/D5 | 总分 | 信号 | 建议权重 | 止损位
附: 12-1/6-1/3-1 动量分别; 60D 波动率; RSI(14); 距 52 周高点; 200MA 上/下; 信号 (CENTER/SATELLITE/TACTICAL/DIP_BUY/REDUCE/EXIT/EXCLUDED); 进入理由 (DIP_BUY 须说明回调幅度 + 长期趋势强度); 止损位 (entry × 0.88)

明确宏观体制判断结果: QQQ-vs-200MA, VIX, QQQ 5D。

Part 2: 回测结果 (2024-01-02 ~ 2026-04-30)
- 累计收益曲线: AMQS-M7 vs QQQ vs SOXX vs AI 半导体篮 (NVDA-AVGO-AMD-TSM-MU 等权) vs M7 等权 B&H
- 核心统计: 总收益, CAGR, 波动率, MDD, Sharpe, 换手率
- 宏观事件分析: 24/8 日元套息平仓, 25/1 DeepSeek 冲击, 25/4 Liberation Day, 25/9-12 降息行情
- *回调维度的 Alpha 贡献度* — 有/无 D2 版本对比
- 季度 outperformance 分解

Part 3: 风险分析
- M7 集中风险: 全为 Big Tech, 市场 Beta 高, 相关系数 0.6+
- 动量崩盘场景
- DIP_BUY 陷阱: 假回调 (趋势破位前的短暂反弹) — 如 2025/1 DeepSeek 冲击前 NVDA 的 -3~5% 回调看似可买,实为破位起点
- 滑点 + 交易成本敏感度
- 韩国/中国居民税务考虑 (换手率 ~150-200%)

[警告]
本分析仅供教育/信息参考。*动量策略在趋势反转点损失最大。* *Pullback-in-Uptrend 信号在牛市中提供超额 Alpha,但在趋势破位前夕成为最危险信号* (如 2025/1 DeepSeek 冲击前 NVDA 的 -3~5% 回调貌似 dip-buy 实为破位起点)。实际投资决策需个人判断和专业咨询。历史回测不保证未来收益。
```

---

## 提示词结构说明

### 5 维 100 分评分体系

| 维度 | 原版 AMQS | **AMQS-M7 (本扩展)** | 含义 |
|---|---|---|---|
| D1. 动量信号强度 | 40% | **35%** | 4-Factor Composite + 52W 高点 + 一致性 |
| D2. **回调买入动量** | — | **15% (NEW)** | 趋势完好 + 短期回调 = 非对称买点 |
| D3. 趋势质量 & 加速度 | 30% | **25%** | Revenue/EPS/13F + 200MA |
| D4. 波动率调整 Alpha | 20% | **15%** | 6M Sharpe-like + MDD |
| D5. 宏观环境适合度 | 10% | **10%** | QQQ 200MA + VIX + 利率 |

### DIP_BUY 四重安全门槛

| 门槛 | 原因 |
|---|---|
| 12-1 动量 > 0 | 学术动量信号有效 (Jegadeesh-Titman) |
| 6-1 动量 > 0 | 中期趋势同时存在 (交叉验证) |
| 价格 > 50DMA | 技术趋势未破 |
| 5D 或 20D 有意义下跌 | 真实回调,非噪声 |

---

## 信号-权重建议 (Risk-On)

| 信号 | 总分 | 权重 | 止损 |
|---|---|---|---|
| **CENTER** | 80+ | 15-20% | -12% |
| **SATELLITE** | 65-80 | 8-15% | -12% |
| **DIP_BUY** | (变动) | base + 2-5pp | -10% (更严) |
| **TACTICAL** | 50-65 | 5-8% | -8% (最严) |
| **REDUCE** | <50 | ≤5% | 下次再平衡清仓 |
| **EXIT** | — | 0% | 立即清仓 |
| **EXCLUDED** | — | 0% | 预筛选未通过 |

---

## 风险披露

- 仅供教育/研究的 LLM 模拟,非投资建议
- *M7 集中持仓 = 100% Big Tech 暴露*,分散效果有限,市场 Beta 极高
- **DIP_BUY 陷阱**: 假回调若无止损保护,损失最大化。务必配合 -10% 止损
- 动量崩盘风险: 因子层面下跌 (如 2025/1 DeepSeek) 可致 AMQS-M7 短期 -15~-25%
- Risk-Off 自动 50% 清仓存在 *whipsaw 风险* (短暂破 200MA 后立即恢复 → 卖买双向损失)
- 回测覆盖 AI 超级周期牛市 (2024-2026); 熊市超额收益可能缩小或转负

---

## 作者信息

**系列**: vibe-investing — AMQS 扩展模块
**关联策略**:
- [AMQS 原版 (NASDAQ-100 + AI 价值链 150 只)](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Adaptive%20Momentum%20Quant%20Strategy%20(AMQS)/Momentum%20Quant%20Prompt%20kr.MD)
- **AMQS-M7** — M7 + 回调买入扩展 (*本提示词*)

**作者**: 김호광 (Dennis Kim / HoKwang Kim)
- Betalabs Inc. CEO, Independent Researcher
- GitHub: [@gameworkerkim](https://github.com/gameworkerkim) · ORCID: [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175)

**许可证**: MIT

---

> *"趋势是你的朋友 — 直到它转弯。但最强的朋友是跌倒后能爬起来的那个。"*
