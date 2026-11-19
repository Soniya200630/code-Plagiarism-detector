"""Draws docs/architecture_diagram.png (system architecture).

Run from the project root:  python docs/diagram_architecture.py
Needs only matplotlib (already in requirements.txt). Edit the text below to change labels.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

APP = ("#EFEBE2", "#8C8577")
DET = ("#E8E6FA", "#6F6BC2")
SHORT = ("#D9EEE1", "#4C9A6A")
EXT = ("#FDF0DD", "#D08A2E")
INK, SUB, ARROW = "#222222", "#555555", "#555555"

fig, ax = plt.subplots(figsize=(18, 12.4))
ax.set_xlim(0, 18)
ax.set_ylim(-1.9, 10.6)
ax.axis("off")


def region(x, y, w, h, fill, edge, label):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.25",
                                fc=fill, ec=edge, lw=1.4, ls=(0, (5, 3))))
    ax.text(x + 0.25, y + h - 0.35, label, fontsize=13, fontweight="bold", color=edge, va="center")


def box(x, y, w, h, title, sub, style, tsize=12.5, ssize=10):
    fc, ec = style
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.18", fc=fc, ec=ec, lw=1.6))
    if sub:
        ax.text(x + w / 2, y + h * 0.66, title, ha="center", va="center", fontsize=tsize, fontweight="bold", color=INK)
        ax.text(x + w / 2, y + h * 0.30, sub, ha="center", va="center", fontsize=ssize, color=SUB)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=tsize, fontweight="bold", color=INK)
    return (x, y, w, h)


def arrow(p, q, both=False):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=ARROW,
                                                    lw=1.8, shrinkA=0, shrinkB=0, mutation_scale=16))


def line(p, q):
    ax.plot([p[0], q[0]], [p[1], q[1]], color=ARROW, lw=1.8, solid_capstyle="butt")


# ---- top row (application layer)
ty, th = 9.0, 1.1
box(0.5, ty, 3.2, th, "Instructor / User", "Uploads .py files", APP)
box(4.6, ty, 3.4, th, "Web interface", "HTML, CSS, JavaScript", APP)
box(8.9, ty, 3.4, th, "Backend API", "FastAPI (Python)", APP)
box(13.1, ty, 3.0, th, "Database", "SQLite", APP)
arrow((3.7, ty + th / 2), (4.6, ty + th / 2))
arrow((8.0, ty + th / 2), (8.9, ty + th / 2))
arrow((12.3, ty + th / 2), (13.1, ty + th / 2), both=True)

# ---- pipeline regions
region(0.4, 0.8, 8.3, 7.5, "#F6F5FD", DET[1], "Detection pipeline")
region(9.2, 0.8, 6.2, 7.5, "#F3FAF6", SHORT[1], "Shortening pipeline")

# branch from backend
line((10.6, ty), (10.6, 8.65))
line((4.5, 8.65), (12.3, 8.65))
arrow((4.5, 8.65), (4.5, 7.5))
arrow((12.3, 8.65), (12.3, 7.5))

# ---- detection pipeline
box(0.95, 6.6, 7.1, 0.9, "Preprocessing and normalization", "Strip comments, unify identifiers", DET)
tok = box(0.7, 4.7, 2.3, 1.0, "Token analysis", "TF-IDF + cosine", DET, 11, 9.5)
ast_ = box(3.35, 4.7, 2.3, 1.0, "AST analysis", "Syntax tree comparison", DET, 11, 9.5)
sem = box(6.0, 4.7, 2.3, 1.0, "Semantic analysis", "CodeBERT (optional)", DET, 11, 9.5)
for b in (tok, ast_, sem):
    arrow((b[0] + b[2] / 2, 6.6), (b[0] + b[2] / 2, 5.7))
box(0.95, 2.85, 7.1, 0.9, "Similarity engine", "Weighted score fusion (token 0.3, AST 0.4, semantic 0.3)", DET)
for cx in (1.85, 4.5, 7.15):
    arrow((cx, 4.7), (cx, 3.75))
box(0.95, 1.0, 7.1, 0.9, "Score and explanation", "Risk level (Low / Medium / High), matched code regions", DET)
arrow((4.5, 2.85), (4.5, 1.9))

# ---- shortening pipeline
sx, sw, sh = 9.7, 5.2, 0.9
ys = [6.6, 5.2, 3.8, 2.4, 1.0]
titles = [
    ("Rule-based shortener", "Dead code, unused imports, duplicates, comprehensions"),
    ("Section splitter", "Splits big files (~150 lines) at function boundaries"),
    ("LLM rewrite", "Strict prompt: same behaviour, same names, shorter"),
    ("Verifier", "Syntax + signature check; retry once, else fallback"),
    ("Shortened code and report", "Before / after line count, list of changes"),
]
for y, (t, s) in zip(ys, titles):
    box(sx, y, sw, sh, t, s, SHORT)
for hi, lo in zip(ys[:-1], ys[1:]):
    arrow((12.3, hi), (12.3, lo + sh))

# Groq external box
box(15.9, 3.8, 1.85, 0.9, "Groq API", "Llama 3.3 70B", EXT, 11.5, 9.5)
arrow((sx + sw, 4.25), (15.9, 4.25), both=True)
ax.text(15.75, 4.9, "HTTPS", ha="center", fontsize=9, color=SUB)
ax.text(16.82, 3.55, "external service", ha="center", va="top", fontsize=9, color=EXT[1], style="italic")

# ---- dashboard
box(2.6, -0.85, 11.6, 1.0, "Dashboard and report (instructor review)",
    "Similarity matrix, ranked pairs, side-by-side highlights, shortened code view", APP)
arrow((4.5, 1.0), (4.5, 0.15))
arrow((12.3, 1.0), (12.3, 0.15))

# ---- legend
for i, (name, st) in enumerate([("Application layer", APP), ("Detection pipeline", DET),
                                ("Shortening pipeline", SHORT), ("External service", EXT)]):
    x = 3.0 + i * 3.4
    ax.add_patch(Rectangle((x, -1.6 - 0.13), 0.35, 0.26, fc=st[0], ec=st[1], lw=1.4))
    ax.text(x + 0.5, -1.6, name, va="center", fontsize=10.5, color=SUB)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "architecture_diagram.png")
plt.savefig(OUT, dpi=170, bbox_inches="tight", pad_inches=0.25, facecolor="white")
print("saved", OUT)
