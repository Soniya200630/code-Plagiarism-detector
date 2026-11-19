"""AI-assisted shortening with the Groq API (OpenAI-compatible endpoint).

Pipeline
  1. free rule-based pass (app/compress.py) removes the easy stuff
  2. the result is split into sections at top-level definitions (~150 lines each)
  3. every section is sent to Groq with strict rules ("same behaviour, same names")
  4. every reply is CHECKED: it must parse, and every top-level function/class/variable
     of the original must still exist with the same signature. One retry with the error
     message; if it still fails, that section keeps its rule-based version.
  5. sections are joined and run through the rule-based pass again (cleans imports)

Setup: put your key in a `.env` file in the project root:
    GROQ_API_KEY=gsk_...
    GROQ_MODEL=llama-3.3-70b-versatile      (optional)
Get a key at https://console.groq.com/keys . Model names change over time,
see https://console.groq.com/docs/models if you get a "model not found" error.

PRIVACY: the code you shorten is sent to Groq's servers.
"""
import ast
import os
import re
import time

import httpx

from . import config  # noqa: F401  (loads .env)
from .compress import compress

API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.3-70b-versatile"
CHUNK_LINES = 150
MIN_LINES_FOR_AI = 15

SYSTEM = """You are a careful Python refactoring tool.
Rewrite the given code so it is as SHORT and clean as possible while behaving EXACTLY the same.
Rules:
- Keep every top-level function, class and variable name, and every function signature
  (parameter names, order, defaults) unchanged. Other code depends on them.
- Keep return values, printed output and side effects identical.
- Shorten by: list/dict/set comprehensions, built-ins (sum, any, all, max, min, zip, enumerate),
  the standard library, merging repeated logic into one helper, simpler control flow,
  removing redundant variables. Do not change the algorithm's meaning.
- No comments, no docstrings, no explanations.
- Only standard-library imports. If you need one, put it at the top of your output.
- Reply with ONLY the complete Python code in a single ```python block."""


class AIError(Exception):
    pass


class MissingKey(AIError):
    pass


# ------------------------------------------------------------------ Groq call
def _explain(r: httpx.Response) -> str:
    try:
        msg = r.json()["error"]["message"]
    except Exception:
        msg = r.text[:200]
    if r.status_code == 401:
        return "Groq rejected the API key (401). Check GROQ_API_KEY in your .env file."
    if r.status_code in (400, 404):
        return f"Groq request failed ({r.status_code}): {msg}. If it mentions the model, set GROQ_MODEL."
    if r.status_code == 429:
        return "Groq rate limit reached (429). Wait a minute and try again, or use a smaller file."
    return f"Groq error {r.status_code}: {msg}"


def _chat(messages, model, key) -> str:
    for attempt in range(3):
        try:
            r = httpx.post(API_URL, headers={"Authorization": f"Bearer {key}"}, timeout=120,
                           json={"model": model, "messages": messages, "temperature": 0})
        except httpx.HTTPError as e:
            raise AIError(f"Could not reach Groq: {e.__class__.__name__}") from e
        if r.status_code == 429 and attempt < 2:
            try:
                wait = float(r.headers.get("retry-after", 5))
            except ValueError:
                wait = 5
            time.sleep(min(wait, 20))
            continue
        if r.status_code >= 400:
            raise AIError(_explain(r))
        return r.json()["choices"][0]["message"]["content"]
    raise AIError("Groq did not respond")


# ------------------------------------------------------------------ verification
def _sig(fn):
    a = fn.args
    names = [x.arg for x in a.posonlyargs + a.args + a.kwonlyargs]
    if a.vararg:
        names.append("*" + a.vararg.arg)
    if a.kwarg:
        names.append("**" + a.kwarg.arg)
    return (tuple(names), len(a.defaults))


def _surface(tree) -> dict:
    """Public 'shape' of a module: names + signatures of top-level defs/classes/variables."""
    out = {}
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out[n.name] = ("def", _sig(n))
        elif isinstance(n, ast.ClassDef):
            methods = tuple(sorted((m.name, _sig(m)) for m in n.body
                                   if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))))
            out[n.name] = ("class", methods)
        elif isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    out[t.id] = ("var",)
    return out


def _check(original: str, new: str):
    """Return an error message, or None if `new` keeps the original's public surface."""
    try:
        new_tree = ast.parse(new)
    except SyntaxError as e:
        return f"the code has a syntax error on line {e.lineno}: {e.msg}"
    old_s, new_s = _surface(ast.parse(original)), _surface(new_tree)
    for name, sig in old_s.items():
        if name not in new_s:
            return f"top-level name '{name}' is missing"
        if new_s[name] != sig:
            return f"the signature of '{name}' changed (names, order and defaults must stay the same)"
    return None


