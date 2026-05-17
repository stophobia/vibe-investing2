# ARDS:自适应衰退-防御策略 (中文版)

> **AMQS 的镜像对称策略** — 以 *经济衰退概率综合指数 (Recession Probability Composite)* 替代 4-Factor Momentum Composite,以 *逆周期相对强度 (Counter-Cyclical Strength)* 替代 Pullback-in-Uptrend 维度。运行 *经济衰退对冲 ETF + 防御股 + 战术性反向 ETF 的动态组合*。完整继承 AMQS 的 5 维度 100 分评分体系、-12% 止损规则、周度再平衡框架。

## 使用方法

1. *完整复制*下方提示词块
2. *直接粘贴*至 Claude / GPT-5 / Gemini / DeepSeek 等前沿 LLM
3. LLM 将自动生成 *4-Tier Universe 全部标的的评分、信号、权重与回测*

> **本提示词是 [AMQS-M7](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Adaptive%20Momentum%20Quant%20Strategy%20(AMQS)%20for%20M7/prompts/AMQS_M7_kr.MD) 的 *对称对冲策略*。**核心差异:(1) Universe 从 M7 → *4-Tier 防御型 Universe*,(2) D1 维度从动量 → *衰退概率*,(3) DIP_BUY 信号 → *FLIGHT_TO_QUALITY (奔向品质) 信号*,(4) 宏观体制从 3 阶段 → *4 阶段 (扩张 / 周期末期 / 衰退预警 / 衰退)*。

---

## 提示词 (中文版)

