# Solar v1.0.2.
from __future__ import annotations

import argparse
import ast
import tkinter as tk  # still used for StringVar/IntVar and event types
from dataclasses import dataclass
from typing import Any, Callable

# --- customtkinter import with helpful error ---
try:
    import customtkinter as ctk
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "customtkinter is not installed.\n"
        "Install it with:\n"
        "  pip3 install --user customtkinter\n"
        "or inside a venv.\n"
    ) from e


# ---------------- AST nodes ----------------
@dataclass
class Stmt:
    pass


@dataclass
class Let(Stmt):
    name: str
    expr: "Expr"


@dataclass
class Print(Stmt):
    expr: "Expr"


@dataclass
class Call(Stmt):
    func_name: str
    args: list["Expr"]


@dataclass
class PyRaw(Stmt):
    raw: str  # raw python line (kept in-order, inserted verbatim into __run)


@dataclass
class ContainImport(Stmt):
    module: str  # "contain pygame" -> "import pygame" at module top


@dataclass
class IfThen(Stmt):
    cond: "Expr"
    then_stmt: Stmt


# ----- UI AST nodes -----
@dataclass
class UiWindow(Stmt):
    name: str


@dataclass
class UiTitle(Stmt):
    win: str
    title: "Expr"


@dataclass
class UiSize(Stmt):
    win: str
    w: "Expr"
    h: "Expr"


@dataclass
class UiBg(Stmt):
    win: str
    color: "Expr"


@dataclass
class UiFg(Stmt):
    win: str
    color: "Expr"


@dataclass
class UiLabel(Stmt):
    win: str
    name: str
    text: "Expr"
    x: "Expr"
    y: "Expr"


@dataclass
class UiButton(Stmt):
    win: str
    name: str
    text: "Expr"
    x: "Expr"
    y: "Expr"
    on_call: Call


@dataclass
class UiEntry(Stmt):
    win: str
    name: str
    x: "Expr"
    y: "Expr"


@dataclass
class UiSlider(Stmt):
    win: str
    name: str
    minv: "Expr"
    maxv: "Expr"
    x: "Expr"
    y: "Expr"


@dataclass
class UiCheckbox(Stmt):
    win: str
    name: str
    text: "Expr"
    x: "Expr"
    y: "Expr"


@dataclass
class UiBind(Stmt):
    win: str
    key: str
    call: Call


@dataclass
class UiRun(Stmt):
    win: str


@dataclass
class UiText(Stmt):
    widget: str
    text: "Expr"


@dataclass
class UiSet(Stmt):
    varname: str
    value: "Expr"


@dataclass
class UiGetInto(Stmt):
    varname: str
    target: str


# --- pygame AST nodes ---
@dataclass
class PgInit(Stmt):
    pass


@dataclass
class PgWindow(Stmt):
    name: str
    w: "Expr"
    h: "Expr"
    title: "Expr"


@dataclass
class PgFps(Stmt):
    name: str
    fps: "Expr"


@dataclass
class PgLoop(Stmt):
    name: str


@dataclass
class PgEnd(Stmt):
    pass


@dataclass
class PgPoll(Stmt):
    name: str


@dataclass
class PgQuitIf(Stmt):
    name: str


@dataclass
class PgClear(Stmt):
    name: str
    r: "Expr"
    g: "Expr"
    b: "Expr"


@dataclass
class PgRect(Stmt):
    name: str
    x: "Expr"
    y: "Expr"
    w: "Expr"
    h: "Expr"
    r: "Expr"
    g: "Expr"
    b: "Expr"


@dataclass
class PgCircle(Stmt):
    name: str
    x: "Expr"
    y: "Expr"
    rad: "Expr"
    r: "Expr"
    g: "Expr"
    b: "Expr"


@dataclass
class PgText(Stmt):
    name: str
    text: "Expr"
    x: "Expr"
    y: "Expr"
    size: "Expr"
    r: "Expr"
    g: "Expr"
    b: "Expr"


@dataclass
class PgFlip(Stmt):
    name: str


@dataclass
class PgTick(Stmt):
    name: str
    fps: "Expr"


@dataclass
class PgKeyInto(Stmt):
    name: str
    key: str
    target: str


@dataclass
class PgStop(Stmt):
    name: str


# ---------------- Expressions ----------------
@dataclass
class Expr:
    pass


@dataclass
class Num(Expr):
    value: float


@dataclass
class String(Expr):
    value: str


@dataclass
class Var(Expr):
    name: str


@dataclass
class RawExpr(Expr):
    src: str  # expression source to evaluate safely at runtime


# ---------------- Tokenizer (keeps whether token was quoted; supports parentheses groups) ----------------
def tokenize_line(line: str) -> list[tuple[str, bool]]:
    """
    Returns [(token, was_quoted), ...]
    Supports:
      - "..." and '...' strings with backslash escapes
      - Parentheses groups as ONE token, including spaces: (a + b*3)
    """
    tokens: list[tuple[str, bool]] = []
    i = 0
    n = len(line)

    def read_string(q: str) -> str:
        nonlocal i
        i += 1
        out: list[str] = []
        while i < n:
            if line[i] == "\\" and i + 1 < n:
                out.append(line[i + 1])
                i += 2
                continue
            if line[i] == q:
                break
            out.append(line[i])
            i += 1
        if i >= n or line[i] != q:
            raise SyntaxError("Oh noes! Solar threw an error: unclosed string literal")
        i += 1
        return "".join(out)

    def read_paren_group() -> str:
        nonlocal i
        depth = 0
        out: list[str] = []
        while i < n:
            ch = line[i]
            if ch in ('"', "'"):
                s = read_string(ch)
                out.append(ch + s + ch)
                continue
            if ch == "(":
                depth += 1
                out.append(ch)
                i += 1
                continue
            if ch == ")":
                depth -= 1
                out.append(ch)
                i += 1
                if depth == 0:
                    break
                continue
            out.append(ch)
            i += 1
        if depth != 0:
            raise SyntaxError("Oh noes! Solar threw an error: unclosed parentheses group")
        return "".join(out)

    while i < n:
        while i < n and line[i].isspace():
            i += 1
        if i >= n:
            break

        ch = line[i]
        if ch in ('"', "'"):
            s = read_string(ch)
            tokens.append((s, True))
            continue

        if ch == "(":
            grp = read_paren_group()
            tokens.append((grp, False))
            continue

        start = i
        while i < n and not line[i].isspace():
            if line[i] == "(":
                break
            i += 1
        if start != i:
            tokens.append((line[start:i], False))
            continue

        # if we hit '(' without consuming, it'll be handled next loop
        if i < n and line[i] == "(":
            continue

    return tokens