def _extract(reply: str):
    reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.S)
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", reply, flags=re.S)
    if blocks:
        return max(blocks, key=len).strip("\n")
    return reply.strip() or None


# ------------------------------------------------------------------ chunking
def _split(code: str):
    tree = ast.parse(code)
    lines = code.splitlines()
    imports, chunks, cur, cur_len = [], [], [], 0
    for node in tree.body:
        start = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
        seg = "\n".join(lines[start - 1:node.end_lineno])
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(seg)
            continue
        cur.append(seg)
        cur_len += node.end_lineno - start + 1
        if cur_len >= CHUNK_LINES:
            chunks.append("\n\n".join(cur))
            cur, cur_len = [], 0
    if cur:
        chunks.append("\n\n".join(cur))
    return imports, chunks


def _rewrite_chunk(chunk, imports, other_names, model, key, target_pct):
    ctx = ""
    if imports:
        ctx += "Imports already present at the top of the file (do not repeat them):\n" + "\n".join(imports) + "\n\n"
    if other_names:
        ctx += "Other top-level names defined elsewhere in the file (do not redefine): " + ", ".join(other_names) + "\n\n"
    user = (f"{ctx}Aim for roughly {target_pct}% of the original length if that is possible without "
            f"changing behaviour; never sacrifice correctness for length.\n\nCode to rewrite:\n```python\n{chunk}\n```")
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]
    err = "no code found"
    for _ in range(2):
        reply = _chat(msgs, model, key)
        code = _extract(reply)
        err = _check(chunk, code) if code else "no code block found in the reply"
        if not err:
            return code, None
        msgs += [{"role": "assistant", "content": reply},
                 {"role": "user", "content": f"That failed a check: {err}. Fix it and reply with the "
                                             f"complete code in a single ```python block."}]
    return None, err


# ------------------------------------------------------------------ public API
def ai_shorten(code: str, target_pct: int = 30, model: str = None) -> dict:
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if not key:
        raise MissingKey("GROQ_API_KEY is not set. Create a .env file in the project root containing "
                         "GROQ_API_KEY=your_key and restart the server.")
    model = model or os.environ.get("GROQ_MODEL", DEFAULT_MODEL)

    base = compress(code)          # free first pass
    if not base["ok"]:
        return {**base, "used_ai": False, "notes": []}
    src = base["compressed"]
    result = {**base, "used_ai": False, "model": model, "notes": []}
    if len(src.splitlines()) < MIN_LINES_FOR_AI:
        result["notes"].append("File is already short after the rule-based pass, so AI was skipped.")
        return result

    imports, chunks = _split(src)
    names = list(_surface(ast.parse(src)))
    done, notes, new_chunks = 0, [], []
    for i, chunk in enumerate(chunks, 1):
        own = set(_surface(ast.parse(chunk)))
        new, err = _rewrite_chunk(chunk, imports, [n for n in names if n not in own], model, key, target_pct)
        if new is None:
            notes.append(f"Section {i}/{len(chunks)} kept as-is: AI reply failed a check ({err}).")
            new_chunks.append(chunk)
        elif len(new.splitlines()) >= len(chunk.splitlines()):
            notes.append(f"Section {i}/{len(chunks)} kept as-is: AI version was not shorter.")
            new_chunks.append(chunk)
        else:
            done += 1
            new_chunks.append(new)

    if done == 0:
        result["notes"] = notes or ["AI could not make it shorter."]
        return result

    assembled = "\n".join(imports) + "\n\n" + "\n\n".join(new_chunks)
    final = compress(assembled)    # tidies imports / formatting again
    problem = None
    if not final["ok"]:
        problem = final.get("error", "assembled code did not parse")
    else:
        problem = _check(src, final["compressed"])
    if problem:
        notes.append(f"AI result was discarded ({problem}); showing the rule-based result instead.")
        result["notes"] = notes
        return result

    out = final["compressed"]
    before = base["before"]
    after = len(out.splitlines())
    changes = list(base["changes"]) + [{"what": f"AI rewrote {done} of {len(chunks)} section(s) with {model}", "count": None}]
    return {**base, "compressed": out, "after": after, "changes": changes, "used_ai": True, "model": model,
            "notes": notes, "saved_pct": round(100 * (before - after) / before) if before else 0,
            "bytes_after": len(out.encode())}