```
[角色设定]
您是全球顶级宏观对冲基金的投资组合经理与宏观风险负责人,拥有 16 年经济周期分析、Quality 因子、防御股 (Defensive Equity)、衰退对冲资产配置的从业经验。您的决策体系基于 'Adaptive Recession-Defensive Strategy (ARDS)' 模型,整合多维度经济衰退信号、Quality/低波动因子暴露、逆周期相对强度、波动率调整后的仓位规模、4 阶段宏观体制过滤器,以输出 *周度再平衡的防御型动态组合收益*。

当前日期为 2026 年 5 月 17 日。

[分析标的 — 4-Tier 防御型 Universe]

Tier 1:防御性行业 ETF (Always-On 核心,5 只)
   XLP (必需消费), XLV (医疗保健), XLU (公用事业), VPU (Vanguard 公用事业), VHT (Vanguard 医疗)

Tier 2:经济衰退对冲 ETF (Always-On 对冲,6 只)
   TLT (20+ 年期国债), IEF (7-10 年期国债), SHV (短期国债), GLD (黄金), IAU (黄金), BIL (1-3 月期短债)

Tier 3:个股防御股 (Quality Defensives,10 只)
   BRK-B (伯克希尔), WMT (沃尔玛), COST (好市多), JNJ (强生), KO (可口可乐), PG (宝洁), PEP (百事), NEE (NextEra 能源), VZ (Verizon), ABBV (艾伯维)

Tier 4:战术性反向 / 波动率 ETF (周期末期/衰退专用,4 只)
   SH (1x 做空标普), PSQ (1x 做空纳指), VIXY (VIX 短期), DOG (1x 做空道指)
   ※ 该 Tier 仅在宏观体制为周期末期 (Late-Cycle) 或更糟时激活。扩张期 (Expansion) 强制权重为 0%。

Universe 总计:25 只标的。请为每只标的生成评分、信号、权重。

本策略为 *4-Tier 防御型动态组合策略*。请同时定义以下 5 个要素:
1. 当前日期 25 只标的完整评分表 (快照)
2. 经济衰退概率计算公式 (5-Factor Recession Composite)
3. *逆周期相对强度 (Counter-Cyclical Strength)* 评分公式
4. 周度再平衡规则 (入场/持有/退出)
5. 4 阶段宏观体制过滤器 (扩张 / 周期末期 / 衰退预警 / 衰退)

[衰退信号定义 — 5-Factor Recession Composite,D1 维度核心]

任一时点的衰退概率为以下 5 个信号的加权之和:

成分 A:收益率曲线倒挂 (权重 30%)
   - 10Y-3M 利差 (纽约联储衰退概率模型标准)
   - 10Y-2Y 利差 (辅助指标)
   - 同时反映倒挂深度 (基点) + 持续时间 (月)
   - "倒挂解除后 6-18 个月"窗口期赋予衰退概率加分

成分 B:Sahm Rule (权重 25%)
   - 失业率 3 个月移动平均 - 此前 12 个月最低值 ≥ 0.50 个百分点 → 衰退触发
   - 0.30-0.50 个百分点区间:警告
   - ≥ 0.50 个百分点:激活

成分 C:ISM 制造业 PMI (权重 15%)
   - PMI < 50:收缩 (评分加分)
   - PMI < 45:衰退临近
   - 是否连续 3 个月下滑

成分 D:领先经济指标 (LEI,权重 15%)
   - 经济咨商局 LEI 6 个月变动率
   - ≤ -4% (年化) → 衰退信号
   - 各成分 (利差、初请失业金、建筑许可等) 贡献度分析

成分 E:信用利差与金融条件 (权重 15%)
   - 高收益债 OAS (BofA US HY Master II)
   - ≥ 400bp:警告,≥ 500bp:衰退临近
   - 芝加哥联储 NFCI (Adjusted) 转正

5-Factor Recession Composite = 0.30·A + 0.25·B + 0.15·C + 0.15·D + 0.15·E
* 各成分先归一化到 0-100 分,再加权求和

[逆周期相对强度 (Counter-Cyclical Strength) — ARDS 的核心差异化]

前提:*真正的防御股在市场下跌日表现出色*。单纯的低 Beta 策略只看"低波动",但 *仅在市场下跌日选择性走强的标的* 才是真正能对冲衰退风险的资产。

信号激活条件 (须同时满足 4 项,否则评分为 0):
   (i)  近 60 个交易日内 SPX 下跌日 ≥ 15 个 (样本窗口有效性)
   (ii) 1 年期 Beta ≤ 0.75  ← 结构性低 Beta
   (iii) 下行捕获率 (Downside Capture) < 70%  ← 市场下跌日跟跌弱
   (iv) 上行捕获率 (Upside Capture) > 40%  ← 市场上涨日不完全脱钩

信号强度:
   基础 = (1 - Downside Capture / 100) × (1 + Sortino Ratio × 0.5)
   + SPX 跌幅 ≥ -2% 当日,本标的收益为正的频次加分 (60 日窗口)
   + 高收益债 OAS 扩张区间 (近 30 日 OAS 走阔 50bp 以上) 中表现强势者,额外加分

z-score 归一化后转换为 100 分制。

(注:Tier 4 反向/VIX ETF 在本维度自动获得 100 分 — 因结构性逆相关。)

[100 分综合评分 — 5 个维度]

每只标的总分为 5 个维度的加权和:

1. 衰退概率适配度 (权重 30%)
   - 当 5-Factor Recession Composite ≥ 50% 时,本维度权重自动上调 +10 个百分点 (从其他维度等额扣除)
   - Tier 1 (防御性行业 ETF):综合指数越高 → 本维度得分越高
   - Tier 2 (国债/黄金):同向,但 TLT 额外反映降息预期
   - Tier 3 (个股防御股):综合指数低 → 本维度得分降低 (牛市中防御股跑输)
   - Tier 4 (反向):综合指数 < 60% 时本维度得分 0 (= 禁止入场)

2. **逆周期相对强度 (权重 20%,NEW)**
   - 上述 Counter-Cyclical Strength 评分
   - 激活条件未全部满足时评分为 0 (双重安全机制)

3. 防御性 Quality 因子 (权重 20%)
   - ROE 稳定性:5 年 ROE 标准差 < 5 个百分点
   - 盈利稳定性:5 年 EPS 变异系数
   - 股息稳定性:10 年无削减 + 5 年连续增派
   - 自由现金流收益率 (FCF Yield):≥ 5% 加分
   - 资产负债率 (D/E) ≤ 1.0

4. 波动率与回撤保护 (权重 20%)
   - 60 日已实现波动率 (越低评分越高)
   - 此前 24 个月最大回撤 ≤ 15% (包含历史衰退期)
   - Sortino Ratio (基于下行偏差)
   - 200 日均线之上 (但 Tier 4 反向 — 跌破 200MA 时加分)

5. 宏观环境适配度 (权重 10%)
   - 美国 10 年期国债收益率趋势 (下行 = TLT/公用事业有利;上行 = 反向 ETF 有利)
   - VIX 指数水位 (≥ 25 时全体防御资产加分)
   - 美元指数 (DXY) 趋势 (与黄金负相关)
   - 近 30 日 SPX 已实现波动率趋势 (扩大时本维度加分)

总分 = 0.30·D1 + 0.20·D2 + 0.20·D3 + 0.20·D4 + 0.10·D5

[再平衡规则 — 继承 AMQS 框架,适配 ARDS Universe]

入场 (BUY) / 核心仓位 (CORE) 条件:
- 总分 ≥ 75 → CORE 仓位 (Tier 1:最大 20%, Tier 2:最大 25%, Tier 3:最大 10%, Tier 4:最大 8%)
- 当前宏观体制必须激活对应 Tier
- 全部预过滤条件通过

持有 (HOLD) 条件:
- 总分 60-75 → SATELLITE 仓位 (Tier 1: 8-15%, Tier 2: 10-18%, Tier 3: 5-8%, Tier 4: 3-5%)
- 总分 45-60 → TACTICAL 仓位 (3-5%,严格止损)
- 标的级止损线未触发

FLIGHT_TO_QUALITY 特殊信号 (本策略核心):
- Recession Composite ≥ 60% 且 Counter-Cyclical Strength ≥ 70 分
- 满足条件的 Tier 1 ETF 或 Tier 3 个股防御股,在基础权重上加 +3~7 个百分点
- Tier 2 (TLT, GLD) 也可能触发 — 此情况下视为正式 risk-off 入场信号

退出 (EXIT) 条件 — 满足任一即触发:
- 标的级止损线触发 (-10% from rebalance entry,较 AMQS 的 -12% 更紧)
- Tier 4:-15% 止损 + 持有 4 周以上自动清仓 (禁止长期持有)
- 宏观体制回归扩张期 → 清仓全部 Tier 4
- 宏观体制进入衰退期 → 清仓 50%+ 的 Tier 3 个股,资金重新分配至 Tier 1/2

再平衡周期:
- 周度:每周五收盘价计算信号 → 周一开盘执行
- 日度:仅止损线 + 宏观体制变化触发器作日度监控
- 月度:5-Factor Recession Composite 全面重算 (月初第一个交易日)

[预过滤规则 — ARDS 专属]

不满足以下条件的标的自动剔除:
- 市值 ≥ 100 亿美元 (Tier 1/3);Tier 2/4 的 ETF AUM ≥ 10 亿美元
- 30 日日均成交额 ≥ 5000 万美元
- 60 日已实现波动率 ≤ 35% (Tier 1/3) / ≤ 60% (Tier 2) / ≤ 120% (Tier 4 — VIXY 例外)
- Beta ≤ 1.0 (Tier 1/3) / 负 Beta (Tier 4)
- 此前 12 个月内无股息削减 (仅适用于 Tier 3)

[宏观体制过滤器 — 4 阶段,ARDS 专属]

阶段 1:扩张期 (Expansion,防御权重 30% / 风险资产权重 70% — Tier 4 停用)
- 10Y-3M > 100bp (正常曲线)
- Sahm Rule < 0.20 个百分点
- ISM PMI > 52
- LEI 6 个月变动率 > 0%
- HY OAS < 350bp
- → Tier 1: 20%, Tier 2: 10%, Tier 3: 0%, Tier 4: 0%,风险资产 70% (外部策略或 SPY)

阶段 2:周期末期 (Late-Cycle,防御权重 55% — Tier 4 部分激活)
- 上述条件中 2 项以上恶化 (如收益率曲线扁平化 + LEI 走缓)
- VIX 平均 18-23
- → Tier 1: 25%, Tier 2: 20%, Tier 3: 10%, Tier 4: 0~5% (优先 SH 对冲)

阶段 3:衰退预警 (Recession-Warning,防御权重 80% — Tier 4 完全激活)
- 5-Factor Recession Composite ≥ 50%
- 收益率曲线倒挂 + Sahm Rule > 0.30 个百分点
- ISM < 50 (连续 2 个月)
- HY OAS > 400bp
- → Tier 1: 30%, Tier 2: 30%, Tier 3: 15%, Tier 4: 5~10%

阶段 4:衰退 (Recession,防御权重 100% — Tier 4 最大激活)
- 5-Factor Recession Composite ≥ 70%
- Sahm Rule 0.50 个百分点触发器激活
- 或近 5 个交易日 SPX 跌幅 ≥ 8%
- → Tier 1: 35%, Tier 2: 40%, Tier 3: 10%, Tier 4: 15% (以 PSQ + VIXY 为核心)

[仓位规模]

默认:Tier 感知 score-tilted 配置
- 各 Tier 的最大/最小权重按上述规则应用
- 各 Tier 内部:weight_i = base × (1 + 1.5 × (总分_i - 65) / 30)
- 上下限剪裁:Tier 1 (5-20%), Tier 2 (5-25%), Tier 3 (3-10%), Tier 4 (2-15%)
- 总和 = invested_fraction (按 Phase 指引)

FLIGHT_TO_QUALITY 标的加 +3~7 个百分点 (从其他标的等额扣除)

(可选) Risk Parity 仓位:
- 权重 = (1/已实现波动率) / Σ(1/已实现波动率)
- 对 TLT (高波动债券) 设绝对权重上限

(可选) Convexity 仓位 (仅 Tier 4):
- VIXY:contango 损耗 (月 5-8%) → 最大持有 30 日
- 反向 ETF (SH/PSQ):daily reset → 跟踪长期持有的 path dependency 损耗,触发后自动清仓

[数据处理原则]
请提供反映 2023 年 1 月 ~ 2026 年 5 月已知价格/财务数据 + 宏观事件 (2024 年 8 月日元套利交易 unwind、2025 年 1 月 DeepSeek 冲击、2025 年 4 月 Liberation Day 关税、2025 年下半年降息周期、2026 年 4 月 CPI 3.8% 意外、2026 年 5 月霍尔木兹海峡封锁等) 的回测模拟结果。估算值标注 ±5% 误差区间。报告扣除交易成本 0.03% (ETF) / 0.05% (个股) + 滑点 0.05% 后的 net 收益。

[输出要求]

第一部分:当前日期 (2026.05.17) 25 只标的评分表 (按 Tier 分 4 张表)
| 代码 | Tier | 5-Factor Recession 分 | Counter-Cyclical 分 | 各维度分 (D1/D2/D3/D4/D5) | 总分 | 信号 | 推荐权重 | 止损线 |

包含以下列:
- Beta (1Y), 下行/上行捕获率, Sortino Ratio
- 60 日波动率, 24M 最大回撤
- 200MA 上/下
- 股息收益率 (仅 Tier 3)
- 信号:CORE / SATELLITE / TACTICAL / FLIGHT_TO_QUALITY / REDUCE / EXIT / EXCLUDED
- 入场依据 (FLIGHT_TO_QUALITY 须注明市场下跌日强势模式)
- 止损线 (entry × 0.90, Tier 4 为 × 0.85)

宏观体制决策结果:
- 当前 Phase:扩张期 / 周期末期 / 衰退预警 / 衰退
- 当前 5-Factor Recession Composite 数值 + 各成分得分
- 依据:10Y-3M 利差、当前 Sahm Rule、ISM PMI、LEI 6M、HY OAS

第二部分:回测结果 (2023-01-03 ~ 2026-04-30)
- 累计收益曲线:ARDS vs SPY vs 60/40 (VTI + AGG) vs 简易防御篮子 (XLP+XLV+XLU 等权) vs TLT 单一持有
- 核心统计:总收益、CAGR、波动率、最大回撤、Sharpe Ratio、Sortino Ratio、换手率
- 各宏观事件表现:23 年 SVB 危机、24 年 8 月日元套息 unwind、25 年 1 月 DeepSeek 冲击、25 年 4 月 Liberation Day、25 年 9-12 月降息行情、26 年 4-5 月通胀再加速
- *FLIGHT_TO_QUALITY 信号的 alpha 贡献度* 单独分析 (无该信号 vs 有该信号对比)
- *各 Phase 的 outperformance 拆解*:Phase 1 (预期跑输) / Phase 3-4 (预期跑赢) 的 alpha 分别度量
- 熊市期间跑赢分析 (仅限 SPX -10% 以上区间)

第三部分:风险分析与局限
- ARDS *机会成本*:Phase 1 牛市中预期跑输 SPY 约 4-8 个百分点/年
- *假衰退信号陷阱 (BEAR_TRAP)*:2022-23 年收益率曲线倒挂后 18 个月 no-landing 案例
- Tier 4 (Inverse/VIXY) *contango 损耗*:VIXY 月度 5-8% 时间价值衰减,SH/PSQ daily reset path dependency
- 利率上行期 TLT 的久期损失 (2022 年 -31%)
- 海外投资者税务影响 (假设换手率 ~80-120%)
- *防御股的估值风险*:bond-proxy 属性 → 利率急升时同步下跌 (2022 年 XLU -1%, XLP -3%)

[免责声明]
本分析仅为教育与信息目的,*防御型策略在牛市中会产生机会成本,在假衰退信号 (false recession signal) 中会录得最大跑输*。*FLIGHT_TO_QUALITY 信号在真正的衰退入场期提供非对称 alpha,但在单纯的市场回调中可能成为 whipsaw 损失的源头* (例如 2022-23 年收益率曲线倒挂后 no-landing 持续 18 个月,防御股策略跑输 SPX -15 个百分点)。*Tier 4 反向/波动率 ETF 因结构性时间价值衰减 (contango, daily reset),长期持有趋近 100% 损失* — 务必严格执行 30 日清仓规则。实际投资决策须结合个人判断与专业咨询。过去回测结果不构成未来收益保证。

```

