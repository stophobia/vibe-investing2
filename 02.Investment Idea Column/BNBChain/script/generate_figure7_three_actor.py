"""
Chart 3: Three-Actor Differential Impact (Section 7.6 + Section 10.3)
Per-actor absolute amount + scenario sensitivity
"""

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7), gridspec_kw={'width_ratios': [1.2, 1]})

# ============================================
# Subplot 1: 3-Actor absolute amount (Base scenario)
# ============================================

actors = ['BNB Holders\n(Gain)', 'Issuing Foundations\n(Loss)', 'BNB Chain\nMarket Cap (Growth)']
values = [1.69, -4.80, 104.0]  # Base scenario
colors_act = ['#2E7D32', '#C62828', '#1565C0']

# Use absolute values for log scale
# Alternative approach - separated bars
y_pos = np.arange(len(actors))[::-1]
bars = ax1.barh(y_pos, values, color=colors_act, edgecolor='black', linewidth=1.2, height=0.6)

# 0 baseline
ax1.axvline(x=0, color='black', linewidth=1)

# Data labels
for i, (y, v, label) in enumerate(zip(y_pos, values, actors)):
    if v > 0:
        ax1.text(v + 3, y, f'+${v:.2f}B', va='center', fontsize=12, fontweight='bold', color=colors_act[i])
    else:
        ax1.text(v - 3, y, f'-${abs(v):.2f}B', va='center', ha='right', fontsize=12, fontweight='bold', color=colors_act[i])

# Ratio annotation
ax1.annotate('Foundation loss = 2.84× Holder gain\n(Asymmetry visible at absolute scale)',
             xy=(-4.8, 1), xytext=(15, 1.7),
             fontsize=9, ha='center',
             arrowprops=dict(arrowstyle='->', color='#555555'),
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFF9C4', edgecolor='#F57F17', linewidth=1))

ax1.annotate('Foundation loss = only 4.6%\nof BNB Chain market cap growth\n(Decoupling pattern)',
             xy=(104, 0), xytext=(50, -0.6),
             fontsize=9, ha='center',
             arrowprops=dict(arrowstyle='->', color='#555555'),
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#E3F2FD', edgecolor='#1565C0', linewidth=1))

ax1.set_yticks(y_pos)
ax1.set_yticklabels(actors, fontsize=11)
ax1.set_xlabel('Absolute Monetary Impact (USD billions, 2024–2025)', fontsize=11, fontweight='bold')
ax1.set_xlim(-15, 120)
ax1.set_ylim(-1.2, 2.6)
ax1.grid(axis='x', alpha=0.3, linestyle=':')
ax1.set_axisbelow(True)
ax1.set_title('Panel A: Three-Actor Absolute Impact (Base Scenario)',
              fontsize=12, fontweight='bold', pad=10)

# ============================================
# Subplot 2: Scenario sensitivity (Foundation/Holder Ratio)
# ============================================

scenarios = ['Pessimistic\n(40% / $200M /\n40 listings)',
             'Conservative\n(55% / $300M /\n50 listings)',
             'Base\n(65% / $400M /\n60 listings)',
             'Optimistic\n(75% / $500M /\n80 listings)',
             'Very Optimistic\n(85% / $600M /\n100 listings)']
holder_gains = [1.04, 1.43, 1.69, 1.95, 2.21]
foundation_losses = [1.60, 3.00, 4.80, 8.00, 12.00]
ratios = [1.5, 2.1, 2.8, 4.1, 5.4]

x = np.arange(len(scenarios))
width = 0.35

bar1 = ax2.bar(x - width/2, holder_gains, width, label='BNB Holder Gain',
               color='#2E7D32', edgecolor='black', linewidth=0.8)
bar2 = ax2.bar(x + width/2, foundation_losses, width, label='Foundation Total Loss',
               color='#C62828', edgecolor='black', linewidth=0.8)

# Ratio display (on twin axis)
ax2_twin = ax2.twinx()
ax2_twin.plot(x, ratios, 'o-', color='#FF8F00', linewidth=2.5, markersize=10,
              markeredgecolor='black', markeredgewidth=1, label='Foundation/Holder Ratio')
ax2_twin.set_ylabel('Foundation Loss / Holder Gain Ratio', fontsize=11, fontweight='bold', color='#FF8F00')
ax2_twin.tick_params(axis='y', labelcolor='#FF8F00')
ax2_twin.set_ylim(0, 7)

# Ratio data labels
for i, r in enumerate(ratios):
    ax2_twin.text(i, r + 0.25, f'{r}×', ha='center', fontsize=10, fontweight='bold', color='#FF8F00')

# Bar data labels
for i, (h, f) in enumerate(zip(holder_gains, foundation_losses)):
    ax2.text(i - width/2, h + 0.2, f'${h:.2f}B', ha='center', fontsize=8)
    ax2.text(i + width/2, f + 0.2, f'${f:.2f}B', ha='center', fontsize=8)

ax2.set_xticks(x)
ax2.set_xticklabels(scenarios, fontsize=8)
ax2.set_ylabel('USD (billions)', fontsize=11, fontweight='bold')
ax2.set_xlabel('Scenarios (Realization Rate / Avg FDV / Listing Count)', fontsize=10, fontweight='bold')
ax2.set_ylim(0, 14)
ax2.legend(loc='upper left', fontsize=9)
ax2_twin.legend(loc='upper right', fontsize=9)
ax2.grid(axis='y', alpha=0.3, linestyle=':')
ax2.set_axisbelow(True)
ax2.set_title('Panel B: Sensitivity Across 5 Scenarios',
              fontsize=12, fontweight='bold', pad=10)

# Overall title
fig.suptitle('Three-Actor Differential Impact of Centralized Exchange Airdrops (2024–2025)\n'
             'Foundation Disaster vs. Holder Gain vs. Ecosystem Decoupling',
             fontsize=13, fontweight='bold', y=1.02)

# Bottom annotation
fig.text(0.5, -0.02,
         'Notes: Panel A shows base scenario (65% realization rate, $400M avg FDV, 60 listings). '
         'Panel B shows sensitivity across 5 scenarios. The Foundation/Holder ratio remains ≥1.5× across all scenarios.',
         ha='center', fontsize=8, style='italic', color='#666666')

plt.tight_layout()
plt.savefig('../figures/Chart3_ThreeActor.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.savefig('../figures/Chart3_ThreeActor.pdf', bbox_inches='tight', facecolor='white')
print("Chart 3 saved: Three-Actor Impact")
plt.close()