# ---------------- Python passthrough detection ----------------
def starts_python_block(raw_line: str) -> bool:
    s = raw_line.lstrip()
    if not s:
        return False

    # Only start passthrough blocks for *real* Python blocks.
    # Solar has `if ... then ...` (no trailing ':'), so we must NOT treat plain "if " as python.
    if s.startswith(("def ", "class ", "@")):
        return True

    # Any Python block header ends with ':'
    return s.rstrip().endswith(":")


def looks_like_python_single_line(raw_line: str) -> bool:
    """
    Single-line python that should NOT be parsed as Solar.
    """
    s = raw_line.lstrip()
    if not s:
        return False

    # Never classify Solar keywords / DSL lines as python, even if they contain '='
    if s.startswith(("contain ", "let ", "print ", "call ", "ui ", "pg ", "if ")):
        return False

    if s.startswith(("import ", "from ")):
        return True

    # treat assignments as python unless Solar's `let ... = ...`
    if "=" in s and not s.strip().startswith("let "):
        return True

    # common in your use-case
    if s.startswith("funcs[") or s.startswith("vars_[") or s.startswith("vars_[" ):
        return True

    return False


# ---------------- Parsing ----------------
def parse_prog(src: str) -> list[Stmt]:
    program: list[Stmt] = []
    in_py_block = False

    for lineno, raw_line in enumerate(src.splitlines(), start=1):
        line = raw_line.rstrip("\n")

        if not line.strip():
            if in_py_block:
                program.append(PyRaw(line))
            continue

        if line.lstrip().startswith("#"):
            if in_py_block:
                program.append(PyRaw(line))
            continue

        if in_py_block:
            if line.startswith((" ", "\t")):
                program.append(PyRaw(line))
                continue
            in_py_block = False

        if line.strip().startswith("contain "):
            rest = line.strip().split(None, 1)[1].strip()
            if "#" in rest:
                rest = rest.split("#", 1)[0].strip()
            rest = rest.rstrip(" ;,")
            mod = rest
            if not mod or not all(part.isidentifier() for part in mod.split(".")):
                raise SyntaxError(
                    f"Oh noes! Solar threw an error: Line {lineno}: `contain <module>` expects a valid module name"
                )
            program.append(ContainImport(mod))
            continue

        if starts_python_block(line):
            program.append(PyRaw(line))
            in_py_block = True
            continue

        if looks_like_python_single_line(line):
            program.append(PyRaw(line))
            continue

        try:
            program.append(parse_solar_line(line, lineno))
        except SyntaxError:
            program.append(PyRaw(line))

    return [s for s in program if s is not None]


