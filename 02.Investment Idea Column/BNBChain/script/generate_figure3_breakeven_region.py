"""
Chart 5: Foundation Break-Even Region (Section 4.7, Theorem 6)
Foundation cost region visualization in (α, d) plane + break-even curve
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10

# Parameter grid
alpha_vals = np.linspace(0.01, 0.15, 200)  # 1% to 15%
d_vals = np.linspace(-0.5, 0.9, 200)  # -50% to +90%
theta = 0.40

# Foundation cost function: C/FDV = α + (1-α-θ)·d
A, D = np.meshgrid(alpha_vals, d_vals)
C = A + (1 - A - theta) * D

# Break-even curve: d* = -α/(1-α-θ)
breakeven_d = -alpha_vals / (1 - alpha_vals - theta)

fig, ax = plt.subplots(figsize=(12, 8))

# Heatmap
levels = np.linspace(-0.4, 0.6, 21)
contour_filled = ax.contourf(A * 100, D * 100, C * 100, levels=levels*100,
                              cmap='RdYlGn_r', extend='both', alpha=0.85)

# Contour lines
contour_lines = ax.contour(A * 100, D * 100, C * 100,
                            levels=[-20, -10, 0, 10, 20, 30, 40, 50],
                            colors='black', linewidths=0.7, alpha=0.5)
ax.clabel(contour_lines, inline=True, fontsize=8, fmt='%d%%')

# Break-even curve (C=0, thick black line)
ax.plot(alpha_vals * 100, breakeven_d * 100, 'k-', linewidth=3,
        label='Break-even curve: $d^* = -\\alpha/(1-\\alpha-\\theta)$')

# Megadrop region highlighted (α=5-8%, d=44%)
ax.fill_between([5, 8], [44, 44], [44, 44], alpha=0)
megadrop_rect = plt.Rectangle((5, 30), 3, 30, fill=True, facecolor='none',
                               edgecolor='#0D47A1', linewidth=2.5, linestyle='--')
ax.add_patch(megadrop_rect)
ax.text(6.5, 70, 'Megadrop\nactual range\n(α=5-8%, d≈44%)',
        ha='center', va='bottom', fontsize=10, fontweight='bold', color='#0D47A1',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor='#0D47A1', linewidth=1.5))

# Key point (Megadrop average: α=7.3%, d=44%)
ax.plot(7.3, 44, 'o', markersize=18, color='#FF6F00', markeredgecolor='black',
        markeredgewidth=2, zorder=5)
ax.annotate('Megadrop average\n(α=7.3%, d=44%)\n→ C = 30.5% FDV',
            xy=(7.3, 44), xytext=(4.5, 10),
            fontsize=10, fontweight='bold', color='#FF6F00',
            ha='center',
            arrowprops=dict(arrowstyle='->', color='#FF6F00', lw=1.5),
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor='#FF6F00', linewidth=1.5))

# HODLer region (α=2-3%, d varies)
hodler_rect = plt.Rectangle((1.5, -50), 1.5, 140, fill=True, facecolor='none',
                             edgecolor='#6A1B9A', linewidth=2, linestyle=':')
ax.add_patch(hodler_rect)
ax.text(2.25, -45, 'HODLer\n(α=2-3%)', ha='center', va='bottom', fontsize=9, color='#6A1B9A',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#6A1B9A'))

# Direct region (α=0)
ax.axvline(x=0.5, color='#1B5E20', linestyle=':', linewidth=2)
ax.text(0.6, 75, 'Direct\n(α≈0)', fontsize=9, color='#1B5E20', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#1B5E20'))

# Region text
ax.text(12, -35, 'Foundation\nProfit Region\n(C < 0)',
        ha='center', va='center', fontsize=12, fontweight='bold', color='#1B5E20',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#E8F5E9', edgecolor='#1B5E20', alpha=0.9))

ax.text(12, 60, 'Foundation\nLoss Region\n(C > 0)',
        ha='center', va='center', fontsize=12, fontweight='bold', color='#C62828',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFEBEE', edgecolor='#C62828', alpha=0.9))

# 0% d baseline
ax.axhline(y=0, color='#666666', linestyle='-', linewidth=0.8, alpha=0.5)

# Colorbar
cbar = plt.colorbar(contour_filled, ax=ax, shrink=0.85, pad=0.02)
cbar.set_label('Foundation Cost / FDV (%)', fontsize=10, fontweight='bold')

# Axes
ax.set_xlabel('Distribution Ratio α (%)', fontsize=11, fontweight='bold')
ax.set_ylabel('Price Decline Rate d (%)', fontsize=11, fontweight='bold')
ax.set_xlim(0, 15)
ax.set_ylim(-50, 90)

# Title
ax.set_title('Theorem 6: Foundation Break-Even Region (θ=0.40 fixed)\n'
             'Foundation Loss = $\\alpha + (1-\\alpha-\\theta) \\cdot d$ — Loss Across All Megadrop α-d Combinations',
             fontsize=12, fontweight='bold', pad=15)

# Legend
ax.legend(loc='lower right', fontsize=10, framealpha=0.95)

# Grid
ax.grid(alpha=0.2, linestyle=':')

# Bottom annotation
ax.text(0.99, -0.10,
        'Note: Solid black curve marks break-even ($C = 0$). For Megadrop typical (α=5-8%, d≈44%), '
        'foundation falls deeply in loss region.\n'
        'Break-even requires d ≤ -14.3% (i.e., 14.3%+ price increase post-listing).',
        transform=ax.transAxes, ha='right', va='top', fontsize=8,
        style='italic', color='#666666')

plt.tight_layout()
plt.savefig('../figures/Chart5_BreakEvenRegion.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.savefig('../figures/Chart5_BreakEvenRegion.pdf', bbox_inches='tight', facecolor='white')
print("Chart 5 saved: Break-Even Region")
plt.close()
