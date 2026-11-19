"""FastAPI backend.  Run from the project root:

    uvicorn app.main:app --reload
then open http://127.0.0.1:8000
"""
from itertools import combinations
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config  # noqa: F401  (loads .env)
from . import db
from .ai_compress import AIError, MissingKey, ai_shorten
from .compress import compress
from .fusion import analyze_pair

FRONTEND = Path(__file__).resolve().parents[1] / "frontend"

app = FastAPI(title="Code Plagiarism Detector")
db.init_db()


class CompareReq(BaseModel):
    a: int
    b: int
    semantic: bool = False


class AnalyzeReq(BaseModel):
    ids: Optional[List[int]] = None   # None = every uploaded file
    semantic: bool = False


class CompressReq(BaseModel):
    id: Optional[int] = None      # an uploaded submission ...
    code: Optional[str] = None    # ... or raw code
    target_pct: int = 30          # AI mode: aim for this % of the original length


@app.post("/api/upload")
async def upload(files: List[UploadFile] = File(...)):
    saved, skipped = [], []
    for f in files:
        if not (f.filename or "").endswith(".py"):
            skipped.append(f.filename)
            continue
        code = (await f.read()).decode("utf-8", errors="replace")
        saved.append({"id": db.add_submission(f.filename, code), "name": f.filename})
    return {"saved": saved, "skipped": skipped}


@app.get("/api/submissions")
def submissions():
    return db.list_submissions()


@app.delete("/api/submissions")
def clear():
    db.clear_all()
    return {"ok": True}


@app.post("/api/compare")
def compare(req: CompareReq):
    a, b = db.get_submission(req.a), db.get_submission(req.b)
    if not a or not b:
        raise HTTPException(404, "submission not found")
    report = analyze_pair(a["code"], b["code"], req.semantic)
    report.update(
        a={"id": a["id"], "name": a["name"]}, b={"id": b["id"], "name": b["name"]},
        code_a=a["code"], code_b=b["code"],
    )
    report["report_id"] = db.save_report(a["id"], b["id"], report)
    return report


@app.get("/api/report/{rid}")
def report(rid: int):
    r = db.get_report(rid)
    if not r:
        raise HTTPException(404, "report not found")
    return r


@app.post("/api/analyze")
def analyze(req: AnalyzeReq):
    subs = db.list_submissions(req.ids, with_code=True)
    if len(subs) < 2:
        raise HTTPException(400, "upload at least two files")
    pairs = []
    for a, b in combinations(subs, 2):
        r = analyze_pair(a["code"], b["code"], req.semantic)
        pairs.append({"a": a["id"], "b": b["id"], "a_name": a["name"], "b_name": b["name"],
                      "scores": r["scores"], "overall": r["overall"], "risk": r["risk"]})
    pairs.sort(key=lambda p: p["overall"], reverse=True)
    return {"submissions": [{"id": s["id"], "name": s["name"]} for s in subs], "pairs": pairs}


def _load_code(req: CompressReq):
    if req.code is not None:
        return req.code, "pasted code"
    sub = db.get_submission(req.id) if req.id is not None else None
    if not sub:
        raise HTTPException(404, "submission not found")
    return sub["code"], sub["name"]


@app.post("/api/compress")
def shorten(req: CompressReq):
    code, name = _load_code(req)
    return {**compress(code), "name": name}


@app.post("/api/compress/ai")
def shorten_ai(req: CompressReq):
    code, name = _load_code(req)
    try:
        return {**ai_shorten(code, req.target_pct), "name": name}
    except MissingKey as e:
        raise HTTPException(400, str(e))
    except AIError as e:
        raise HTTPException(502, str(e))


# Serve the UI last so it doesn't shadow /api routes
app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")
