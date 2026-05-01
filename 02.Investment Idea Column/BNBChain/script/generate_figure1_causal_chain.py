"""
Diagram 1: Mathematical Causal Chain (Section 10.1)
Convert 7-stage causal chain ASCII art to academic publication-grade flowchart
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Academic publication style settings
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 9
plt.rcParams['axes.linewidth'] = 0.8

fig, ax = plt.subplots(figsize=(11, 14))
ax.set_xlim(0, 10)
ax.set_ylim(0, 18)
ax.axis('off')

# Color palette (academic/neutral)
INPUT_COLOR = '#E8F0F7'
PROCESS_COLOR = '#FFF4E6'
OUTPUT_COLOR = '#E8F5E9'
EDGE_COLOR = '#2C3E50'
TEXT_COLOR = '#1A1A1A'

def draw_box(x, y, w, h, title, content, color, ax):
    """Draw rounded-corner box"""
    box = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0.05,rounding_size=0.15",
                          facecolor=color, edgecolor=EDGE_COLOR,
                          linewidth=1.2)
    ax.add_patch(box)
    # Title
    ax.text(x + w/2, y + h - 0.3, title,
            ha='center', va='top', fontsize=10, fontweight='bold',
            color=TEXT_COLOR)
    # Content
    ax.text(x + w/2, y + h/2 - 0.3, content,
            ha='center', va='center', fontsize=9,
            color=TEXT_COLOR)

def draw_arrow(x1, y1, x2, y2, ax, label=None):
    """Draw arrow"""
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                             arrowstyle='->,head_width=4,head_length=6',
                             color=EDGE_COLOR, linewidth=1.5)
    ax.add_patch(arrow)
    if label:
        ax.text((x1+x2)/2 + 0.15, (y1+y2)/2, label,
                fontsize=8, style='italic', color='#555555')

# Title
ax.text(5, 17.5, 'Mathematical Causal Chain',
        ha='center', fontsize=14, fontweight='bold', color=TEXT_COLOR)
ax.text(5, 17.0, 'Seven-Stage Formal Derivation of Distribution Asymmetry',
        ha='center', fontsize=10, style='italic', color='#555555')

# 1. Input box
draw_box(3, 15.2, 4, 1.3, 'INPUT',
         'Distribution Ratio α ∈ [0.05, 0.08]\nMegadrop typical range',
         INPUT_COLOR, ax)
draw_arrow(5, 15.15, 5, 14.4, ax)

# 2. Theorems 1-2 box
draw_box(2, 12.8, 6, 1.5, 'Theorems 1–2: Foundation Cost Function',
         r'$C_{total} = \alpha S P_0 + (1-\alpha-\theta) d S P_0$',
         PROCESS_COLOR, ax)
draw_arrow(5, 12.75, 5, 12.0, ax)

# 3. Theorems 3-5 box
draw_box(2, 10.4, 6, 1.5, 'Theorems 3–5: Numerical Substitution',
         'Megadrop average: 30.5% FDV foundation cost\nAsymmetry R = 4.18,  Value destruction D = 23%',
         PROCESS_COLOR, ax)
draw_arrow(5, 10.35, 5, 9.6, ax)

# 4. Theorem 6
draw_box(2, 8.0, 6, 1.5, 'Theorem 6: Break-Even Impossibility',
         r'$d^* = -\alpha/(1-\alpha-\theta) < 0$' + '\n→ Only price increase enables break-even',
         PROCESS_COLOR, ax)
draw_arrow(5, 7.95, 5, 7.2, ax)

# 5. Theorem 7
draw_box(2, 5.6, 6, 1.5, 'Theorem 7: Nash Equilibrium',
         'Immediate sell-off is dominant strategy\nEmpirical: SPK −70% within hours',
         PROCESS_COLOR, ax)

# 6. Side branches: 4.10 + 4.11 + 4.8.1 (parallel verification)
# Left
draw_box(0.2, 3.0, 3.0, 1.8, 'Section 4.10\nScenario Robustness',
         'α: 2–15%\nθ: 30–60%\nd: 10–90%\n→ R ≥ 1.70 always',
         INPUT_COLOR, ax)
# Center
draw_box(3.5, 3.0, 3.0, 1.8, 'Section 4.11\nThreshold α*',
         r'$\alpha^* = (1-\theta)d / (R^*-1+d)$' + '\nR*=5 → α* = 5.95%\nMegadrop in critical zone',
         INPUT_COLOR, ax)
# Right
draw_box(6.8, 3.0, 3.0, 1.8, 'Section 4.8.1\nStochastic Extension',
         r'$\sigma_i \sim Beta(\eta, \mu)$' + '\nσ̄ ∈ [0.55, 0.85]\n→ Robustness verified',
         INPUT_COLOR, ax)

# Theorem 7 → 3 branches
draw_arrow(3.5, 5.55, 1.7, 4.85, ax)
draw_arrow(5.0, 5.55, 5.0, 4.85, ax)
draw_arrow(6.5, 5.55, 8.3, 4.85, ax)

# 3 branches → output
draw_arrow(1.7, 2.95, 3.5, 2.0, ax)
draw_arrow(5.0, 2.95, 5.0, 2.0, ax)
draw_arrow(8.3, 2.95, 6.5, 2.0, ax)

# 7. Output box
draw_box(2, 0.3, 6, 1.7, 'OUTPUT — Three-Actor Asymmetry',
         'Asymmetry R = 4.18 (Megadrop)  |  R = 12.66 (HODLer)\n'
         'Value destruction D = 23.1% FDV\n'
         'Decoupling pattern observed',
         OUTPUT_COLOR, ax)

plt.tight_layout()
plt.savefig('../figures/Diagram1_Causal_Chain.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.savefig('../figures/Diagram1_Causal_Chain.pdf', bbox_inches='tight', facecolor='white')
print("Diagram 1 saved: Causal Chain")
plt.close()
