# Evaluation script. In VS Code each "# %%" line becomes a runnable cell
# (Jupyter extension -> "Run Cell"), or just run:  python notebooks/evaluation.py
# Run `python data/generate_dataset.py` first.

# %% Setup
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split

try:
    ROOT = Path(__file__).resolve().parents[1]
except NameError:                       # interactive window
    ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT))

from app.fusion import analyze_pair  # noqa: E402

USE_SEMANTIC = False   # set True after `pip install torch transformers` (slower)

# %% Score every pair in data/pairs.csv
pairs = pd.read_csv(ROOT / "data" / "pairs.csv")
rows = []
for r in pairs.itertuples():
    a = (ROOT / "data" / "samples" / r.file_a).read_text()
    b = (ROOT / "data" / "samples" / r.file_b).read_text()
    res = analyze_pair(a, b, use_semantic=USE_SEMANTIC)
    rows.append({"token": res["scores"]["token"], "ast": res["scores"]["ast"],
                 "semantic": res["scores"]["semantic"], "fused": res["overall"]})
scores = pd.concat([pairs, pd.DataFrame(rows)], axis=1)
scores.to_csv(ROOT / "data" / "scores.csv", index=False)
print(scores.groupby("kind")[["token", "ast", "fused"]].mean().round(3))

# %% Metrics: pick the best threshold on a train split, report on the test split
methods = ["token", "ast", "fused"] + (["semantic"] if USE_SEMANTIC else [])
train, test = train_test_split(scores, test_size=0.3, stratify=scores["label"], random_state=42)


def best_threshold(df, col):
    grid = np.linspace(0, 1, 101)
    f1s = [precision_recall_fscore_support(df["label"], df[col] >= t, average="binary",
                                           zero_division=0)[2] for t in grid]
    return grid[int(np.argmax(f1s))]


results = []
for m in methods:
    t = best_threshold(train, m)
    pred = test[m] >= t
    p, r, f1, _ = precision_recall_fscore_support(test["label"], pred, average="binary", zero_division=0)
    results.append({"method": m, "threshold": round(t, 2), "precision": p, "recall": r,
                    "f1": f1, "accuracy": accuracy_score(test["label"], pred)})
table = pd.DataFrame(results).round(3)
print(table.to_string(index=False))

# %% Confusion matrix of the fused score + F1 bar chart
t = table.loc[table.method == "fused", "threshold"].iloc[0]
print("Confusion matrix (rows = truth, cols = predicted) for fused @", t)
print(confusion_matrix(test["label"], test["fused"] >= t))

import matplotlib.pyplot as plt  # noqa: E402
ax = table.set_index("method")[["precision", "recall", "f1", "accuracy"]].plot.bar(figsize=(7, 4), rot=0)
ax.set_ylim(0, 1.05)
ax.set_title("Detection quality on held-out pairs")
plt.tight_layout()
plt.savefig(ROOT / "data" / "results.png", dpi=150)
plt.show()
