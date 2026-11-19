# Trains a classifier on the similarity scores and compares it with hand-set weights.
# In VS Code each "# %%" line is a runnable cell, or just run:  python notebooks/train_classifier.py
# Run `python data/generate_dataset.py` first.
#
# What it does
#   1. scores every pair in data/pairs.csv  (token, ast and optionally semantic)
#   2. cross-validates (grouped by problem, so one problem never sits in both train and test)
#        - single score + best threshold          (token only, ast only)
#        - the hand-weighted fusion from app/fusion.py + best threshold
#        - Logistic Regression and Random Forest on the scores   <- the learned models
#   3. prints the ablation table, saves a ROC chart and the final model to models/classifier.joblib

# %% Setup
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_recall_fscore_support, roc_auc_score, roc_curve)
from sklearn.model_selection import GroupKFold

try:
    ROOT = Path(__file__).resolve().parents[1]
except NameError:                       # interactive window
    ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT))

from app.fusion import analyze_pair  # noqa: E402

USE_SEMANTIC = False   # True needs torch + transformers (slow first run)

# %% Score every pair
pairs = pd.read_csv(ROOT / "data" / "pairs.csv")
rows = []
for r in pairs.itertuples():
    a = (ROOT / "data" / "samples" / r.file_a).read_text()
    b = (ROOT / "data" / "samples" / r.file_b).read_text()
    s = analyze_pair(a, b, use_semantic=USE_SEMANTIC)["scores"]
    rows.append({"token": s["token"], "ast": s["ast"] or 0.0, "semantic": s["semantic"]})
df = pd.concat([pairs, pd.DataFrame(rows)], axis=1)
df["fused"] = 0.3 * df["token"] + 0.4 * df["ast"] if not USE_SEMANTIC else \
    0.3 * df["token"] + 0.4 * df["ast"] + 0.3 * df["semantic"].fillna(0)
df["group"] = df["file_a"].str.split("_").str[0]          # problem name: fib, prime, sort, pal, freq
FEATURES = ["token", "ast"] + (["semantic"] if USE_SEMANTIC else [])
y = df["label"].to_numpy()
print(f"{len(df)} pairs, {y.sum()} copied, {len(y) - y.sum()} not copied, groups: {sorted(df.group.unique())}")

# %% Helpers
def best_threshold(scores, labels):
    grid = np.linspace(0, 1, 101)
    f1s = [precision_recall_fscore_support(labels, scores >= t, average="binary", zero_division=0)[2] for t in grid]
    return grid[int(np.argmax(f1s))]


def summarize(name, y_true, y_pred, y_score):
    p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="binary", zero_division=0)
    try:
        auc = roc_auc_score(y_true, y_score)
    except ValueError:
        auc = float("nan")
    return {"method": name, "precision": p, "recall": r, "f1": f1,
            "accuracy": accuracy_score(y_true, y_pred), "roc_auc": auc}


# %% Grouped cross-validation (every problem is held out once)
gkf = GroupKFold(n_splits=df["group"].nunique())
methods = {}      # name -> (true labels, predictions, scores) collected over all folds


def add(name, yt, yp, ys):
    t = methods.setdefault(name, ([], [], []))
    t[0].extend(yt); t[1].extend(yp); t[2].extend(ys)


for train_idx, test_idx in gkf.split(df, y, df["group"]):
    tr, te = df.iloc[train_idx], df.iloc[test_idx]
    ytr, yte = y[train_idx], y[test_idx]

    # threshold-based baselines
    for col, name in [("token", "Token only (threshold)"), ("ast", "AST only (threshold)"),
                      ("fused", "Hand-weighted fusion (threshold)")]:
        t = best_threshold(tr[col].to_numpy(), ytr)
        add(name, yte, (te[col] >= t).astype(int), te[col])

    # learned models
    for name, model in [("Logistic Regression (learned)", LogisticRegression(class_weight="balanced")),
                        ("Random Forest (learned)", RandomForestClassifier(n_estimators=200, random_state=42,
                                                                          class_weight="balanced"))]:
        model.fit(tr[FEATURES], ytr)
        add(name, yte, model.predict(te[FEATURES]), model.predict_proba(te[FEATURES])[:, 1])

table = pd.DataFrame([summarize(n, *map(np.array, v)) for n, v in methods.items()]).round(3)
print("\nAblation / comparison (grouped cross-validation):")
print(table.to_string(index=False))
table.to_csv(ROOT / "data" / "classifier_results.csv", index=False)

# %% Per-kind errors for the best learned model (where does it fail?)
lr_pred = np.array(methods["Logistic Regression (learned)"][1])
# gkf yields folds in a different order than df, so rebuild the matching order
order = np.concatenate([test_idx for _, test_idx in gkf.split(df, y, df["group"])])
errs = df.iloc[order].assign(pred=lr_pred)
errs["correct"] = errs["pred"] == errs["label"]
print("\nAccuracy of Logistic Regression by kind of pair:")
print(errs.groupby("kind")["correct"].mean().round(2).to_string())

# %% ROC curves
import matplotlib.pyplot as plt  # noqa: E402

fig, ax = plt.subplots(figsize=(6, 5))
for name, (yt, yp, ys) in methods.items():
    yt, ys = np.array(yt), np.array(ys)
    if len(set(yt)) > 1:
        fpr, tpr, _ = roc_curve(yt, ys)
        ax.plot(fpr, tpr, label=f"{name} (AUC {roc_auc_score(yt, ys):.2f})")
ax.plot([0, 1], [0, 1], "--", color="grey")
ax.set_xlabel("False positive rate"); ax.set_ylabel("True positive rate"); ax.set_title("ROC curves")
ax.legend(fontsize=7, loc="lower right"); plt.tight_layout()
plt.savefig(ROOT / "data" / "roc.png", dpi=150)
plt.show()

# %% Train the final model on ALL pairs and save it (the web app uses it when USE_LEARNED_MODEL=1 is set in .env)
final = LogisticRegression(class_weight="balanced").fit(df[FEATURES].to_numpy(), y)
joblib.dump({"model": final, "features": FEATURES}, ROOT / "models" / "classifier.joblib")
print("\nsaved models/classifier.joblib  coefficients:", dict(zip(FEATURES, final.coef_[0].round(2))))
