"""Step 1 - preprocessing & normalization.

Two views of a program are produced:
  * normalize_tokens(): flat token list, comments/formatting dropped,
    identifiers -> ID, numbers -> NUM, strings -> STR   (used by token_sim)
  * canonicalize():     comment-free, consistently formatted source with
    identifiers renamed to v0, v1, ...                  (used by semantic_sim)
"""
import ast
import builtins
import io
import keyword
import tokenize
from functools import lru_cache

# Names we never rename / never blank out: keywords + builtins
KEEP = set(keyword.kwlist) | set(dir(builtins))

_SKIP_TOKENS = {
    tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
    tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER,
}
_FSTRING_MIDDLE = getattr(tokenize, "FSTRING_MIDDLE", None)  # Python 3.12+


@lru_cache(maxsize=1024)
def normalize_tokens(code: str) -> tuple:
    out = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(code).readline):
            t, s = tok.type, tok.string
            if t in _SKIP_TOKENS:
                continue
            if t == tokenize.NAME:
                out.append(s if s in KEEP else "ID")
            elif t == tokenize.NUMBER:
                out.append("NUM")
            elif t == tokenize.STRING or t == _FSTRING_MIDDLE:
                out.append("STR")
            else:
                out.append(s)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass  # broken file: keep whatever tokens we managed to read
    return tuple(out)


# ---------------------------------------------------------------- canonical form
class _Renamer(ast.NodeTransformer):
    """Renames variables, arguments, functions and classes consistently."""

    def __init__(self, namer, protected):
        self.namer = namer
        self.protected = protected
        self.map = {}

    def _new(self, old):
        if old in self.protected or (old.startswith("__") and old.endswith("__")):
            return old
        if old not in self.map:
            self.map[old] = self.namer(old, len(self.map))
        return self.map[old]

    def visit_Name(self, node):
        node.id = self._new(node.id)
        return node

    def visit_arg(self, node):
        node.arg = self._new(node.arg)
        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node):
        node.name = self._new(node.name)
        self.generic_visit(node)
        return node

    visit_AsyncFunctionDef = visit_FunctionDef
    visit_ClassDef = visit_FunctionDef


def _imported_names(tree):
    names = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                names.add(a.asname or a.name.split(".")[0])
        elif isinstance(n, ast.ImportFrom):
            for a in n.names:
                names.add(a.asname or a.name)
    return names


def _strip_docstrings(tree):
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            b = n.body
            if (b and isinstance(b[0], ast.Expr)
                    and isinstance(b[0].value, ast.Constant)
                    and isinstance(b[0].value.value, str)):
                n.body = b[1:] or [ast.Pass()]


def canonicalize(code: str, namer=None) -> str:
    """Comment-free, re-formatted code with identifiers renamed.

    namer(old_name, index) -> new_name. Default gives v0, v1, ...
    Falls back to the raw code if it does not parse.
    """
    namer = namer or (lambda old, i: f"v{i}")
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return code
    _strip_docstrings(tree)
    protected = KEEP | {"self", "cls"} | _imported_names(tree)
    tree = _Renamer(namer, protected).visit(tree)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)