def parse_solar_line(raw_line: str, lineno: int) -> Stmt:
    line = raw_line.strip()
    parts_q = tokenize_line(line)
    if not parts_q:
        raise SyntaxError("empty")

    parts = [t for (t, _q) in parts_q]
    quoted = [q for (_t, q) in parts_q]
    head = parts[0]

    # if <expr> then <stmt...>
    if head == "if" and "then" in parts:
        then_i = parts.index("then")
        if then_i < 2 or then_i == len(parts) - 1:
            raise SyntaxError(f"Oh noes! Solar threw an error: Line {lineno}: bad if-then")
        cond_src = " ".join(parts[1:then_i])
        cond = parse_expr(cond_src, lineno, False)
        then_line = " ".join(parts[then_i + 1 :])
        then_stmt = parse_solar_line(then_line, lineno)
        return IfThen(cond, then_stmt)

    if head == "let":
        if len(parts) < 4 or parts[2] != "=":
            raise SyntaxError(
                f"Oh noes! Solar threw an error: Line {lineno}: expected `let <name> = <expr>`"
            )
        name = parts[1]
        expr_src = " ".join(parts[3:])
        was_quoted = (len(parts[3:]) == 1 and quoted[3])
        return Let(name, parse_expr(expr_src, lineno, was_quoted))

    if head == "print":
        if len(parts) < 2:
            raise SyntaxError(
                f"Oh noes! Solar threw an error: Line {lineno}: expected `print <expr>`"
            )
        if len(parts) == 2:
            return Print(parse_expr(parts[1], lineno, quoted[1]))
        args = [parse_expr(parts[i], lineno, quoted[i]) for i in range(1, len(parts))]
        return Call("print_many", args)

    if head == "call":
        if len(parts) < 2:
            raise SyntaxError(
                f"Oh noes! Solar threw an error: Line {lineno}: expected `call <func> [args...]`"
            )
        func_name = parts[1]
        args = [parse_expr(parts[i], lineno, quoted[i]) for i in range(2, len(parts))]
        return Call(func_name, args)

    # UI
    if head == "ui":
        if len(parts) < 3:
            raise SyntaxError(f"Oh noes! Solar threw an error: Line {lineno}: bad ui statement")
        cmd = parts[1]

        if cmd == "window":
            return UiWindow(parts[2])

        if cmd == "title":
            return UiTitle(parts[2], parse_expr(parts[3], lineno, quoted[3]))

        if cmd == "size":
            return UiSize(
                parts[2],
                parse_expr(parts[3], lineno, quoted[3]),
                parse_expr(parts[4], lineno, quoted[4]),
            )

        if cmd == "bg":
            return UiBg(parts[2], parse_expr(parts[3], lineno, quoted[3]))

        if cmd == "fg":
            return UiFg(parts[2], parse_expr(parts[3], lineno, quoted[3]))

        if cmd == "label":
            if "at" not in parts:
                raise SyntaxError(
                    f"Oh noes! Solar threw an error: Line {lineno}: label needs `at x y`"
                )
            at_i = parts.index("at")
            win = parts[2]
            name = parts[3]
            text = parse_expr(parts[4], lineno, quoted[4])
            x = parse_expr(parts[at_i + 1], lineno, quoted[at_i + 1])
            y = parse_expr(parts[at_i + 2], lineno, quoted[at_i + 2])
            return UiLabel(win, name, text, x, y)

        if cmd == "button":
            if "at" not in parts or "do" not in parts:
                raise SyntaxError(
                    f"Oh noes! Solar threw an error: Line {lineno}: button needs `at x y do ...`"
                )
            at_i = parts.index("at")
            do_i = parts.index("do")
            win = parts[2]
            name = parts[3]
            text = parse_expr(parts[4], lineno, quoted[4])
            x = parse_expr(parts[at_i + 1], lineno, quoted[at_i + 1])
            y = parse_expr(parts[at_i + 2], lineno, quoted[at_i + 2])
            func_name = parts[do_i + 1]
            args = [parse_expr(parts[i], lineno, quoted[i]) for i in range(do_i + 2, len(parts))]
            return UiButton(win, name, text, x, y, Call(func_name, args))

        if cmd == "entry":
            if "at" not in parts:
                raise SyntaxError(
                    f"Oh noes! Solar threw an error: Line {lineno}: entry needs `at x y`"
                )
            at_i = parts.index("at")
            return UiEntry(
                parts[2],
                parts[3],
                parse_expr(parts[at_i + 1], lineno, quoted[at_i + 1]),
                parse_expr(parts[at_i + 2], lineno, quoted[at_i + 2]),
            )

        if cmd == "slider":
            if "from" not in parts or "to" not in parts or "at" not in parts:
                raise SyntaxError(
                    f"Oh noes! Solar threw an error: Line {lineno}: slider needs `from a to b at x y`"
                )
            from_i = parts.index("from")
            to_i = parts.index("to")
            at_i = parts.index("at")
            return UiSlider(
                parts[2],
                parts[3],
                parse_expr(parts[from_i + 1], lineno, quoted[from_i + 1]),
                parse_expr(parts[to_i + 1], lineno, quoted[to_i + 1]),
                parse_expr(parts[at_i + 1], lineno, quoted[at_i + 1]),
                parse_expr(parts[at_i + 2], lineno, quoted[at_i + 2]),
            )

        if cmd == "checkbox":
            if "at" not in parts:
                raise SyntaxError(
                    f"Oh noes! Solar threw an error: Line {lineno}: checkbox needs `at x y`"
                )
            at_i = parts.index("at")
            win = parts[2]
            name = parts[3]
            text = parse_expr(parts[4], lineno, quoted[4])
            x = parse_expr(parts[at_i + 1], lineno, quoted[at_i + 1])
            y = parse_expr(parts[at_i + 2], lineno, quoted[at_i + 2])
            return UiCheckbox(win, name, text, x, y)

        if cmd == "bind":
            if "do" not in parts:
                raise SyntaxError(
                    f"Oh noes! Solar threw an error: Line {lineno}: bind needs `do ...`"
                )
            do_i = parts.index("do")
            key = parts[3]
            func = parts[do_i + 1]
            args = [parse_expr(parts[i], lineno, quoted[i]) for i in range(do_i + 2, len(parts))]
            return UiBind(parts[2], key, Call(func, args))

        if cmd == "text":
            return UiText(parts[2], parse_expr(parts[3], lineno, quoted[3]))

        if cmd == "set":
            return UiSet(parts[2], parse_expr(parts[3], lineno, quoted[3]))

        if cmd == "get":
            if len(parts) < 5 or parts[3] != "into":
                raise SyntaxError(
                    f"Oh noes! Solar threw an error: Line {lineno}: expected `ui get <var> into <name>`"
                )
            return UiGetInto(parts[2], parts[4])

        if cmd == "run":
            return UiRun(parts[2])

        raise SyntaxError(
            f"Oh noes! Solar threw an error: Line {lineno}: unknown ui command: {cmd}"
        )

    # pygame
    if head == "pg":
        if len(parts) < 2:
            raise SyntaxError(f"Oh noes! Solar threw an error: Line {lineno}: bad pg statement")
        cmd = parts[1]

        if cmd == "init":
            return PgInit()

        if cmd == "window":
            if len(parts) < 6:
                raise SyntaxError(
                    f"Oh noes! Solar threw an error: Line {lineno}: pg window <name> <w> <h> <title>"
                )
            return PgWindow(
                parts[2],
                parse_expr(parts[3], lineno, quoted[3]),
                parse_expr(parts[4], lineno, quoted[4]),
                parse_expr(parts[5], lineno, quoted[5]),
            )

        if cmd == "fps":
            if len(parts) < 4:
                raise SyntaxError(
                    f"Oh noes! Solar threw an error: Line {lineno}: pg fps <name> <fps>"
                )
            return PgFps(parts[2], parse_expr(parts[3], lineno, quoted[3]))

        if cmd == "loop":
            if len(parts) < 3:
                raise SyntaxError(
                    f"Oh noes! Solar threw an error: Line {lineno}: pg loop <name>"
                )
            return PgLoop(parts[2])

        if cmd == "end":
            return PgEnd()

        if cmd == "poll":
            if len(parts) < 3:
                raise SyntaxError(
                    f"Oh noes! Solar threw an error: Line {lineno}: pg poll <name>"
                )
            return PgPoll(parts[2])

        if cmd == "quitif":
            if len(parts) < 3:
                raise SyntaxError(
                    f"Oh noes! Solar threw an error: Line {lineno}: pg quitif <name>"
                )
            return PgQuitIf(parts[2])

        if cmd == "stop":
            if len(parts) < 3:
                raise SyntaxError(
                    f"Oh noes! Solar threw an error: Line {lineno}: pg stop <name>"
                )
            return PgStop(parts[2])

        if cmd == "clear":
            if len(parts) < 6:
                raise SyntaxError(
                    f"Oh noes! Solar threw an error: Line {lineno}: pg clear <name> <r> <g> <b>"
                )
            return PgClear(
                parts[2],
                parse_expr(parts[3], lineno, quoted[3]),
                parse_expr(parts[4], lineno, quoted[4]),
                parse_expr(parts[5], lineno, quoted[5]),
            )

        if cmd == "rect":
            if len(parts) < 10:
                raise SyntaxError(
                    f"Oh noes! Solar threw an error: Line {lineno}: pg rect <name> x y w h r g b"
                )
            return PgRect(
                parts[2],
                parse_expr(parts[3], lineno, quoted[3]),
                parse_expr(parts[4], lineno, quoted[4]),
                parse_expr(parts[5], lineno, quoted[5]),
                parse_expr(parts[6], lineno, quoted[6]),
                parse_expr(parts[7], lineno, quoted[7]),
                parse_expr(parts[8], lineno, quoted[8]),
                parse_expr(parts[9], lineno, quoted[9]),
            )

        if cmd == "circle":
            if len(parts) < 9:
                raise SyntaxError(
                    f"Oh noes! Solar threw an error: Line {lineno}: pg circle <name> x y rad r g b"
                )
            return PgCircle(
                parts[2],
                parse_expr(parts[3], lineno, quoted[3]),
                parse_expr(parts[4], lineno, quoted[4]),
                parse_expr(parts[5], lineno, quoted[5]),
                parse_expr(parts[6], lineno, quoted[6]),
                parse_expr(parts[7], lineno, quoted[7]),
                parse_expr(parts[8], lineno, quoted[8]),
            )

        if cmd == "text":
            if len(parts) < 10:
                raise SyntaxError(
                    f"Oh noes! Solar threw an error: Line {lineno}: pg text <name> <text> x y size r g b"
                )
            return PgText(
                parts[2],
                parse_expr(parts[3], lineno, quoted[3]),
                parse_expr(parts[4], lineno, quoted[4]),
                parse_expr(parts[5], lineno, quoted[5]),
                parse_expr(parts[6], lineno, quoted[6]),
                parse_expr(parts[7], lineno, quoted[7]),
                parse_expr(parts[8], lineno, quoted[8]),
                parse_expr(parts[9], lineno, quoted[9]),
            )

        if cmd == "flip":
            if len(parts) < 3:
                raise SyntaxError(
                    f"Oh noes! Solar threw an error: Line {lineno}: pg flip <name>"
                )
            return PgFlip(parts[2])

        if cmd == "tick":
            if len(parts) < 4:
                raise SyntaxError(
                    f"Oh noes! Solar threw an error: Line {lineno}: pg tick <name> <fps>"
                )
            return PgTick(parts[2], parse_expr(parts[3], lineno, quoted[3]))

        if cmd == "key":
            if len(parts) < 6 or parts[4] != "into":
                raise SyntaxError(
                    f"Oh noes! Solar threw an error: Line {lineno}: pg key <name> <K_*> into <var>"
                )
            return PgKeyInto(parts[2], parts[3], parts[5])

        raise SyntaxError(
            f"Oh noes! Solar threw an error: Line {lineno}: unknown pg command: {cmd}"
        )

    func_name = head
    args = [parse_expr(parts[i], lineno, quoted[i]) for i in range(1, len(parts))]
    return Call(func_name, args)


