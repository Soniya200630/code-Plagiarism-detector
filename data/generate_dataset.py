"""Builds the evaluation dataset.

Run from the project root:   python data/generate_dataset.py

Creates
  data/samples/*.py   base programs (…_a.py / …_b.py = two different solutions
                      of the same problem) + automatically transformed copies
  data/pairs.csv      file_a, file_b, label (1 = plagiarised, 0 = not), kind
"""
import ast
import copy
import csv
import itertools
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.preprocess import canonicalize  # noqa: E402

SAMPLES = ROOT / "data" / "samples"

BASE = {
"fib_a": '''
def fibonacci(n):
    # returns the nth fibonacci number iteratively
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def fib_list(count):
    result = []
    for i in range(count):
        result.append(fibonacci(i))
    return result
''',
"fib_b": '''
def fib(n, memo=None):
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    if n < 2:
        return n
    memo[n] = fib(n - 1, memo) + fib(n - 2, memo)
    return memo[n]
''',
"prime_a": '''
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True


def primes_upto(limit):
    found = []
    for num in range(2, limit + 1):
        if is_prime(num):
            found.append(num)
    return found
''',
"prime_b": '''
def sieve(limit):
    flags = [True] * (limit + 1)
    flags[0:2] = [False, False]
    p = 2
    while p * p <= limit:
        if flags[p]:
            for multiple in range(p * p, limit + 1, p):
                flags[multiple] = False
        p += 1
    return [i for i, ok in enumerate(flags) if ok]
''',
"sort_a": '''
def bubble_sort(items):
    data = list(items)
    n = len(data)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
                swapped = True
        if not swapped:
            break
    return data
''',
"sort_b": '''
def insertion_sort(items):
    data = list(items)
    for i in range(1, len(data)):
        key = data[i]
        j = i - 1
        while j >= 0 and data[j] > key:
            data[j + 1] = data[j]
            j -= 1
        data[j + 1] = key
    return data
''',
"pal_a": '''
def clean(text):
    return "".join(ch.lower() for ch in text if ch.isalnum())


def is_palindrome(text):
    s = clean(text)
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True
''',
"pal_b": '''
def is_palindrome(text):
    filtered = [c.lower() for c in text if c.isalnum()]
    return filtered == filtered[::-1]
''',
"freq_a": '''
def normalize(text):
    return text.lower().replace(",", " ").replace(".", " ").split()


def word_frequency(text):
    counts = {}
    for word in normalize(text):
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1
    return counts
''',
"freq_b": '''
from collections import Counter


def word_frequency(text):
    cleaned = text.lower().replace(",", " ").replace(".", " ")
    return dict(Counter(cleaned.split()))
''',
"gcd_a": '''
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


def lcm(a, b):
    return a * b // gcd(a, b)


def gcd_many(values):
    result = values[0]
    for v in values[1:]:
        result = gcd(result, v)
    return result
''',
"gcd_b": '''
def gcd(a, b):
    if b == 0:
        return a
    return gcd(b, a % b)


def common_divisors(a, b):
    g = gcd(a, b)
    return [d for d in range(1, g + 1) if g % d == 0]
''',
"fact_a": '''
def factorial(n):
    if n < 0:
        raise ValueError("negative")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def choose(n, k):
    return factorial(n) // (factorial(k) * factorial(n - k))
''',
"fact_b": '''
def fact(n):
    if n < 0:
        raise ValueError("negative")
    if n <= 1:
        return 1
    return n * fact(n - 1)


def trailing_zeros(n):
    count = 0
    while n >= 5:
        n //= 5
        count += n
    return count
''',
"rev_a": '''
def reverse_text(text):
    out = ""
    for ch in text:
        out = ch + out
    return out


def reverse_words(sentence):
    words = sentence.split()
    result = []
    for i in range(len(words) - 1, -1, -1):
        result.append(words[i])
    return " ".join(result)
''',
"rev_b": '''
def reverse_text(text):
    chars = list(text)
    left, right = 0, len(chars) - 1
    while left < right:
        chars[left], chars[right] = chars[right], chars[left]
        left += 1
        right -= 1
    return "".join(chars)
''',
"maxv_a": '''
def find_max(items):
    best = items[0]
    for x in items:
        if x > best:
            best = x
    return best


def find_min(items):
    smallest = items[0]
    for x in items:
        if x < smallest:
            smallest = x
    return smallest


def value_range(items):
    return find_max(items) - find_min(items)
''',
"maxv_b": '''
def top_two(items):
    ordered = sorted(items, reverse=True)
    return ordered[0], ordered[1]


def second_largest(items):
    first = second = float("-inf")
    for x in items:
        if x > first:
            first, second = x, first
        elif x > second and x != first:
            second = x
    return second
''',
"vowel_a": '''
def count_vowels(text):
    count = 0
    for ch in text.lower():
        if ch in "aeiou":
            count += 1
    return count


def vowel_ratio(text):
    if len(text) == 0:
        return 0
    return count_vowels(text) / len(text)
''',
"vowel_b": '''
VOWELS = set("aeiou")


def vowel_positions(text):
    return [i for i, ch in enumerate(text.lower()) if ch in VOWELS]


def has_all_vowels(text):
    return VOWELS <= set(text.lower())
''',
}


# ---------------------------------------------------------------- transformations
def t_reformat(code, rng):
    """Comments removed + formatting changed (ast round-trip)."""
    return ast.unparse(ast.parse(code))


