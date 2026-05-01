# 中央集権型取引所エアドロップの分配非対称性とBNB Chainエコシステム

[![SSRN: 6688740](https://img.shields.io/badge/SSRN-6688740-orange.svg)](https://ssrn.com/abstract=6688740)
[![Companion: SSRN 6632838](https://img.shields.io/badge/Companion-SSRN%206632838-orange.svg)](https://ssrn.com/abstract=6632838)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Data: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

> **多言語README**: [English](./readme.md) · [한국어](./README_KR.md) · [中文](./README_CN.md)

---

## 概要

本リポジトリは、2024-2025年のBinance中央集権型取引所(CEX)エアドロッププログラム(MegadropおよびHODLer Airdrop)の*分配非対称メカニズム* に関する実証的・理論的研究の**予備ワーキングペーパー、ソースコード、データ、図表** を含みます。

**著者**: 金浩光 (Dennis Kim), Betalabs Inc.最高経営責任者
**ステータス**: 予備ワーキングペーパー, 2026年5月
**SSRN**: [Abstract ID 6688740](https://ssrn.com/abstract=6688740)
**関連論文**: [Kim, H. (2026). *The 72-Hour Shock: Token Unlock Price Impact*. SSRN 6632838](https://ssrn.com/abstract=6632838)

---

## 研究課題

> **Binanceの26億ドル規模のエアドロッププログラムにおいて、誰が実際に利益を得て、誰の犠牲の上に成り立っているのか?**

2024-2025年、Binanceは76以上の報酬プログラムを通じてBNB保有者に約26億ドルを分配し、これは世界のCEX分配の約94%を占めます。代表的なプログラムは*Megadrop* と*HODLer Airdrop* で、*「BNBをロックすれば新規プロジェクトトークンを無料で受け取れる」* と広く宣伝されています。

本研究は、3つの主体への差別的影響を形式化します:

1. **BNB保有者** — 分配トークンの受領者
2. **発行財団** — 新規トークンを発行するプロジェクト主体
3. **BNB Chainエコシステム** — ブロックチェーンプラットフォーム自体

---

## 主要な発見

### 1. 財団災害 (Foundation Disaster)

平均分配比率α = 7.3%のMegadropトークンの場合:
- **財団コスト ≈ FDVの30.5%** (完全希釈評価額)
- **非対称比率R = 4.18** (財団損失:保有者利益)
- **価値破壊D ≈ FDVの23%** (市場摩擦による)

### 2. 数学的頑健性

合理的なパラメータ範囲において (α: 2-15%, θ: 30-60%, d: 10-90%):
- 財団コストは常に ≥ 12.75%
- 非対称比率は常に R ≥ 1.70
- **臨界分配比率α* = 5.95% (R*=5)** — Megadropの典型的な5-8%範囲が爆発領域に該当

### 3. 実証検証

ブートストラップ95%信頼区間分析 (N = 10,000回反復, サンプルN = 21トークン):

| カテゴリ | N | 平均リターン | 95% CI |
|----------|---|-------------|--------|
| Megadrop | 5 | -76.0% | [-86.4%, -65.8%] |
| HODLer | 8 | -19.5% | [-67.8%, +39.6%] |
| Launchpool | 5 | -29.8% | [-50.4%, +0.0%] |
| Direct (Memecoin) | 2 | +81.5% | [+68.0%, +95.0%] |
| **Direct (HYPE含む)** | 3 | **+384.3%** | **[+68.0%, +990.0%]** |

**Cohen's d (Megadrop vs. Direct, N=21) = -1.52** (非常に大きい効果量, Hyperliquid HYPE反実仮想統合により学術的信頼性を確保)

### 4. デカップリングパターン (Decoupling Pattern)

Megadropトークンが下落する一方で、BNB Chainエコシステムは*反対方向* に成長:

| 指標 | 2025年Q1→Q3変化 |
|------|-----------------|
| BNB Chain取引量 | **+171.4%** |
| BNB Chain DeFi TVL | **+47.2%** |
| BNB Chainアクティブウォレット | **+91.6%** |
| BNB価格 | $629 → $1,030 (Q4 ATH $1,369) |
| Megadropカテゴリ時価総額 | **-75%** |

### 5. 3主体の絶対金額影響 (2024-2025)

| 主体 | 推定影響 |
|------|----------|
| BNB保有者 (利益) | **+$14億-20億** |
| 発行財団 (損失) | **-$48億** |
| BNB Chain時価総額 (成長) | **+$1,040億** |

**主要な洞察**: 財団損失は明確 (保有者利益の2.84倍) ですが、BNB Chain時価総額成長のわずか4.6%にすぎない — *システムレベルでのデカップリングパターン*。

### 6. 理論的貢献

7つの定理が財団コスト関数を形式化し、以下を証明:

- **定理6**: *損益分岐不可能性* — d* = -α/(1-α-θ) < 0 (財団は価格上昇によってのみ損益分岐に到達可能)
- **定理7**: *ナッシュ均衡* — 即時売却が支配戦略

本研究はAllen, Berg, Lane (2023) の*直接エアドロップ* 分析を*中央集権型取引所主導(CEX-led)エアドロップ* という新規カテゴリに拡張し、Schelling (1960) の協調ゲーム理論およびMorrisとShin (1998) のグローバルゲームフレームワークを適用しています。

---

## リポジトリ構造

```
.
├── README.md                          # 英語版
├── README_KR.md                       # 韓国語版
├── README_CN.md                       # 中国語版
├── README_JP.md                       # 日本語版 (このファイル)
├── paper/                             # 論文成果物
│   ├── Distribution_Asymmetry_CEX_Airdrops.md
│   ├── Distribution_Asymmetry_CEX_Airdrops.pdf
│   ├── Distribution_Asymmetry_CEX_Airdrops_with_figures.docx
│   └── Distribution_Asymmetry_CEX_Airdrops_with_figures.pdf
├── figures/                           # 7枚の出版グレード可視化図表
├── scripts/                           # Pythonソースコード
├── data/                              # 入力データ (CSV, 英語)
├── results/                           # 分析結果出力
└── docs/                              # ドキュメント
```

---

## 再現性

### クイックスタート

```bash
# リポジトリのクローン
git clone https://github.com/gameworkerkim/vibe-investing.git
cd vibe-investing/02.Investment\ Idea\ Column/BNBChain

# 依存関係のインストール
pip install pandas numpy scipy matplotlib

# すべての分析を実行 (results/に出力)
cd scripts/
python correlation_analysis.py
python robustness_analysis.py
python integrated_analysis_v10.py
python pair_trading_backtest.py

# すべての図表を再生成 (figures/に出力)
for f in generate_figure*.py; do python "$f"; done
```

---

## 注意事項と限界

本研究は**予備ワーキングペーパー** です。以下の限界を明示的に認めます:

1. **サンプルサイズ**: N=21トークン (カテゴリ別N=2-8) は完全な統計的推論には不十分。後続バージョンでN≥100に拡大予定
2. **因果性**: デカップリングパターンは**観察的証拠のみ**。完全なグレンジャー因果性検定には日次データが必要であり、後続バージョンに延期
3. **時間解像度**: 四半期データは短期因果方向の推論を制限
4. **選択バイアス**: HYPE組み入れ (N=2→N=3) によりDirectカテゴリのMemecoinバイアスを部分的に緩和したものの、選択効果を完全に排除することはできない
5. **取引戦略**: 5.4節のBTC優位性パターンは**観察的証拠** であり、取引戦略への使用は推奨されない
6. **予測**: 本研究は過去の上場の**記述的分析** を生成。CEXポリシーの進化により、将来のトークンは異なるパターンを示す可能性がある

---

## 引用

本コード、データ、論文を研究で使用する場合は、以下のように引用してください:

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

## ライセンス

本リポジトリは**デュアルライセンス** を使用します:

- **ソースコード** (`scripts/`内のPythonスクリプト): [MITライセンス](https://opensource.org/licenses/MIT)
- **論文、データ、図表** (`paper/`, `data/`, `figures/`): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

---

## 著者

**金浩光 (Dennis Kim)** · 独立研究者
- Betalabs Inc.最高経営責任者 (ブロックチェーンカンパニービルダー)
- 元Cyworld Z最高経営責任者
- 元Microsoft Azure MVP (9年間)
- ORCID: [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175)
- GitHub: [@gameworkerkim](https://github.com/gameworkerkim)
- Email: gameworker@gmail.com

---

## ロードマップ

### v1.2 (現在 — 2026年5月)
- ✅ HYPE反実仮想統合 (N=2→N=3)
- ✅ ブートストラップ95% CI (N=10,000回反復)
- ✅ 3主体差別的影響の定量化
- ✅ 7枚の出版グレード図表 + 学術キャプション
- ✅ 5.2節相関係数値の修正
- ✅ 本文出現順序による図表番号の振り直し

### v2.0 (予定 — 2027)
- サンプルサイズN≥100トークン
- CoinGecko/Binance API経由の日次OHLCVデータ
- 完全なグレンジャー因果性検定
- 選択バイアスに対する傾向スコアマッチング (PSM)
- Heckman 2段階推定
- 複数取引所比較 (Bybit, OKX, Coinbase)
- 査読付き学術誌へのLaTeX投稿

---

## 関連文献

- **関連論文**: Kim, H. (2026). *The 72-Hour Shock: Token Unlock Price Impact*. SSRN 6632838.
- **トークンアンロック文献**: Allen, F., Gu, X., & Li, J.Y. (2023). *Crypto Tokens and Token Offerings*. Annual Review of Financial Economics.
- **共和分方法論**: Engle, R.F., & Granger, C.W.J. (1987). *Co-integration and Error Correction*. Econometrica.
- **協調ゲーム**: Schelling, T.C. (1960). *The Strategy of Conflict*. Harvard University Press.
- **グローバルゲーム**: Morris, S., & Shin, H.S. (1998). *Unique Equilibrium in a Model of Self-Fulfilling Currency Attacks*. American Economic Review.

---

*最終更新: 2026年5月1日*