def parse_expr(token: str, lineno: int, was_quoted: bool) -> Expr:
    if was_quoted:
        return String(token)

    # strip outer parentheses group only if it wraps fully
    s = token.strip()
    if s.startswith("(") and s.endswith(")"):
        # keep parentheses for python eval; it's fine
        pass

    try:
        if "." in s:
            return Num(float(s))
        return Num(int(s))
    except ValueError:
        pass

    if s.isidentifier():
        return Var(s)

    return RawExpr(s)


# ---------------- Compilation (AST -> Python source) ----------------
def actual_interpreter_func(program: list[Stmt]) -> str:
    module_prelude: list[str] = []
    run_lines: list[str] = []

    seen_imports: set[str] = set()

    module_prelude.append("# --- compiled by Solar v1.0.2-beta ---")

    run_lines.append("def __run(vars_, funcs):")
    run_lines.append("    __wins = {}")
    run_lines.append("    __widgets = {}")
    run_lines.append("    __uivars = {}")
    run_lines.append("    __uistyle = {}")
    run_lines.append("    __pg = {}")
    run_lines.append("")

    # ---- Safe expression evaluator ----
    run_lines.append("    import math, random")
    run_lines.append("")
    run_lines.append("    def __truthy(v):")
    run_lines.append("        try:")
    run_lines.append("            return bool(v)")
    run_lines.append("        except Exception:")
    run_lines.append("            return False")
    run_lines.append("")
    run_lines.append("    def __eval_expr(expr_src: str):")
    run_lines.append("        tree = ast.parse(expr_src, mode='eval')")
    run_lines.append("        allowed = (")
    run_lines.append("            ast.Expression, ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare,")
    run_lines.append("            ast.Name, ast.Load, ast.Constant, ast.Call, ast.Attribute,")
    run_lines.append("            ast.Subscript, ast.Slice, ast.Index,")
    run_lines.append("            ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,")
    run_lines.append("            ast.UAdd, ast.USub, ast.And, ast.Or,")
    run_lines.append("            ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,")
    run_lines.append("            ast.Not, ast.Invert,")
    run_lines.append("            ast.BitAnd, ast.BitOr, ast.BitXor, ast.LShift, ast.RShift,")
    run_lines.append("            ast.IfExp, ast.List, ast.Tuple, ast.Dict")
    run_lines.append("        )")
    run_lines.append("        for node in ast.walk(tree):")
    run_lines.append("            if not isinstance(node, allowed):")
    run_lines.append("                raise ValueError('Solar expr blocked: ' + node.__class__.__name__)")
    run_lines.append("            if isinstance(node, ast.Attribute) and node.attr.startswith('__'):")
    run_lines.append("                raise ValueError('Solar expr blocked: dunder attribute')")
    run_lines.append("            if isinstance(node, ast.Name) and node.id in ('__import__','eval','exec','open','compile','globals','locals'):")
    run_lines.append("                raise ValueError('Solar expr blocked: dangerous name')")
    run_lines.append("")
    run_lines.append("        def clamp(v, lo, hi):")
    run_lines.append("            return lo if v < lo else (hi if v > hi else v)")
    run_lines.append("")
    run_lines.append("        env = {}")
    run_lines.append("        env.update(vars_)")
    run_lines.append("        env.update({")
    run_lines.append("            'math': math, 'random': random,")
    run_lines.append("            'min': min, 'max': max, 'abs': abs, 'round': round,")
    run_lines.append("            'int': int, 'float': float, 'str': str, 'len': len,")
    run_lines.append("            'clamp': clamp,")
    run_lines.append("            'randint': random.randint,")
    run_lines.append("        })")
    run_lines.append("        return eval(compile(tree, '<solar_expr>', 'eval'), {'__builtins__': {}}, env)")
    run_lines.append("")

    # ---- UI helpers ----
    run_lines.append("    def __style_defaults(win_name):")
    run_lines.append("        return __uistyle.get(win_name, {'bg': None, 'fg': None})")
    run_lines.append("")
    run_lines.append("    def __safe_config(widget, **kwargs):")
    run_lines.append("        for k, v in list(kwargs.items()):")
    run_lines.append("            if v is None:")
    run_lines.append("                kwargs.pop(k, None)")
    run_lines.append("        if not kwargs:")
    run_lines.append("            return")
    run_lines.append("        try:")
    run_lines.append("            widget.configure(**kwargs)")
    run_lines.append("        except Exception:")
    run_lines.append("            pass")
    run_lines.append("")
    run_lines.append("    def __apply_style(win_name, widget, kind: str):")
    run_lines.append("        st = __style_defaults(win_name)")
    run_lines.append("        bg = st.get('bg')")
    run_lines.append("        fg = st.get('fg')")
    run_lines.append("        if kind == 'root':")
    run_lines.append("            __safe_config(widget, fg_color=bg)")
    run_lines.append("            return")
    run_lines.append("        try:")
    run_lines.append("            cls = widget.__class__.__name__")
    run_lines.append("        except Exception:")
    run_lines.append("            cls = ''")
    run_lines.append("        if cls == 'CTkButton':")
    run_lines.append("            return")
    run_lines.append("        __safe_config(widget, text_color=fg)")
    run_lines.append("")

    indent = 1
    pg_loop_stack: list[str] = []

    def emit(s: str) -> None:
        run_lines.append(("    " * indent) + s)

    def compile_one(stmt: Stmt) -> None:
        nonlocal indent
        if isinstance(stmt, Let):
            emit(f"vars_[{stmt.name!r}] = {expr_to_py(stmt.expr)}")
            return
        if isinstance(stmt, Print):
            emit(f"print({expr_to_py(stmt.expr)})")
            return
        if isinstance(stmt, Call):
            args = ", ".join(expr_to_py(a) for a in stmt.args)
            emit(f"_fn = funcs.get({stmt.func_name!r})")
            emit(f"if _fn is None: raise NameError('Oh noes! Solar threw an error: Unknown function: {stmt.func_name}')")
            emit(f"_fn({args})")
            return
        if isinstance(stmt, PgStop):
            emit(f"__pg.get({stmt.name!r}, {{}})['running'] = False")
            return
        # fallback
        emit("pass")

    for st in program:
        if isinstance(st, ContainImport):
            if st.module not in seen_imports:
                module_prelude.append(f"import {st.module}")
                seen_imports.add(st.module)
            continue

        if isinstance(st, PyRaw):
            run_lines.append(("    " * indent) + st.raw)
            continue

        if isinstance(st, IfThen):
            emit(f"if __truthy({expr_to_py(st.cond)}):")
            indent += 1
            compile_one(st.then_stmt)
            indent -= 1
            continue

        # --- UI ---
        if isinstance(st, Let):
            emit(f"vars_[{st.name!r}] = {expr_to_py(st.expr)}")
            continue

        if isinstance(st, Print):
            emit(f"print({expr_to_py(st.expr)})")
            continue

        if isinstance(st, Call):
            args = ", ".join(expr_to_py(a) for a in st.args)
            emit(f"_fn = funcs.get({st.func_name!r})")
            emit(f"if _fn is None: raise NameError('Oh noes! Solar threw an error: Unknown function: {st.func_name}')")
            emit(f"_fn({args})")
            continue

        if isinstance(st, UiWindow):
            emit(f"__wins[{st.name!r}] = ctk.CTk()")
            emit(f"__uistyle[{st.name!r}] = {{'bg': None, 'fg': None}}")
            emit(f"__apply_style({st.name!r}, __wins[{st.name!r}], 'root')")
            continue

        if isinstance(st, UiTitle):
            emit(f"__wins[{st.win!r}].title({expr_to_py(st.title)})")
            continue

        if isinstance(st, UiSize):
            emit(f"__wins[{st.win!r}].geometry(str({expr_to_py(st.w)}) + 'x' + str({expr_to_py(st.h)}))")
            continue

        if isinstance(st, UiBg):
            emit(f"__uistyle.setdefault({st.win!r}, {{'bg': None, 'fg': None}})['bg'] = {expr_to_py(st.color)}")
            emit(f"__apply_style({st.win!r}, __wins[{st.win!r}], 'root')")
            emit("for __n, __w in list(__widgets.items()):")
            indent += 1
            emit("try:")
            indent += 1
            emit(f"if getattr(__w, 'master', None) is __wins[{st.win!r}]:")
            indent += 1
            emit(f"__apply_style({st.win!r}, __w, 'widget')")
            indent -= 1
            indent -= 1
            emit("except Exception:")
            indent += 1
            emit("pass")
            indent -= 1
            indent -= 1
            continue

        if isinstance(st, UiFg):
            emit(f"__uistyle.setdefault({st.win!r}, {{'bg': None, 'fg': None}})['fg'] = {expr_to_py(st.color)}")
            emit("for __n, __w in list(__widgets.items()):")
            indent += 1
            emit("try:")
            indent += 1
            emit(f"if getattr(__w, 'master', None) is __wins[{st.win!r}]:")
            indent += 1
            emit(f"__apply_style({st.win!r}, __w, 'widget')")
            indent -= 1
            indent -= 1
            emit("except Exception:")
            indent += 1
            emit("pass")
            indent -= 1
            indent -= 1
            continue

        if isinstance(st, UiLabel):
            emit(f"__widgets[{st.name!r}] = ctk.CTkLabel(__wins[{st.win!r}], text={expr_to_py(st.text)})")
            emit(f"__apply_style({st.win!r}, __widgets[{st.name!r}], 'widget')")
            emit(f"__widgets[{st.name!r}].place(x={expr_to_py(st.x)}, y={expr_to_py(st.y)})")
            continue

        if isinstance(st, UiButton):
            fn = st.on_call.func_name
            args = ", ".join(expr_to_py(a) for a in st.on_call.args)
            cb_name = f"__cb_{st.name}"
            emit(f"def {cb_name}():")
            indent += 1
            emit(f"_fn = funcs.get({fn!r})")
            emit(f"if _fn is None: raise NameError('Oh noes! Solar threw an error: Unknown function: {fn}')")
            emit(f"_fn({args})")
            indent -= 1

            emit(f"__st = __style_defaults({st.win!r})")
            emit("__btn_tc = __st.get('fg')")
            emit(
                f"__widgets[{st.name!r}] = ctk.CTkButton(__wins[{st.win!r}], text={expr_to_py(st.text)}, command={cb_name}, text_color=__btn_tc if __btn_tc is not None else None)"
            )
            emit(f"__widgets[{st.name!r}].place(x={expr_to_py(st.x)}, y={expr_to_py(st.y)})")
            continue

        if isinstance(st, UiEntry):
            emit(f"__uivars[{st.name!r}] = tk.StringVar()")
            emit(f"__widgets[{st.name!r}] = ctk.CTkEntry(__wins[{st.win!r}], textvariable=__uivars[{st.name!r}])")
            emit(f"__apply_style({st.win!r}, __widgets[{st.name!r}], 'widget')")
            emit(f"__widgets[{st.name!r}].place(x={expr_to_py(st.x)}, y={expr_to_py(st.y)})")
            emit(f"vars_[{st.name!r}] = __uivars[{st.name!r}]")
            continue

        if isinstance(st, UiSlider):
            emit(f"__uivars[{st.name!r}] = tk.IntVar()")
            emit(f"__widgets[{st.name!r}] = ctk.CTkSlider(__wins[{st.win!r}], from_={expr_to_py(st.minv)}, to={expr_to_py(st.maxv)}, variable=__uivars[{st.name!r}])")
            emit(f"__apply_style({st.win!r}, __widgets[{st.name!r}], 'widget')")
            emit(f"__widgets[{st.name!r}].place(x={expr_to_py(st.x)}, y={expr_to_py(st.y)})")
            emit(f"vars_[{st.name!r}] = __uivars[{st.name!r}]")
            continue

        if isinstance(st, UiCheckbox):
            emit(f"__uivars[{st.name!r}] = tk.IntVar()")
            emit(f"__widgets[{st.name!r}] = ctk.CTkCheckBox(__wins[{st.win!r}], text={expr_to_py(st.text)}, variable=__uivars[{st.name!r}])")
            emit(f"__apply_style({st.win!r}, __widgets[{st.name!r}], 'widget')")
            emit(f"__widgets[{st.name!r}].place(x={expr_to_py(st.x)}, y={expr_to_py(st.y)})")
            emit(f"vars_[{st.name!r}] = __uivars[{st.name!r}]")
            continue

        if isinstance(st, UiBind):
            fn = st.call.func_name
            args = ", ".join(expr_to_py(a) for a in st.call.args)
            bind_name = f"__bind_{fn}"
            emit(f"def {bind_name}(event=None):")
            indent += 1
            emit(f"_fn = funcs.get({fn!r})")
            emit(f"if _fn is None: raise NameError('Oh noes! Solar threw an error: Unknown function: {fn}')")
            emit(f"_fn({args})")
            indent -= 1
            emit(f"__wins[{st.win!r}].bind('<{st.key}>', {bind_name})")
            continue

        if isinstance(st, UiText):
            emit(f"__w = __widgets.get({st.widget!r})")
            emit(f"if __w is None: raise NameError('Oh noes! Solar threw an error: Unknown widget: {st.widget}')")
            emit("try:")
            indent += 1
            emit(f"__w.configure(text={expr_to_py(st.text)})")
            indent -= 1
            emit("except Exception:")
            indent += 1
            emit("pass")
            indent -= 1
            continue

        if isinstance(st, UiSet):
            emit(f"__v = vars_.get({st.varname!r})")
            emit(f"if __v is None: raise NameError('Oh noes! Solar threw an error: Unknown ui var: {st.varname}')")
            emit("try:")
            indent += 1
            emit(f"__v.set({expr_to_py(st.value)})")
            indent -= 1
            emit("except Exception:")
            indent += 1
            emit(f"vars_[{st.varname!r}] = {expr_to_py(st.value)}")
            indent -= 1
            continue

        if isinstance(st, UiGetInto):
            emit(f"__v = vars_.get({st.varname!r})")
            emit(f"if __v is None: raise NameError('Oh noes! Solar threw an error: Unknown ui var: {st.varname}')")
            emit("try:")
            indent += 1
            emit(f"vars_[{st.target!r}] = __v.get()")
            indent -= 1
            emit("except Exception:")
            indent += 1
            emit(f"vars_[{st.target!r}] = __v")
            indent -= 1
            continue

        if isinstance(st, UiRun):
            emit(f"__wins[{st.win!r}].mainloop()")
            continue

        # --- PYGAME ---
        if isinstance(st, PgInit):
            emit("import pygame")
            emit("pygame.init()")
            continue

        if isinstance(st, PgWindow):
            emit("import pygame")
            emit(f"__pg[{st.name!r}] = {{'running': True, 'fps': 60, 'events': [], 'keys': None, 'font_cache': {{}}}}")
            emit(f"__pg[{st.name!r}]['w'] = int({expr_to_py(st.w)})")
            emit(f"__pg[{st.name!r}]['h'] = int({expr_to_py(st.h)})")
            emit(f"__pg[{st.name!r}]['screen'] = pygame.display.set_mode((__pg[{st.name!r}]['w'], __pg[{st.name!r}]['h']))")
            emit(f"pygame.display.set_caption(str({expr_to_py(st.title)}))")
            emit(f"__pg[{st.name!r}]['clock'] = pygame.time.Clock()")
            continue

        if isinstance(st, PgFps):
            emit(f"__pg.get({st.name!r}, {{}})['fps'] = int({expr_to_py(st.fps)})")
            continue

        if isinstance(st, PgLoop):
            emit(f"while __pg.get({st.name!r}, {{}}).get('running', False):")
            pg_loop_stack.append(st.name)
            indent += 1
            continue

        if isinstance(st, PgEnd):
            if pg_loop_stack:
                pg_loop_stack.pop()
                indent = max(1, indent - 1)
            continue

        if isinstance(st, PgPoll):
            emit("import pygame")
            emit(f"__pg[{st.name!r}]['events'] = pygame.event.get()")
            emit(f"__pg[{st.name!r}]['keys'] = pygame.key.get_pressed()")
            continue

        if isinstance(st, PgQuitIf):
            emit("import pygame")
            emit(f"for __ev in __pg[{st.name!r}].get('events', []):")
            indent += 1
            emit("if __ev.type == pygame.QUIT:")
            indent += 1
            emit(f"__pg[{st.name!r}]['running'] = False")
            indent -= 1
            indent -= 1
            continue

        if isinstance(st, PgStop):
            emit(f"__pg.get({st.name!r}, {{}})['running'] = False")
            continue

        if isinstance(st, PgClear):
            emit("import pygame")
            emit(f"__pg[{st.name!r}]['screen'].fill((int({expr_to_py(st.r)}), int({expr_to_py(st.g)}), int({expr_to_py(st.b)})))")
            continue

        if isinstance(st, PgRect):
            emit("import pygame")
            emit(
                f"pygame.draw.rect(__pg[{st.name!r}]['screen'], "
                f"(int({expr_to_py(st.r)}), int({expr_to_py(st.g)}), int({expr_to_py(st.b)})), "
                f"pygame.Rect(int({expr_to_py(st.x)}), int({expr_to_py(st.y)}), int({expr_to_py(st.w)}), int({expr_to_py(st.h)})))"
            )
            continue

        if isinstance(st, PgCircle):
            emit("import pygame")
            emit(
                f"pygame.draw.circle(__pg[{st.name!r}]['screen'], "
                f"(int({expr_to_py(st.r)}), int({expr_to_py(st.g)}), int({expr_to_py(st.b)})), "
                f"(int({expr_to_py(st.x)}), int({expr_to_py(st.y)})), int({expr_to_py(st.rad)}))"
            )
            continue

        if isinstance(st, PgText):
            emit("import pygame")
            emit(f"__fc = __pg[{st.name!r}].setdefault('font_cache', {{}})")
            emit(f"__sz = int({expr_to_py(st.size)})")
            emit("__font = __fc.get(__sz)")
            emit("if __font is None:")
            indent += 1
            emit("pygame.font.init()")
            emit("__font = pygame.font.SysFont(None, __sz)")
            emit("__fc[__sz] = __font")
            indent -= 1
            emit(
                f"__surf = __font.render(str({expr_to_py(st.text)}), True, "
                f"(int({expr_to_py(st.r)}), int({expr_to_py(st.g)}), int({expr_to_py(st.b)})))"
            )
            emit(f"__pg[{st.name!r}]['screen'].blit(__surf, (int({expr_to_py(st.x)}), int({expr_to_py(st.y)})))")
            continue

        if isinstance(st, PgFlip):
            emit("import pygame")
            emit("pygame.display.flip()")
            continue

        if isinstance(st, PgTick):
            emit("import pygame")
            emit(f"__pg[{st.name!r}]['clock'].tick(int({expr_to_py(st.fps)}))")
            continue

        if isinstance(st, PgKeyInto):
            emit("import pygame")
            emit(f"__keys = __pg[{st.name!r}].get('keys')")
            emit(f"__k = getattr(pygame, {st.key!r}, None)")
            emit("if __keys is None or __k is None:")
            indent += 1
            emit(f"vars_[{st.target!r}] = 0")
            indent -= 1
            emit("else:")
            indent += 1
            emit(f"vars_[{st.target!r}] = 1 if __keys[__k] else 0")
            indent -= 1
            continue

        raise TypeError(f"Oh noes! Solar threw an error: Unknown statement: {st}")

    run_lines.append("")
    run_lines.append("    # end")

    return "\n".join(module_prelude) + "\n\n" + "\n".join(run_lines)