def t_rename(code, rng):
    words = ["alpha", "beta", "tmp", "res", "data", "count", "val", "acc", "item", "total"]
    return canonicalize(code, namer=lambda old, i: f"{rng.choice(words)}_{i}")


class _AugToPlain(ast.NodeTransformer):
    def visit_AugAssign(self, node):
        self.generic_visit(node)
        load = copy.deepcopy(node.target)
        for n in ast.walk(load):
            if hasattr(n, "ctx"):
                n.ctx = ast.Load()
        return ast.Assign(targets=[node.target],
                          value=ast.BinOp(left=load, op=node.op, right=node.value))


def t_augassign(code, rng):
    """x += 1  ->  x = x + 1"""
    tree = _AugToPlain().visit(ast.parse(code))
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def t_reorder(code, rng):
    """Reverse the order of top-level functions."""
    tree = ast.parse(code)
    slots = [i for i, n in enumerate(tree.body) if isinstance(n, ast.FunctionDef)]
    if len(slots) < 2:
        return code
    funcs = [tree.body[i] for i in slots][::-1]
    for i, f in zip(slots, funcs):
        tree.body[i] = f
    return ast.unparse(tree)


def t_junk(code, rng):
    """Insert dead assignments and an unused helper function."""
    tree = ast.parse(code)
    k = 0
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            k += 1
            node.body.insert(0, ast.parse(f"unused_{k} = {k * 7}").body[0])
    tree.body.append(ast.parse("def helper_unused():\n    return None").body[0])
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)



class _ForToWhile(ast.NodeTransformer):
    """for i in range(a, b): ...  ->  i = a; while i < b: ...; i += 1"""

    def visit_For(self, node):
        self.generic_visit(node)
        it = node.iter
        ok = (isinstance(node.target, ast.Name) and isinstance(it, ast.Call)
              and isinstance(it.func, ast.Name) and it.func.id == "range"
              and len(it.args) in (1, 2) and not it.keywords and not node.orelse
              and not any(isinstance(n, ast.Continue) for n in ast.walk(node)))
        if not ok:
            return node
        start, stop = (ast.Constant(0), it.args[0]) if len(it.args) == 1 else (it.args[0], it.args[1])
        name = node.target.id
        init = ast.Assign(targets=[ast.Name(id=name, ctx=ast.Store())], value=start)
        step = ast.AugAssign(target=ast.Name(id=name, ctx=ast.Store()), op=ast.Add(), value=ast.Constant(1))
        test = ast.Compare(left=ast.Name(id=name, ctx=ast.Load()), ops=[ast.Lt()], comparators=[stop])
        return [init, ast.While(test=test, body=node.body + [step], orelse=[])]


def t_for_to_while(code, rng):
    tree = _ForToWhile().visit(ast.parse(code))
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


class _SwapIf(ast.NodeTransformer):
    """if c: A else: B  ->  if not c: B else: A"""

    def visit_If(self, node):
        self.generic_visit(node)
        if node.orelse and not (len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If)):
            node.test = ast.UnaryOp(op=ast.Not(), operand=node.test)
            node.body, node.orelse = node.orelse, node.body
        return node


def t_swap_if(code, rng):
    tree = _SwapIf().visit(ast.parse(code))
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def t_combined(code, rng):
    out = t_swap_if(code, rng)
    out = t_for_to_while(out, rng)
    out = t_augassign(out, rng)
    out = t_reorder(out, rng)
    out = t_junk(out, rng)
    return t_rename(out, rng)


TRANSFORMS = {"reformat": t_reformat, "rename": t_rename, "augassign": t_augassign,
              "reorder": t_reorder, "junk": t_junk, "for_to_while": t_for_to_while,
              "swap_if": t_swap_if, "combined": t_combined}


def main():
    rng = random.Random(42)
    SAMPLES.mkdir(parents=True, exist_ok=True)
    for old in SAMPLES.glob("*.py"):
        old.unlink()

    pairs = []
    for name, src in BASE.items():
        src = src.lstrip("\n")
        (SAMPLES / f"{name}.py").write_text(src)

    # positives: original vs transformed copy of itself
    for name, src in BASE.items():
        src = src.lstrip("\n")
        for kind, fn in TRANSFORMS.items():
            new = fn(src, rng)
            if kind != "combined" and ast.unparse(ast.parse(new)) == ast.unparse(ast.parse(src)) \
                    and kind not in ("reformat", "rename"):
                continue  # transformation did not apply to this program
            fname = f"{name}__{kind}.py"
            (SAMPLES / fname).write_text(new + "\n")
            pairs.append((f"{name}.py", fname, 1, kind))

    # negatives: same problem / different algorithm, and different problems
    names = list(BASE)
    for a, b in itertools.combinations(names, 2):
        same_problem = a.split("_")[0] == b.split("_")[0]
        pairs.append((f"{a}.py", f"{b}.py", 0,
                      "same-problem-different-solution" if same_problem else "different-problem"))

    with open(ROOT / "data" / "pairs.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file_a", "file_b", "label", "kind"])
        w.writerows(pairs)
    pos = sum(p[2] for p in pairs)
    print(f"{len(list(SAMPLES.glob('*.py')))} files, {len(pairs)} pairs "
          f"({pos} plagiarised, {len(pairs) - pos} not)")


if __name__ == "__main__":
    main()
