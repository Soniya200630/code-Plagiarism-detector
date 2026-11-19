"""Step 4 - semantic similarity with code embeddings (CodeBERT by default).

Optional: needs `pip install torch transformers`. If they are missing, or the
model can't be downloaded, semantic_sim() returns None and the fusion step
simply re-weights the other two scores.

Env vars:
  SEM_MODEL  - HF model name (default microsoft/codebert-base;
               try microsoft/unixcoder-base for better similarity behaviour)
  SEM_FLOOR  - raw cosine values below this map to 0. Mean-pooled CodeBERT
               vectors are all fairly similar (cos ~0.9 even for unrelated
               code), so we rescale (cos-FLOOR)/(1-FLOOR). Tune it with
               notebooks/evaluation.py.
"""
import os
from functools import lru_cache

import numpy as np

from .preprocess import canonicalize

MODEL_NAME = os.getenv("SEM_MODEL", "microsoft/codebert-base")
FLOOR = float(os.getenv("SEM_FLOOR", "0.80"))
_state = {"tok": None, "model": None, "failed": False}


def _load() -> bool:
    if _state["model"] is not None:
        return True
    if _state["failed"]:
        return False
    try:
        from transformers import AutoModel, AutoTokenizer
        _state["tok"] = AutoTokenizer.from_pretrained(MODEL_NAME)
        _state["model"] = AutoModel.from_pretrained(MODEL_NAME).eval()
        return True
    except Exception as e:  # ImportError, no internet, ...
        print(f"[semantic_sim] disabled: {e}")
        _state["failed"] = True
        return False


@lru_cache(maxsize=512)
def _embed(code: str) -> np.ndarray:
    import torch
    text = canonicalize(code)
    enc = _state["tok"](text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        hidden = _state["model"](**enc).last_hidden_state      # (1, T, H)
    mask = enc["attention_mask"].unsqueeze(-1)
    vec = (hidden * mask).sum(1) / mask.sum(1)                 # mean pooling
    return vec[0].numpy()
    # Note: files > 512 tokens are truncated. Chunking is a possible improvement.


def semantic_sim(a: str, b: str):
    if not _load():
        return None
    va, vb = _embed(a), _embed(b)
    cos = float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb)))
    return max(0.0, min(1.0, (cos - FLOOR) / (1 - FLOOR)))