def expr_to_py(expr: Expr) -> str:
    if isinstance(expr, Num):
        return repr(expr.value)
    if isinstance(expr, String):
        return repr(expr.value)
    if isinstance(expr, Var):
        return f"vars_.get({expr.name!r})"
    if isinstance(expr, RawExpr):
        return f"__eval_expr({expr.src!r})"
    raise TypeError(f"Oh noes! Solar threw an error: Unknown expression: {expr}")


# ---------------- Runtime ----------------
def run_compiled(py_src: str, funcs: dict[str, Callable[..., Any]]) -> None:
    tree = ast.parse(py_src, mode="exec")

    safe_globals = {
        "__builtins__": {
            "__import__": __import__,
            "print": print,
            "eval": eval,
            "compile": compile,
            "NameError": NameError,
            "TypeError": TypeError,
            "ValueError": ValueError,
            "Exception": Exception,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "len": len,
            "range": range,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "min": min,
            "max": max,
            "abs": abs,
            "round": round,
            "getattr": getattr,
            "hasattr": hasattr,
            "callable": callable,
            "isinstance": isinstance,
        },
        "tk": tk,
        "ctk": ctk,
        "ast": ast,
    }

    local_env: dict[str, Any] = {}
    exec(compile(tree, filename="<solar_lang>", mode="exec"), safe_globals, local_env)

    vars_: dict[str, Any] = {}
    local_env["__run"](vars_, funcs)


