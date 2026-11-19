"""Draws docs/flowchart.png (working flow of the system).

Run from the project root:  python docs/diagram_flowchart.py
Needs only matplotlib (already in requirements.txt). Edit the text below to change labels.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyBboxPatch, Polygon

APP = ("#EFEBE2", "#8C8577")
DET = ("#E8E6FA", "#6F6BC2")
SHORT = ("#D9EEE1", "#4C9A6A")
EXT = ("#FDF0DD", "#D08A2E")
END = ("#E4E6EB", "#6B7280")
INK, SUB, ARROW = "#222222", "#555555", "#555555"

fig, ax = plt.subplots(figsize=(18, 13.6))
ax.set_xlim(0, 18)
ax.set_ylim(-0.5, 12.9)
ax.axis("off")


def region(x, y, w, h, fill, edge, label):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.25",
                                fc=fill, ec=edge, lw=1.4, ls=(0, (5, 3))))
    ax.text(x + 0.25, y + h - 0.3, label, fontsize=13, fontweight="bold", color=edge, va="center")


def box(cx, cy, w, h, text, style, size=11.5):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0,rounding_size=0.15",
                                fc=style[0], ec=style[1], lw=1.6))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=size, color=INK, linespacing=1.35)


def oval(cx, cy, w, h, text):
    ax.add_patch(Ellipse((cx, cy), w, h, fc=END[0], ec=END[1], lw=1.6))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=11.5, fontweight="bold", color=INK)


def diamond(cx, cy, w, h, text, style):
    ax.add_patch(Polygon([(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)],
                         closed=True, fc=style[0], ec=style[1], lw=1.6))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=10.5, color=INK, linespacing=1.3)


def arrow(p, q):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color=ARROW, lw=1.8,
                                                    shrinkA=0, shrinkB=0, mutation_scale=16))


def line(p, q):
    ax.plot([p[0], q[0]], [p[1], q[1]], color=ARROW, lw=1.8, solid_capstyle="butt")


LX, RX = 3.8, 11.2
region(0.9, 0.85, 5.8, 9.45, "#F6F5FD", DET[1], "Plagiarism detection")
region(8.3, 0.85, 9.6, 9.45, "#F3FAF6", SHORT[1], "Code shortening")

# top
oval(7.5, 12.2, 2.4, 0.7, "Start")
box(7.5, 11.2, 4.8, 0.8, "Instructor uploads Python files", APP)
arrow((7.5, 11.85), (7.5, 11.6))
line((7.5, 10.8), (7.5, 10.55))
line((LX, 10.55), (RX, 10.55))
arrow((LX, 10.55), (LX, 9.65))
arrow((RX, 10.55), (RX, 9.65))

# left lane: detection
ly = [9.2, 7.8, 6.4, 5.0, 3.6, 2.2]
ltxt = ["Preprocess and normalize\n(remove comments, unify identifiers)",
        "Token (TF-IDF), AST and\nsemantic (CodeBERT) similarity",
        "Weighted score fusion",
        "Assign risk level\n(Low / Medium / High)",
        "Highlight matched\ncode regions",
        "Show ranked pairs, heatmap\nand side-by-side view"]
for y, t in zip(ly, ltxt):
    box(LX, y, 5.0, 0.9, t, DET)
for a, b in zip(ly[:-1], ly[1:]):
    arrow((LX, a - 0.45), (LX, b + 0.45))

# right lane: shortening
box(RX, 9.2, 5.4, 0.9, "Rule-based shortening\n(dead code, unused imports, duplicates, loops)", SHORT)
box(RX, 7.8, 5.4, 0.9, "Optional AI mode: split code into\nsections (~150 lines each)", SHORT)
box(RX, 6.4, 5.4, 0.9, "Send each section to Groq LLM\n(rewrite shorter, keep behaviour)", SHORT)
arrow((RX, 8.75), (RX, 8.25))
arrow((RX, 7.35), (RX, 6.85))
diamond(RX, 4.6, 4.4, 1.7, "Passes syntax and\nsignature check?", SHORT)
arrow((RX, 5.95), (RX, 5.45))
box(RX, 2.9, 5.4, 0.9, "Assemble sections, remove unused\nimports, verify final code", SHORT)
arrow((RX, 3.75), (RX, 3.35))
ax.text(RX + 0.15, 3.6, "Yes", fontsize=11, color=SUB, va="center")
box(RX, 1.6, 5.4, 0.9, "Show shortened code with\nbefore / after line count", SHORT)
arrow((RX, 2.45), (RX, 2.05))

# retry branch
box(16.0, 4.6, 3.3, 1.3, "Retry once with the error.\nIf it still fails, keep the\nrule-based version", EXT, 10.5)
arrow((RX + 2.2, 4.6), (14.35, 4.6))
ax.text(13.05, 4.85, "No", fontsize=11, color=SUB, ha="center")
line((16.0, 3.95), (16.0, 2.9))
arrow((16.0, 2.9), (RX + 2.7, 2.9))

# end
oval(7.5, 0.05, 3.9, 0.75, "Instructor reviews results")
line((LX, 1.75), (LX, 0.05))
arrow((LX, 0.05), (5.55, 0.05))
line((RX, 1.15), (RX, 0.05))
arrow((RX, 0.05), (9.45, 0.05))

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flowchart.png")
plt.savefig(OUT, dpi=170, bbox_inches="tight", pad_inches=0.25, facecolor="white")
print("saved", OUT)
