"""
Diagram 2: Revised Model — Partial Self-Cannibalizing Loop + Decoupling
(Section 7.4) - Convert two-domain separation ASCII art flowchart to academic diagram
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 9

fig, ax = plt.subplots(figsize=(13, 11))
ax.set_xlim(0, 13)
ax.set_ylim(0, 14)
ax.axis('off')

# Colors
LOSS_COLOR = '#FFEBEE'
LOSS_EDGE = '#C62828'
GAIN_COLOR = '#E8F5E9'
GAIN_EDGE = '#1B5E20'
EDGE_COLOR = '#2C3E50'
TEXT_COLOR = '#1A1A1A'

def draw_box(x, y, w, h, text, color, edge_color, ax, fontsize=9, weight='normal'):
    box = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0.05,rounding_size=0.1",
                          facecolor=color, edgecolor=edge_color,
                          linewidth=1.3)
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, text,
            ha='center', va='center', fontsize=fontsize, fontweight=weight,
            color=TEXT_COLOR)

def draw_arrow(x1, y1, x2, y2, ax, color=EDGE_COLOR, style='->'):
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                             arrowstyle=f'{style},head_width=4,head_length=6',
                             color=color, linewidth=1.5)
    ax.add_patch(arrow)

# Title
ax.text(6.5, 13.4, 'Revised Model: Partial Self-Cannibalizing Loop + Decoupling',
        ha='center', fontsize=14, fontweight='bold', color=TEXT_COLOR)
ax.text(6.5, 12.9, 'Two Domains with Different Outcomes',
        ha='center', fontsize=10, style='italic', color='#555555')

# Domain headers
ax.text(3, 12.0, '[Megadrop Impact Domain]',
        ha='center', fontsize=12, fontweight='bold', color=LOSS_EDGE,
        bbox=dict(boxstyle='round,pad=0.4', facecolor=LOSS_COLOR, edgecolor=LOSS_EDGE, linewidth=1.5))
ax.text(10, 12.0, '[BNB Chain Macro Domain]',
        ha='center', fontsize=12, fontweight='bold', color=GAIN_EDGE,
        bbox=dict(boxstyle='round,pad=0.4', facecolor=GAIN_COLOR, edgecolor=GAIN_EDGE, linewidth=1.5))

# ====== Left (Megadrop Impact Domain) ======
left_x = 0.8
box_w = 4.4
box_h = 0.9

# Step 1
draw_box(left_x, 10.5, box_w, box_h, '1. BNB holder benefits enhanced',
         LOSS_COLOR, LOSS_EDGE, ax)
draw_arrow(3, 10.4, 3, 9.7, ax, color=LOSS_EDGE)

# Step 2
draw_box(left_x, 8.7, box_w, box_h, '2. Megadrop 5%+ distribution',
         LOSS_COLOR, LOSS_EDGE, ax)
draw_arrow(3, 8.6, 3, 7.9, ax, color=LOSS_EDGE)

# Step 3
draw_box(left_x, 6.9, box_w, box_h, '3. New token selling pressure',
         LOSS_COLOR, LOSS_EDGE, ax)
draw_arrow(3, 6.8, 3, 6.1, ax, color=LOSS_EDGE)

# Step 4
draw_box(left_x, 5.1, box_w, box_h, '4. New tokens −44% average loss',
         LOSS_COLOR, LOSS_EDGE, ax, weight='bold')
draw_arrow(3, 5.0, 3, 4.3, ax, color=LOSS_EDGE)

# Step 5
draw_box(left_x, 3.3, box_w, box_h, '5. Megadrop category market cap collapse',
         LOSS_COLOR, LOSS_EDGE, ax, weight='bold')

# Result label (left domain)
draw_box(left_x, 1.0, box_w, 1.5, 
         'Megadrop Category Outcome:\nLoss accumulation\n(−$4.8B foundation cost)',
         '#FFCDD2', LOSS_EDGE, ax, fontsize=10, weight='bold')

# ====== Right (BNB Chain Macro Domain) ======
right_x = 7.8

# Driver 1
draw_box(right_x, 10.5, box_w, box_h, 'Binance Alpha trading volume surge',
         GAIN_COLOR, GAIN_EDGE, ax)
draw_arrow(10, 10.4, 10, 9.7, ax, color=GAIN_EDGE)

# Driver 2
draw_box(right_x, 8.7, box_w, box_h, 'PancakeSwap V4 launch',
         GAIN_COLOR, GAIN_EDGE, ax)
draw_arrow(10, 8.6, 10, 7.9, ax, color=GAIN_EDGE)

# Driver 3
draw_box(right_x, 6.9, box_w, box_h, 'Aster Perp DEX',
         GAIN_COLOR, GAIN_EDGE, ax)
draw_arrow(10, 6.8, 10, 6.1, ax, color=GAIN_EDGE)

# Result 1
draw_box(right_x, 5.1, box_w, box_h, 'BNB Chain macro +63.7% growth',
         GAIN_COLOR, GAIN_EDGE, ax, weight='bold')
draw_arrow(10, 5.0, 10, 4.3, ax, color=GAIN_EDGE)

# Result 2
draw_box(right_x, 3.3, box_w, box_h, 'BNB price ATH $1,369 (Q4 2025)',
         GAIN_COLOR, GAIN_EDGE, ax, weight='bold')

# Result label (right domain)
draw_box(right_x, 1.0, box_w, 1.5, 
         'BNB Chain Macro Outcome:\nGrowth +$104B market cap\n(decoupled from new tokens)',
         '#C8E6C9', GAIN_EDGE, ax, fontsize=10, weight='bold')

# ====== Domain separator line ======
ax.axvline(x=6.5, ymin=0.05, ymax=0.85, color='#888888', linestyle='--', linewidth=1.5)
ax.text(6.5, 5.0, 'D\nE\nC\nO\nU\nP\nL\nI\nN\nG',
        ha='center', va='center', fontsize=11, fontweight='bold', color='#F57F17',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF9C4', edgecolor='#F57F17', linewidth=1.5))

# ====== Key message ======
draw_box(2, -0.3, 9, 1.1, 
         'Key Finding: The two domains exhibit time-series trends in opposite directions.\n'
         'Self-cannibalizing loop hypothesis is partially negated at the BNB Chain macro level.',
         '#FFFDE7', '#F57F17', ax, fontsize=10, weight='bold')

plt.tight_layout()
plt.savefig('../figures/Diagram2_DecouplingDomains.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.savefig('../figures/Diagram2_DecouplingDomains.pdf', bbox_inches='tight', facecolor='white')
print("Diagram 2 saved: Decoupling Domains")
plt.close()