---

## 提示词结构说明

### 5 维度 100 分评分 (与 AMQS 对称)

| 维度 | AMQS-M7 (动量型) | **ARDS (防御型)** | 含义 |
| --- | --- | --- | --- |
| D1. 核心宏观信号 | 35% (动量) | **30% (Recession Composite)** | 5-Factor 衰退概率 |
| D2. 非对称入场信号 | 15% (Pullback-in-Uptrend) | **20% (Counter-Cyclical Strength)** | 市场下跌日相对强度 |
| D3. 基本面品质 | 25% (加速度) | **20% (Defensive Quality)** | ROE/EPS/股息稳定性 |
| D4. 波动率调整 | 15% (动量 alpha) | **20% (Downside Protection)** | MDD/Sortino |
| D5. 宏观环境 | 10% | **10%** | VIX/利率/DXY |

### 4-Tier Universe 的结构含义

| Tier | 资产类别 | 活跃阶段 | 角色 |
| --- | --- | --- | --- |
| Tier 1 | 防御性行业 ETF | 全阶段 | Always-On 核心防御 |
| Tier 2 | 国债/黄金 ETF | 全阶段 (权重浮动) | 双重对冲 |
| Tier 3 | 个股 Quality 防御股 | Phase 2-3 为主 | Alpha 增厚 |
| Tier 4 | 反向/VIX | Phase 2-4 限定 | 正式对冲 (时间受限) |

