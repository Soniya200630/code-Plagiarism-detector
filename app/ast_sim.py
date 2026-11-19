"""Step 3 - structural similarity using Python's Abstract Syntax Tree.

Only node TYPES are compared (not variable names or literal values), so
renaming / reformatting / changing constants does not fool it.

score = 0.5 * sequence similarity of the node-type sequence
      + 0.5 * Dice overlap of sub-tree hashes
Matching regions = statements (>= MIN_REGION_NODES nodes) whose whole
sub-tree also appears in the other file -> used for highlighting.
"""
import ast
import builtins
from collections import Counter
from difflib import SequenceMatcher
from functools import lru_cache

BUILTINS = set(dir(builtins))
MIN_REGION_NODES = 8   # ignore tiny statements when highlighting
MIN_HASH_NODES = 3     # ignore tiny sub-trees when computing overlap


def _label(node) -> str:
    if isinstance(node, ast.Name) and node.id in BUILTINS:
        return f"Name:{node.id}"
    if isinstance(node, ast.Constant):
        return f"Const:{type(node.value).__name__}"
    return type(node).__name__


def _sequence(node, out):
    out.append(_label(node))
    for c in ast.iter_child_nodes(node):
        _sequence(c, out)


def _hash_tree(node, info):
    kids = [_hash_tree(c, info) for c in ast.iter_child_nodes(node)]
    size = 1 + sum(k[1] for k in kids)
    h = hash((_label(node), tuple(k[0] for k in kids)))
    info[id(node)] = (h, size)
    return h, size


@lru_cache(maxsize=256)
def _prepare(code: str):
    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError, RecursionError):
        return None
    seq, info = [], {}
    _sequence(tree, seq)
    _hash_tree(tree, info)
    counter = Counter(h for h, s in info.values() if s >= MIN_HASH_NODES)
    return tree, seq, info, counter


def _dice(c1: Counter, c2: Counter) -> float:
    total = sum(c1.values()) + sum(c2.values())
    if total == 0:
        return 0.0
    common = sum((c1 & c2).values())
    return 2 * common / total


def _regions(ta, ia, tb, ib):
    index = {}
    for node in ast.walk(tb):
        if isinstance(node, ast.stmt):
            h, s = ib[id(node)]
            if s >= MIN_REGION_NODES:
                index.setdefault(h, node)
    out = []

    def visit(node):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.stmt):
                h, s = ia[id(child)]
                if s >= MIN_REGION_NODES and h in index:
                    m = index[h]
                    out.append({"a": [child.lineno, child.end_lineno],
                                "b": [m.lineno, m.end_lineno]})
                    continue  # don't descend into an already-matched block
            visit(child)

    visit(ta)
    return out


def ast_compare(a: str, b: str) -> dict:
    pa, pb = _prepare(a), _prepare(b)
    if pa is None or pb is None:
        return {"score": None, "regions": [], "error": "could not parse one of the files"}
    ta, sa, ia, ca = pa
    tb, sb, ib, cb = pb
    seq = SequenceMatcher(None, sa, sb, autojunk=False).ratio()
    dice = _dice(ca, cb)
    return {"score": 0.5 * seq + 0.5 * dice, "regions": _regions(ta, ia, tb, ib)}
