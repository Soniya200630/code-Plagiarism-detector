"""Step 5 - score fusion, risk level and explanation.

Default: hand-weighted fusion (WEIGHTS below).
Optional: set USE_LEARNED_MODEL=1 in .env to use the Logistic Regression trained by
notebooks/train_classifier.py (models/classifier.joblib). It is only used when the semantic
score is off, because the model was trained on the token + AST scores.
"""
import os
from pathlib import Path

from . import config  # noqa: F401  (loads .env)
from .ast_sim import ast_compare
from .semantic_sim import semantic_sim
from .token_sim import token_sim

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "classifier.joblib"
_model = {"loaded": False, "obj": None}
WEIGHTS = {"token": 0.3, "ast": 0.4, "semantic": 0.3}
LOW_MAX, MEDIUM_MAX = 0.50, 0.75   # < 0.50 Low, < 0.75 Medium, else High


def fuse(scores: dict, weights: dict = None) -> float:
    """Weighted average; scores that are None are skipped and weights re-normalised."""
    w = weights or WEIGHTS
    avail = {k: v for k, v in scores.items() if v is not None and k in w}
    if not avail:
        return 0.0
    total = sum(w[k] for k in avail)
    return sum(w[k] * v for k, v in avail.items()) / total


def _learned():
    if os.environ.get("USE_LEARNED_MODEL", "").strip() not in ("1", "true", "yes"):
        return None
    if not _model["loaded"]:
        _model["loaded"] = True
        try:
            import joblib
            _model["obj"] = joblib.load(MODEL_PATH)
        except Exception as e:
            print(f"[fusion] learned model not available: {e}")
    return _model["obj"]


def risk_level(score: float) -> str:
    if score < LOW_MAX:
        return "Low"
    if score < MEDIUM_MAX:
        return "Medium"
    return "High"


def analyze_pair(a: str, b: str, use_semantic: bool = False) -> dict:
    ast_res = ast_compare(a, b)
    scores = {
        "token": token_sim(a, b),
        "ast": ast_res["score"],
        "semantic": semantic_sim(a, b) if use_semantic else None,
    }
    overall, method = fuse(scores), "weighted"
    bundle = _learned()
    if bundle and scores["semantic"] is None and scores["ast"] is not None \
            and bundle["features"] == ["token", "ast"]:
        overall = float(bundle["model"].predict_proba([[scores["token"], scores["ast"]]])[0, 1])
        method = "learned"
    return {
        "method": method,
        "scores": {k: (None if v is None else round(v, 4)) for k, v in scores.items()},
        "overall": round(overall, 4),
        "risk": risk_level(overall),
        "regions": ast_res["regions"],
        "error": ast_res.get("error"),
    }