### 4 阶段宏观体制 (AMQS 的 3 阶段 → ARDS 的 4 阶段)

| Phase | 5F Composite | 防御权重 | Tier 4 激活 |
| --- | --- | --- | --- |
| 1. 扩张期 | < 25% | 30% | ❌ |
| 2. 周期末期 | 25-50% | 55% | 部分 (~5%) |
| 3. 衰退预警 | 50-70% | 80% | 激活 (5-10%) |
| 4. 衰退 | > 70% | 100% | 最大 (15%) |

---

## 使用建议

### 各信号推荐权重 (以 Phase 3 为基准)

| 信号 | 总分区间 | Tier 1 推荐 | Tier 2 推荐 | Tier 3 推荐 | Tier 4 推荐 |
| --- | --- | --- | --- | --- | --- |
| **CORE** | 75+ | 15-20% | 18-25% | 8-10% | 5-8% |
| **SATELLITE** | 60-75 | 8-15% | 10-18% | 5-8% | 3-5% |
| **FLIGHT_TO_QUALITY** | (浮动) | 基础 +3~7ppt | 基础 +5ppt | 基础 +5ppt | — |
| **TACTICAL** | 45-60 | 3-5% | 3-5% | 3-5% | 2-3% |
| **REDUCE** | <45 | <3% | <3% | <3% | 0% |
| **EXIT** | — | 0% | 0% | 0% | 0% |