# ---------------- Built-in functions (advanced) ----------------
def default_funcs() -> dict[str, Callable[..., Any]]:
    import math
    import random

    funcs: dict[str, Callable[..., Any]] = {}

    def _val(x):
        try:
            if hasattr(x, "get") and callable(x.get):
                return x.get()
        except Exception:
            pass
        return x

    def print_many(*items):
        out = []
        for it in items:
            out.append(_val(it))
        print(*out)

    # arithmetic / numeric (print-style)
    funcs["add"] = lambda a, b: print(_val(a) + _val(b))
    funcs["sub"] = lambda a, b: print(_val(a) - _val(b))
    funcs["mul"] = lambda a, b: print(_val(a) * _val(b))
    funcs["div"] = lambda a, b: print(_val(a) / _val(b))
    funcs["mod"] = lambda a, b: print(_val(a) % _val(b))
    funcs["pow"] = lambda a, b: print(_val(a) ** _val(b))
    funcs["abs"] = lambda a: print(abs(_val(a)))
    funcs["min"] = lambda a, b: print(min(_val(a), _val(b)))
    funcs["max"] = lambda a, b: print(max(_val(a), _val(b)))
    funcs["floor"] = lambda a: print(math.floor(_val(a)))
    funcs["ceil"] = lambda a: print(math.ceil(_val(a)))
    funcs["round"] = lambda a: print(round(_val(a)))

    # trig / math
    funcs["sin"] = lambda a: print(math.sin(_val(a)))
    funcs["cos"] = lambda a: print(math.cos(_val(a)))
    funcs["tan"] = lambda a: print(math.tan(_val(a)))
    funcs["sqrt"] = lambda a: print(math.sqrt(_val(a)))

    # random
    funcs["randint"] = lambda a, b: print(random.randint(int(_val(a)), int(_val(b))))
    funcs["rand"] = lambda: print(random.random())

    # strings
    funcs["strlen"] = lambda s: print(len(str(_val(s))))
    funcs["upper"] = lambda s: print(str(_val(s)).upper())
    funcs["lower"] = lambda s: print(str(_val(s)).lower())

    funcs["print_many"] = print_many
    funcs["print"] = print_many

    return funcs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="Path .solar source file")
    args = ap.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        src = f.read()

    program = parse_prog(src)
    py_src = actual_interpreter_func(program)

    funcs = default_funcs()
    run_compiled(py_src, funcs)


if __name__ == "__main__":
    main()
