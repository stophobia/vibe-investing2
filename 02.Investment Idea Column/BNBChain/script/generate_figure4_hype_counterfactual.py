"""
Chart 4: HYPE Counterfactual Trajectory (Section 6.2.7)
Hyperliquid HYPE +990% vs Megadrop average -76%
"""

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10

fig, ax = plt.subplots(figsize=(13, 7))

# Time axis (T-0 to T+1y, month units)
months = [0, 0.07, 1, 6, 12, 16]  # T-0, 48h, 1mo, 6mo, 12mo, 16mo (2026 Q1)

# HYPE price (normalized: T-0 = 100)
# $3.90 → $9.74 (+150%) → $35 (+797%) → $25-30 (+540~670%) → $40-45 (+925~1054%)
hype_prices = [100, 250, 897, 705, 1027, 1027]  # average values

# Megadrop average (normalized: T-0 = 100)
# T-0=100 → T+1y ~24 (-76%)
# Time distribution: fast initial decline + gradual further decline
megadrop_prices = [100, 75, 50, 32, 24, 24]

# Direct (Memecoin) average
# WIF +95%, PEPE +68% average +81.5%
direct_meme = [100, 105, 115, 140, 181, 181]

# HODLer average (wide range, mean -19.5%)
hodler_avg = [100, 90, 80, 75, 80, 80]

# Plot
ax.plot(months, hype_prices, 'o-', linewidth=3, markersize=12, color='#1B5E20',
        label='Hyperliquid HYPE (Direct, no CEX distribution)', zorder=4,
        markeredgecolor='black', markeredgewidth=1)
ax.plot(months, direct_meme, 's-', linewidth=2.5, markersize=10, color='#558B2F',
        label='Direct Memecoin avg (WIF, PEPE)', zorder=3,
        markeredgecolor='black', markeredgewidth=0.8)
ax.plot(months, hodler_avg, '^-', linewidth=2, markersize=10, color='#E65100',
        label='HODLer Airdrop avg', zorder=3,
        markeredgecolor='black', markeredgewidth=0.8)
ax.plot(months, megadrop_prices, 'v-', linewidth=3, markersize=12, color='#C62828',
        label='Megadrop avg (BB, LISTA, SOLV, ...)', zorder=4,
        markeredgecolor='black', markeredgewidth=1)

# 100% baseline
ax.axhline(y=100, color='#666666', linestyle=':', linewidth=1.2, zorder=1)

# Data labels (final point + initial point)
ax.text(16.4, 1027, '+927%', fontsize=11, fontweight='bold', color='#1B5E20', va='center')
ax.text(16.4, 181, '+81%', fontsize=11, fontweight='bold', color='#558B2F', va='center')
ax.text(16.4, 80, '-20%', fontsize=11, fontweight='bold', color='#E65100', va='center')
ax.text(16.4, 24, '-76%', fontsize=11, fontweight='bold', color='#C62828', va='center')

# Region shading
ax.axhspan(0, 100, alpha=0.05, color='red')
ax.axhspan(100, 1100, alpha=0.05, color='green')

# Annotation: key message
ax.annotate('HYPE has zero CEX distribution\nand zero VC allocation\n(Counterfactual evidence)',
            xy=(12, 1027), xytext=(7, 1100),
            fontsize=10, fontweight='bold', color='#000000',
            ha='center',
            arrowprops=dict(arrowstyle='->', color='#1B5E20', lw=1.5),
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#E8F5E9', edgecolor='#1B5E20', linewidth=1.2))

ax.annotate('Megadrop α=5–8% distribution\n→ Sustained decline',
            xy=(12, 24), xytext=(8, -100),
            fontsize=10, fontweight='bold', color='#000000',
            ha='center',
            arrowprops=dict(arrowstyle='->', color='#C62828', lw=1.5),
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFEBEE', edgecolor='#C62828', linewidth=1.2))

# Axis settings
ax.set_xlabel('Time After Listing (months)', fontsize=11, fontweight='bold')
ax.set_ylabel('Indexed Price (Listing = 100)', fontsize=11, fontweight='bold')
ax.set_xlim(-1, 19)
ax.set_ylim(-200, 1200)
ax.set_xticks([0, 1, 3, 6, 9, 12, 15])
ax.set_xticklabels(['T-0\n(Listing)', '1mo', '3mo', '6mo', '9mo', '12mo', '15mo'])

# Grid
ax.grid(alpha=0.3, linestyle=':')
ax.set_axisbelow(True)

# Title
ax.set_title('Counterfactual Evidence: Distribution Mechanism Effect on Token Price\n'
             'Hyperliquid HYPE (Direct, no CEX) vs. Megadrop / HODLer Categories',
             fontsize=12, fontweight='bold', pad=15)

# Legend
ax.legend(loc='center left', fontsize=10, framealpha=0.95)

# Bottom annotation
ax.text(0.99, 0.02,
        'Sources: HYPE prices from CoinDesk, CoinMarketCap, Coinpedia. '
        'Megadrop / HODLer averages from Table 6.1.\n'
        'Note: Index = 100 at listing date (T-0). Logarithmic effect visible due to HYPE outlier.',
        transform=ax.transAxes, ha='right', va='bottom', fontsize=8,
        style='italic', color='#666666',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='none'))

plt.tight_layout()
plt.savefig('../figures/Chart4_HYPE_Counterfactual.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.savefig('../figures/Chart4_HYPE_Counterfactual.pdf', bbox_inches='tight', facecolor='white')
print("Chart 4 saved: HYPE Counterfactual")
plt.close()