### 组合构建注意事项

- **与 AMQS-M7 配对**:ARDS 是 AMQS-M7 的 *对称对冲*。两者 50:50 并行运行可获得市场 Beta ~0.5 + 衰退入场期 alpha 双重捕获
- **税收感知的 Tier 选择**:Tier 2 (TLT, IEF, BIL) 换手率低 (长期持有) → 税收拖累最小;Tier 4 换手率高,但本就为波动率驱动
- **久期意识**:TLT 久期 17+ 年 — 利率变动 100bp = 约 17% 价格冲击。须据此设定仓位上限
- **海外投资者考虑**:美股股息预扣税约 15-30% (视税收协定而定)。Tier 1 (XLP 2.5%, XLU 2.8%) 与 Tier 3 (KO 3%, VZ 6.5%) 股息均为预扣前数据

---

## 风险警示

- 上述输出为 *LLM 模拟,仅供教育和研究用途*,非投资建议
- *防御型策略在牛市中机会成本极高*:Phase 1 中预期跑输 SPY 约 4-8 个百分点/年
- **BEAR_TRAP 信号陷阱**:2022-23 年收益率曲线倒挂后 18 个月 no-landing → 防御型策略大幅跑输的实战案例
- **Tier 4 的时间价值衰减**:VIXY 月度 5-8%,SH/PSQ daily reset path dependency。*务必严格执行 30 日清仓规则*
- **利率上行期债券久期风险**:2022 年 TLT -31%, XLU -1% (虽名为"防御"仍亏损)
- 回测反映 *2023-2026 周期末期环境*;1995-99 等强势牛市中可能录得大幅跑输

---

## 作者信息

**系列**:vibe-investing — ARDS 新增模块 (AMQS 的对称对冲策略)
**关联策略**:
- [AMQS 原版 (NASDAQ-100 + AI Value Chain)](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Adaptive%20Momentum%20Quant%20Strategy%20(AMQS)/Momentum%20Quant%20Prompt%20kr.MD)
- [AMQS-M7](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Adaptive%20Momentum%20Quant%20Strategy%20(AMQS)%20for%20M7/prompts/AMQS_M7_kr.MD)
- **ARDS** — 衰退-防御 4-Tier 策略 (*本提示词*)

**作者**:金浩光 (Dennis Kim / HoKwang Kim / 김호광)
- Betalabs Inc. CEO, 独立研究员
- GitHub: [@gameworkerkim](https://github.com/gameworkerkim) · ORCID: [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175)

**许可证**:MIT

---

> *"牛市中,防御是一种税。熊市中,防御是氧气。艺术在于,识别空气何时变稀薄。"*
