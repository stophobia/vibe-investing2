"""
Chart 1: Bootstrap 95% CI Forest Plot (Section 6.2.1, Table 6.1 visualization)
Medical/meta-analysis standard Forest Plot format
"""

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10

# Data (Table 6.1)
categories = [
    "Megadrop\n(N=5)",
    "HODLer\n(N=8)",
    "Launchpool\n(N=5)",
    "Direct (Memecoin)\n(N=2)",
    "Direct (Diversified)\n(N=3, +HYPE)"
]

means = [-76.00, -19.50, -29.80, 81.50, 384.33]
ci_lower = [-86.40, -67.75, -50.40, 68.00, 68.00]
ci_upper = [-65.80, 39.62, 0.00, 95.00, 990.00]
geom_means = [-80.04, -60.57, -34.90, 81.00, 229.30]
n_sizes = [5, 8, 5, 2, 3]

# Colors: negative = red shades, positive = green shades
colors = []
for m in means:
    if m < -50:
        colors.append('#C62828')  # deep red
    elif m < 0:
        colors.append('#E65100')  # orange
    elif m < 100:
        colors.append('#558B2F')  # light green
    else:
        colors.append('#1B5E20')  # deep green

fig, ax = plt.subplots(figsize=(13, 7))

y_positions = np.arange(len(categories))[::-1]  # Top to bottom (Megadrop on top)

# 0% baseline
ax.axvline(x=0, color='#888888', linestyle='--', linewidth=1.2, zorder=1)
ax.text(0, len(categories)+0.1, '0% (No effect)', ha='center', fontsize=8, style='italic', color='#666666')

# CI line + mean point
for i, (y, mean, lo, hi, geom, color, n) in enumerate(zip(y_positions, means, ci_lower, ci_upper, geom_means, colors, n_sizes)):
    # CI line
    ax.plot([lo, hi], [y, y], color=color, linewidth=2.5, zorder=2)
    # CI end caps
    ax.plot([lo, lo], [y-0.12, y+0.12], color=color, linewidth=2.5, zorder=2)
    ax.plot([hi, hi], [y-0.12, y+0.12], color=color, linewidth=2.5, zorder=2)
    # Arithmetic mean point (large circle)
    ax.scatter(mean, y, s=180, color=color, edgecolor='black', linewidth=1.2, zorder=3, label='Arithmetic mean' if i == 0 else "")
    # Geometric mean point (small diamond)
    ax.scatter(geom, y, s=80, color='white', edgecolor=color, linewidth=2, marker='D', zorder=3, label='Geometric mean' if i == 0 else "")
    
    # Right label: mean + CI
    label_text = f'  {mean:+.1f}% [{lo:+.1f}, {hi:+.1f}]'
    if hi > 500:
        # Too-large CIs displayed inside body area (above CI line)
        ax.text(220, y + 0.28, label_text, va='center', fontsize=9, color=color, fontweight='bold')
    else:
        ax.text(hi + 15, y, label_text, va='center', fontsize=9, color=color, fontweight='bold')

# Y-axis labels
ax.set_yticks(y_positions)
ax.set_yticklabels(categories, fontsize=10)

# X-axis
ax.set_xlabel('1-year+ BTC-relative Return (%)', fontsize=11, fontweight='bold')
ax.set_xlim(-150, 1100)

# X-axis grid
ax.grid(axis='x', alpha=0.3, linestyle=':')
ax.set_axisbelow(True)

# Legend
ax.legend(loc='lower right', fontsize=9, framealpha=0.9)

# Title
ax.set_title('Category-wise 1-year+ Returns with Bootstrap 95% Confidence Intervals\n'
             'Distribution Mechanism Effect: Negative for Airdrop Categories, Positive for Direct',
             fontsize=12, fontweight='bold', pad=15)

# Region shading
ax.axvspan(-150, 0, alpha=0.05, color='red')
ax.axvspan(0, 1100, alpha=0.05, color='green')

# Bottom-right annotation
ax.text(0.99, 0.02, 'Bootstrap N=10,000  |  Sample N=21 tokens  |  Source: Table 6.1',
        transform=ax.transAxes, ha='right', va='bottom', fontsize=8,
        style='italic', color='#666666')

# Left labels (region indicators)
ax.text(-75, len(categories)+0.45, 'Loss', ha='center', fontsize=9, color='#C62828', fontweight='bold')
ax.text(500, len(categories)+0.45, 'Gain', ha='center', fontsize=9, color='#1B5E20', fontweight='bold')

plt.tight_layout()
plt.savefig('../figures/Chart1_ForestPlot.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.savefig('../figures/Chart1_ForestPlot.pdf', bbox_inches='tight', facecolor='white')
print("Chart 1 saved: Forest Plot")
plt.close()
