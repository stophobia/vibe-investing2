"""
Chart 2: BNB Chain Decoupling Pattern (Section 7.4)
Dual time series - BNB Chain macro vs Megadrop category
"""

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10

# Data (Table B.6 + Megadrop category market cap estimates)
quarters = ['2025 Q1', '2025 Q2', '2025 Q3']

# BNB Chain macro indicators (normalized to Q1=100)
volume_normalized = [100, 202, 271]  # +101.9%, +171.4%
tvl_normalized = [100, 113, 147]  # +13.0%, +47.2% 
active_wallets = [100, 133, 192]  # +33.3%, +91.6%

# Megadrop category market cap (normalized to Q1=100)
# Q1 ~$200M -> Q3 ~$50M estimate (about -75%)
megadrop_mc = [100, 60, 25]

# BNB price (Q1=$629, Q2=$655, Q3=$1,030, Q4=$1,200)
bnb_price_normalized = [100, 104, 164]

fig, ax = plt.subplots(figsize=(12, 7))

x = np.arange(len(quarters))

# BNB Chain macro (positive region, deep colors)
ax.plot(x, volume_normalized, marker='o', markersize=10, linewidth=2.5,
        color='#1B5E20', label='BNB Chain Trading Volume', zorder=3)
ax.plot(x, tvl_normalized, marker='s', markersize=10, linewidth=2.5,
        color='#2E7D32', label='BNB Chain DeFi TVL', zorder=3)
ax.plot(x, bnb_price_normalized, marker='^', markersize=10, linewidth=2.5,
        color='#388E3C', label='BNB Price', zorder=3)
ax.plot(x, active_wallets, marker='D', markersize=9, linewidth=2.5,
        color='#558B2F', label='BNB Chain Active Wallets', zorder=3)

# Megadrop category (negative region, red)
ax.plot(x, megadrop_mc, marker='v', markersize=12, linewidth=3,
        color='#C62828', label='Megadrop Category Market Cap', zorder=3,
        linestyle='--')

# 100% baseline
ax.axhline(y=100, color='#666666', linestyle=':', linewidth=1.2, zorder=1)
ax.text(2.05, 102, 'Q1 baseline (100)', fontsize=8, style='italic', color='#666666')

# Data labels
for i, q in enumerate(quarters):
    ax.text(i, volume_normalized[i]+10, f'+{volume_normalized[i]-100}%' if volume_normalized[i] > 100 else f'{volume_normalized[i]-100}%',
            ha='center', fontsize=8, color='#1B5E20', fontweight='bold')
    ax.text(i, megadrop_mc[i]-15, f'{megadrop_mc[i]-100}%' if megadrop_mc[i] != 100 else 'baseline',
            ha='center', fontsize=8, color='#C62828', fontweight='bold')

# Region shading
ax.axhspan(0, 100, alpha=0.05, color='red')
ax.axhspan(100, 300, alpha=0.05, color='green')

# Annotation: emphasize decoupling
ax.annotate('Decoupling Pattern\n(Macro grows; new tokens decline)',
            xy=(1.5, 165), xytext=(0.7, 230),
            fontsize=11, fontweight='bold', color='#000000',
            ha='center',
            arrowprops=dict(arrowstyle='->', color='#333333', lw=1.5),
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF9C4', edgecolor='#F57F17', linewidth=1.2))

# Axis settings
ax.set_xticks(x)
ax.set_xticklabels(quarters, fontsize=11)
ax.set_xlabel('Quarter', fontsize=11, fontweight='bold')
ax.set_ylabel('Indexed Value (Q1 2025 = 100)', fontsize=11, fontweight='bold')
ax.set_ylim(-10, 290)

# Grid
ax.grid(axis='y', alpha=0.3, linestyle=':')
ax.set_axisbelow(True)

# Title
ax.set_title('BNB Chain Macro-Activity vs. Megadrop Category Market Cap (2025 Q1–Q3)\n'
             'Pattern Observation: Time-Series Trends in Opposite Directions',
             fontsize=12, fontweight='bold', pad=15)

# Legend
ax.legend(loc='upper left', fontsize=9, framealpha=0.95, ncol=1)

# Caution notice
ax.text(0.99, 0.02, 'Note: Pattern observation only — causality requires Granger testing (Limitation 6).\n'
                    'Source: Messari "State of BNB" Q1–Q3 2025 reports + author estimates.',
        transform=ax.transAxes, ha='right', va='bottom', fontsize=8,
        style='italic', color='#666666',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='none'))

plt.tight_layout()
plt.savefig('../figures/Chart2_Decoupling.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.savefig('../figures/Chart2_Decoupling.pdf', bbox_inches='tight', facecolor='white')
print("Chart 2 saved: Decoupling Pattern")
plt.close()
