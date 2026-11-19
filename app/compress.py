"""Shortens a Python file without changing what it does.

Rule-based (no AI model, works offline). Each rule is a small, safe rewrite:
  * removes comments, docstrings and extra blank lines / formatting
  * removes unused imports
  * removes unreachable code (after return / raise / break / continue)
  * removes `if True` / `if False` blocks and useless `pass` / `else: pass`
  * `if x > 3: return True else: return False`   ->  `return x > 3`
  * `r = []` + `for t in it: r.append(f(t))`      ->  `r = [f(t) for t in it]`
  * duplicate functions (identical apart from the name) -> alias of the first

Use it from the web UI ("Shorten" button) or the command line:
    python -m app.compress path/to/file.py      (writes file.short.py)

IMPORTANT: real reduction depends on how messy the input is. Comment-heavy,
repetitive code can shrink by 30-60%; already tight code shrinks very little.
Always re-run your tests on the shortened file.
"""
import ast
import copy
from collections import Counter

from .preprocess import _strip_docstrings

_BODY_FIELDS = ("body", "orelse", "finalbody")


# ------------------------------------------------------------------ helpers
def _is_const(node, value) -> bool:
    return isinstance(node, ast.Constant) and node.value is value


def _count(node, name: str) -> int:
    return sum(1 for n in ast.walk(node) if isinstance(n, ast.Name) and n.id == name)


def _blocks(tree):
    """Yield (owner, field, statement_list) for every statement list in the tree."""
    for node in ast.walk(tree):
        for f in _BODY_FIELDS:
            v = getattr(node, f, None)
            if isinstance(v, list) and v and isinstance(v[0], ast.stmt):
                yield node, f, v


def _docstring_lines(tree) -> int:
    total = 0
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            b = n.body
            if (b and isinstance(b[0], ast.Expr) and isinstance(b[0].value, ast.Constant)
                    and isinstance(b[0].value.value, str)):
                total += b[0].end_lineno - b[0].lineno + 1
    return total


# ------------------------------------------------------------------ rules
def _dead_ifs(tree, log):
    class T(ast.NodeTransformer):
        def visit_If(self, node):
            self.generic_visit(node)
            if isinstance(node.test, ast.Constant):
                log["Removed constant conditions (if True / if False)"] += 1
                return node.body if node.test.value else (node.orelse or None)
            return node
    return T().visit(tree)


def _unreachable(tree, log):
    for node, f, stmts in list(_blocks(tree)):
        for i, s in enumerate(stmts):
            if isinstance(s, (ast.Return, ast.Raise, ast.Break, ast.Continue)) and i + 1 < len(stmts):
                log["Removed unreachable statements"] += len(stmts) - i - 1
                setattr(node, f, stmts[:i + 1])
                break


def _unused_imports(tree, log):
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    if "__all__" in used:
        return
    for node, f, stmts in list(_blocks(tree)):
        new = []
        for s in stmts:
            if isinstance(s, (ast.Import, ast.ImportFrom)) and not (
                    isinstance(s, ast.ImportFrom) and s.module == "__future__"):
                keep = []
                for a in s.names:
                    bound = a.asname or a.name.split(".")[0]
                    if a.name == "*" or bound in used:
                        keep.append(a)
                    else:
                        log["Removed unused imports"] += 1
                if keep:
                    s.names = keep
                    new.append(s)
            else:
                new.append(s)
        if len(new) != len(stmts):
            setattr(node, f, new)


def _simplify_bool_returns(tree, log):
    def is_ret(s, v):
        return isinstance(s, ast.Return) and _is_const(s.value, v)

    def cond_ok(t):  # only expressions that are already real booleans
        return isinstance(t, ast.Compare) or (isinstance(t, ast.UnaryOp) and isinstance(t.op, ast.Not))

    def make(test, negate):
        return ast.Return(value=ast.UnaryOp(op=ast.Not(), operand=test) if negate else test)

    for node, f, stmts in list(_blocks(tree)):
        out, i, changed = [], 0, False
        while i < len(stmts):
            s = stmts[i]
            if isinstance(s, ast.If) and cond_ok(s.test) and len(s.body) == 1:
                b = s.body[0]
                if len(s.orelse) == 1 and ((is_ret(b, True) and is_ret(s.orelse[0], False))
                                           or (is_ret(b, False) and is_ret(s.orelse[0], True))):
                    out.append(make(s.test, is_ret(b, False)))
                    log["Simplified if/else that returns True/False"] += 1
                    changed = True
                    i += 1
                    continue
                if not s.orelse and i + 1 < len(stmts) and ((is_ret(b, True) and is_ret(stmts[i + 1], False))
                                                            or (is_ret(b, False) and is_ret(stmts[i + 1], True))):
                    out.append(make(s.test, is_ret(b, False)))
                    log["Simplified if/else that returns True/False"] += 1
                    changed = True
                    i += 2
                    continue
            out.append(s)
            i += 1
        if changed:
            setattr(node, f, out)


def _loops_to_comprehensions(tree, log):
    parents = {c: p for p in ast.walk(tree) for c in ast.iter_child_nodes(p)}

    def scope_of(n):
        while n in parents:
            n = parents[n]
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.Module)):
                return n
        return tree

    def append_arg(stmt, r):
        if (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)
                and isinstance(stmt.value.func, ast.Attribute) and stmt.value.func.attr == "append"
                and isinstance(stmt.value.func.value, ast.Name) and stmt.value.func.value.id == r
                and len(stmt.value.args) == 1 and not stmt.value.keywords):
            return stmt.value.args[0]
        return None

    for node, f, stmts in list(_blocks(tree)):
        out, i, changed = [], 0, False
        while i < len(stmts):
            s = stmts[i]
            if (isinstance(s, ast.Assign) and len(s.targets) == 1 and isinstance(s.targets[0], ast.Name)
                    and isinstance(s.value, ast.List) and not s.value.elts
                    and i + 1 < len(stmts) and isinstance(stmts[i + 1], ast.For) and not stmts[i + 1].orelse):
                r, loop = s.targets[0].id, stmts[i + 1]
                elt, ifs = None, []
                if len(loop.body) == 1:
                    elt = append_arg(loop.body[0], r)
                    inner = loop.body[0]
                    if elt is None and isinstance(inner, ast.If) and not inner.orelse and len(inner.body) == 1:
                        elt, ifs = append_arg(inner.body[0], r), [inner.test]
                if elt is not None and _count(loop, r) == 1:
                    tnames = {n.id for n in ast.walk(loop.target) if isinstance(n, ast.Name)}
                    sc = scope_of(loop)
                    # loop variable must not be used anywhere else (a comprehension doesn't leak it)
                    if all(_count(sc, t) == _count(loop, t) for t in tnames):
                        comp = ast.ListComp(elt=elt, generators=[ast.comprehension(
                            target=loop.target, iter=loop.iter, ifs=ifs, is_async=0)])
                        out.append(ast.Assign(targets=s.targets, value=comp))
                        log["Turned append-loops into list comprehensions"] += 1
                        changed = True
                        i += 2
                        continue
            out.append(s)
            i += 1
        if changed:
            setattr(node, f, out)


def _dedupe_functions(tree, log):
    for node, f, stmts in list(_blocks(tree)):
        if isinstance(node, ast.ClassDef):
            continue
        seen, out, changed = {}, [], False
        for s in stmts:
            if isinstance(s, ast.FunctionDef) and not s.decorator_list and _count(s, s.name) == 0:
                clone = copy.deepcopy(s)
                clone.name = "_"
                key = ast.dump(clone)
                if key in seen:
                    out.append(ast.Assign(targets=[ast.Name(id=s.name, ctx=ast.Store())],
                                          value=ast.Name(id=seen[key], ctx=ast.Load())))
                    log["Merged duplicate functions"] += 1
                    changed = True
                    continue
                seen[key] = s.name
            out.append(s)
        if changed:
            setattr(node, f, out)


def _remove_pass(tree, log):
    for node, f, stmts in list(_blocks(tree)):
        if f == "orelse" and all(isinstance(s, ast.Pass) for s in stmts):
            setattr(node, f, [])
            log["Removed useless pass statements"] += 1
        elif len(stmts) > 1:
            new = [s for s in stmts if not isinstance(s, ast.Pass)]
            if len(new) != len(stmts):
                log["Removed useless pass statements"] += len(stmts) - len(new)
                setattr(node, f, new)


def _fix_empty(tree):
    for node in ast.walk(tree):
        v = getattr(node, "body", None)
        if isinstance(v, list) and not v and not isinstance(node, ast.Module):
            v.append(ast.Pass())


# ------------------------------------------------------------------ public API
def compress(code: str) -> dict:
    before_lines = len(code.splitlines())
    base = {"ok": False, "original": code, "compressed": code, "changes": [],
            "before": before_lines, "after": before_lines, "saved_pct": 0}
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {**base, "error": f"Syntax error on line {e.lineno}: {e.msg}"}

    log = Counter()
    comment_blank = sum(1 for l in code.splitlines() if not l.strip() or l.strip().startswith("#"))
    doc_lines = _docstring_lines(tree)

    _strip_docstrings(tree)
    tree = _dead_ifs(tree, log)
    _unreachable(tree, log)
    _unused_imports(tree, log)
    _simplify_bool_returns(tree, log)
    _loops_to_comprehensions(tree, log)
    _dedupe_functions(tree, log)
    _remove_pass(tree, log)
    _fix_empty(tree)
    ast.fix_missing_locations(tree)

    out = ast.unparse(tree)
    out = out + "\n" if out.strip() else ""
    try:
        compile(out, "<shortened>", "exec")
    except SyntaxError as e:  # should never happen; never hand back broken code
        return {**base, "error": f"Internal error, original kept ({e.msg})"}

    after_lines = len(out.splitlines())
    changes = []
    if comment_blank:
        changes.append({"what": "Removed comment and blank lines", "count": comment_blank})
    if doc_lines:
        changes.append({"what": "Removed docstring lines", "count": doc_lines})
    changes += [{"what": k, "count": v} for k, v in log.items()]
    changes.append({"what": "Re-formatted compactly (multi-line expressions joined)", "count": None})
    return {
        "ok": True, "original": code, "compressed": out, "changes": changes,
        "before": before_lines, "after": after_lines,
        "saved_pct": round(100 * (before_lines - after_lines) / before_lines) if before_lines else 0,
        "bytes_before": len(code.encode()), "bytes_after": len(out.encode()),
    }


if __name__ == "__main__":
    import pathlib
    import sys

    if len(sys.argv) != 2:
        sys.exit("usage: python -m app.compress path/to/file.py")
    src = pathlib.Path(sys.argv[1])
    res = compress(src.read_text(encoding="utf-8"))
    if not res["ok"]:
        sys.exit(res["error"])
    dst = src.with_suffix(".short.py")
    dst.write_text(res["compressed"], encoding="utf-8")
    print(f"{res['before']} -> {res['after']} lines ({res['saved_pct']}% shorter), saved to {dst}")
    for c in res["changes"]:
        print(" -", c["what"], "" if c["count"] is None else f"({c['count']})")
