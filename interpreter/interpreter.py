# Solar v1.0.1 - A big jump from v1.0.0
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


# ----- UI AST nodes -----
@dataclass
class UiWindow(Stmt):
    name: str


@dataclass
class UiTitle(Stmt):
    win: str
    title: Expr


@dataclass
class UiSize(Stmt):
    win: str
    w: Expr
    h: Expr


@dataclass
class UiBg(Stmt):
    win: str
    color: Expr


@dataclass
class UiFg(Stmt):
    win: str
    color: Expr


@dataclass
class UiLabel(Stmt):
    win: str
    name: str
    text: Expr
    x: Expr
    y: Expr


@dataclass
class UiButton(Stmt):
    win: str
    name: str
    text: Expr
    x: Expr
    y: Expr
    on_call: Call


@dataclass
class UiEntry(Stmt):
    win: str
    name: str
    x: Expr
    y: Expr


@dataclass
class UiSlider(Stmt):
    win: str
    name: str
    minv: Expr
    maxv: Expr
    x: Expr
    y: Expr


@dataclass
class UiCheckbox(Stmt):
    win: str
    name: str
    text: Expr
    x: Expr
    y: Expr


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
    text: Expr


@dataclass
class UiSet(Stmt):
    varname: str
    value: Expr


@dataclass
class UiGetInto(Stmt):
    varname: str
    target: str


# ---------------- Tokenizer (keeps whether token was quoted) ----------------
def tokenize_line(line: str) -> list[tuple[str, bool]]:
    """
    Returns [(token, was_quoted), ...]
    - Supports "..." and '...'
    - Supports backslash escapes inside strings: \" \n etc (simple: keeps escaped char)
    - Splits on whitespace outside strings
    """
    tokens: list[tuple[str, bool]] = []
    i = 0
    n = len(line)

    while i < n:
        while i < n and line[i].isspace():
            i += 1
        if i >= n:
            break

        ch = line[i]
        if ch in ('"', "'"):
            q = ch
            i += 1
            out: list[str] = []
            while i < n:
                if line[i] == "\\" and i + 1 < n:
                    # simple escape: keep next char as-is
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
            tokens.append(("".join(out), True))
        else:
            start = i
            while i < n and not line[i].isspace():
                i += 1
            tokens.append((line[start:i], False))

    return tokens


# ---------------- Python passthrough detection ----------------
def starts_python_block(raw_line: str) -> bool:
    s = raw_line.lstrip()
    if not s:
        return False

    starters = (
        "def ",
        "class ",
        "if ",
        "elif ",
        "else:",
        "for ",
        "while ",
        "try:",
        "except",
        "finally:",
        "with ",
        "@",  # decorators
    )
    if s.startswith(starters):
        return True

    return s.rstrip().endswith(":")


def looks_like_python_single_line(raw_line: str) -> bool:
    """
    Single-line python that should NOT be parsed as Solar.
    Fixes cases like:
      funcs["greet"] = greet_bridge
      x = 123
      import something
    """
    s = raw_line.lstrip()
    if not s:
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

        # blank lines
        if not line.strip():
            if in_py_block:
                program.append(PyRaw(line))
            continue

        # comment lines
        if line.lstrip().startswith("#"):
            if in_py_block:
                program.append(PyRaw(line))
            continue

        # if inside a python block, any indented line stays python
        if in_py_block:
            if line.startswith((" ", "\t")):
                program.append(PyRaw(line))
                continue
            in_py_block = False  # dedent ends python block

        # contain <module> -> import <module>
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

        # python block start?
        if starts_python_block(line):
            program.append(PyRaw(line))
            in_py_block = True
            continue

        # python single line?
        if looks_like_python_single_line(line):
            program.append(PyRaw(line))
            continue

        # otherwise try Solar; on SyntaxError, passthrough as python line
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

    if head == "let":
        if len(parts) < 4 or parts[2] != "=":
            raise SyntaxError(
                f"Oh noes! Solar threw an error: Line {lineno}: expected `let <name> = <expr>`"
            )
        name = parts[1]
        expr = parse_expr(parts[3], lineno, quoted[3])
        return Let(name, expr)

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

    # default: treat as Solar call command: add 1 2
    func_name = head
    args = [parse_expr(parts[i], lineno, quoted[i]) for i in range(1, len(parts))]
    return Call(func_name, args)


def parse_expr(token: str, lineno: int, was_quoted: bool) -> Expr:
    # If it was quoted, it is ALWAYS a string literal (fixes CTkButton text bug)
    if was_quoted:
        return String(token)

    try:
        if "." in token:
            return Num(float(token))
        return Num(int(token))
    except ValueError:
        if token.isidentifier():
            return Var(token)
        return String(token)


# ---------------- Compilation (AST -> Python source) ----------------
def actual_interpreter_func(program: list[Stmt]) -> str:
    module_prelude: list[str] = []
    run_lines: list[str] = []

    seen_imports: set[str] = set()

    module_prelude.append("# --- compiled by Solar v1.0.1 ---")

    run_lines.append("def __run(vars_, funcs):")
    run_lines.append("    # vars_: variable storage, funcs: callable registry")
    run_lines.append("    __wins = {}")
    run_lines.append("    __widgets = {}")
    run_lines.append("    __uivars = {}")
    run_lines.append("    __uistyle = {}  # per-window defaults: {'bg': ..., 'fg': ...}")
    run_lines.append("")
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
    run_lines.append("")
    run_lines.append("        # Never touch CTkButton here; we'll set its text_color at creation.")
    run_lines.append("        try:")
    run_lines.append("            cls = widget.__class__.__name__")
    run_lines.append("        except Exception:")
    run_lines.append("            cls = ''")
    run_lines.append("        if cls == 'CTkButton':")
    run_lines.append("            return")
    run_lines.append("")
    run_lines.append("        __safe_config(widget, text_color=fg)")
    run_lines.append("")

    for st in program:
        if isinstance(st, ContainImport):
            if st.module not in seen_imports:
                module_prelude.append(f"import {st.module}")
                seen_imports.add(st.module)
            continue

        if isinstance(st, PyRaw):
            run_lines.append("    " + st.raw)
            continue

        if isinstance(st, Let):
            run_lines.append(f"    vars_[{st.name!r}] = {expr_to_py(st.expr)}")
            continue

        if isinstance(st, Print):
            run_lines.append(f"    print({expr_to_py(st.expr)})")
            continue

        if isinstance(st, Call):
            args = ", ".join(expr_to_py(a) for a in st.args)
            run_lines.append(f"    _fn = funcs.get({st.func_name!r})")
            run_lines.append(
                f"    if _fn is None: raise NameError('Oh noes! Solar threw an error: Unknown function: {st.func_name}')"
            )
            run_lines.append(f"    _fn({args})")
            continue

        if isinstance(st, UiWindow):
            run_lines.append(f"    __wins[{st.name!r}] = ctk.CTk()")
            run_lines.append(f"    __uistyle[{st.name!r}] = {{'bg': None, 'fg': None}}")
            run_lines.append(f"    __apply_style({st.name!r}, __wins[{st.name!r}], 'root')")
            continue

        if isinstance(st, UiTitle):
            run_lines.append(f"    __wins[{st.win!r}].title({expr_to_py(st.title)})")
            continue

        if isinstance(st, UiSize):
            run_lines.append(
                f"    __wins[{st.win!r}].geometry(str({expr_to_py(st.w)}) + 'x' + str({expr_to_py(st.h)}))"
            )
            continue

        if isinstance(st, UiBg):
            run_lines.append(
                f"    __uistyle.setdefault({st.win!r}, {{'bg': None, 'fg': None}})['bg'] = {expr_to_py(st.color)}"
            )
            run_lines.append(f"    __apply_style({st.win!r}, __wins[{st.win!r}], 'root')")
            run_lines.append("    for __n, __w in list(__widgets.items()):")
            run_lines.append("        try:")
            run_lines.append(f"            if getattr(__w, 'master', None) is __wins[{st.win!r}]:")
            run_lines.append(f"                __apply_style({st.win!r}, __w, 'widget')")
            run_lines.append("        except Exception:")
            run_lines.append("            pass")
            continue

        if isinstance(st, UiFg):
            run_lines.append(
                f"    __uistyle.setdefault({st.win!r}, {{'bg': None, 'fg': None}})['fg'] = {expr_to_py(st.color)}"
            )
            run_lines.append("    for __n, __w in list(__widgets.items()):")
            run_lines.append("        try:")
            run_lines.append(f"            if getattr(__w, 'master', None) is __wins[{st.win!r}]:")
            run_lines.append(f"                __apply_style({st.win!r}, __w, 'widget')")
            run_lines.append("        except Exception:")
            run_lines.append("            pass")
            continue

        if isinstance(st, UiLabel):
            run_lines.append(
                f"    __widgets[{st.name!r}] = ctk.CTkLabel(__wins[{st.win!r}], text={expr_to_py(st.text)})"
            )
            run_lines.append(f"    __apply_style({st.win!r}, __widgets[{st.name!r}], 'widget')")
            run_lines.append(
                f"    __widgets[{st.name!r}].place(x={expr_to_py(st.x)}, y={expr_to_py(st.y)})"
            )
            continue

        if isinstance(st, UiButton):
            fn = st.on_call.func_name
            args = ", ".join(expr_to_py(a) for a in st.on_call.args)

            cb_name = f"__cb_{st.name}"
            run_lines.append(f"    def {cb_name}():")
            run_lines.append(f"        _fn = funcs.get({fn!r})")
            run_lines.append(
                f"        if _fn is None: raise NameError('Oh noes! Solar threw an error: Unknown function: {fn}')"
            )
            run_lines.append(f"        _fn({args})")

            # Set CTkButton text_color at creation using window fg (fixes invisible text)
            run_lines.append(f"    __st = __style_defaults({st.win!r})")
            run_lines.append("    __btn_tc = __st.get('fg')")
            run_lines.append(
                f"    __widgets[{st.name!r}] = ctk.CTkButton(__wins[{st.win!r}], text={expr_to_py(st.text)}, command={cb_name}, text_color=__btn_tc if __btn_tc is not None else None)"
            )
            run_lines.append(
                f"    __widgets[{st.name!r}].place(x={expr_to_py(st.x)}, y={expr_to_py(st.y)})"
            )
            continue

        if isinstance(st, UiEntry):
            run_lines.append(f"    __uivars[{st.name!r}] = tk.StringVar()")
            run_lines.append(
                f"    __widgets[{st.name!r}] = ctk.CTkEntry(__wins[{st.win!r}], textvariable=__uivars[{st.name!r}])"
            )
            run_lines.append(f"    __apply_style({st.win!r}, __widgets[{st.name!r}], 'widget')")
            run_lines.append(
                f"    __widgets[{st.name!r}].place(x={expr_to_py(st.x)}, y={expr_to_py(st.y)})"
            )
            run_lines.append(f"    vars_[{st.name!r}] = __uivars[{st.name!r}]")
            continue

        if isinstance(st, UiSlider):
            run_lines.append(f"    __uivars[{st.name!r}] = tk.IntVar()")
            run_lines.append(
                f"    __widgets[{st.name!r}] = ctk.CTkSlider(__wins[{st.win!r}], from_={expr_to_py(st.minv)}, to={expr_to_py(st.maxv)}, variable=__uivars[{st.name!r}])"
            )
            run_lines.append(f"    __apply_style({st.win!r}, __widgets[{st.name!r}], 'widget')")
            run_lines.append(
                f"    __widgets[{st.name!r}].place(x={expr_to_py(st.x)}, y={expr_to_py(st.y)})"
            )
            run_lines.append(f"    vars_[{st.name!r}] = __uivars[{st.name!r}]")
            continue

        if isinstance(st, UiCheckbox):
            run_lines.append(f"    __uivars[{st.name!r}] = tk.IntVar()")
            run_lines.append(
                f"    __widgets[{st.name!r}] = ctk.CTkCheckBox(__wins[{st.win!r}], text={expr_to_py(st.text)}, variable=__uivars[{st.name!r}])"
            )
            run_lines.append(f"    __apply_style({st.win!r}, __widgets[{st.name!r}], 'widget')")
            run_lines.append(
                f"    __widgets[{st.name!r}].place(x={expr_to_py(st.x)}, y={expr_to_py(st.y)})"
            )
            run_lines.append(f"    vars_[{st.name!r}] = __uivars[{st.name!r}]")
            continue

        if isinstance(st, UiBind):
            fn = st.call.func_name
            args = ", ".join(expr_to_py(a) for a in st.call.args)
            bind_name = f"__bind_{fn}"

            run_lines.append(f"    def {bind_name}(event=None):")
            run_lines.append(f"        _fn = funcs.get({fn!r})")
            run_lines.append(
                f"        if _fn is None: raise NameError('Oh noes! Solar threw an error: Unknown function: {fn}')"
            )
            run_lines.append(f"        _fn({args})")
            run_lines.append(f"    __wins[{st.win!r}].bind('<{st.key}>', {bind_name})")
            continue

        if isinstance(st, UiText):
            run_lines.append(f"    __w = __widgets.get({st.widget!r})")
            run_lines.append(
                f"    if __w is None: raise NameError('Oh noes! Solar threw an error: Unknown widget: {st.widget}')"
            )
            run_lines.append("    try:")
            run_lines.append(f"        __w.configure(text={expr_to_py(st.text)})")
            run_lines.append("    except Exception:")
            run_lines.append("        pass")
            continue

        if isinstance(st, UiSet):
            run_lines.append(f"    __v = vars_.get({st.varname!r})")
            run_lines.append(
                f"    if __v is None: raise NameError('Oh noes! Solar threw an error: Unknown ui var: {st.varname}')"
            )
            run_lines.append("    try:")
            run_lines.append(f"        __v.set({expr_to_py(st.value)})")
            run_lines.append("    except Exception:")
            run_lines.append(f"        vars_[{st.varname!r}] = {expr_to_py(st.value)}")
            continue

        if isinstance(st, UiGetInto):
            run_lines.append(f"    __v = vars_.get({st.varname!r})")
            run_lines.append(
                f"    if __v is None: raise NameError('Oh noes! Solar threw an error: Unknown ui var: {st.varname}')"
            )
            run_lines.append("    try:")
            run_lines.append(f"        vars_[{st.target!r}] = __v.get()")
            run_lines.append("    except Exception:")
            run_lines.append(f"        vars_[{st.target!r}] = __v")
            continue

        if isinstance(st, UiRun):
            run_lines.append(f"    __wins[{st.win!r}].mainloop()")
            continue

        raise TypeError(f"Oh noes! Solar threw an error: Unknown statement: {st}")

    run_lines.append("")
    run_lines.append("# end")

    return "\n".join(module_prelude) + "\n\n" + "\n".join(run_lines)


def expr_to_py(expr: Expr) -> str:
    if isinstance(expr, Num):
        return repr(expr.value)
    if isinstance(expr, String):
        return repr(expr.value)
    if isinstance(expr, Var):
        return f"vars_.get({expr.name!r})"
    raise TypeError(f"Oh noes! Solar threw an error: Unknown expression: {expr}")


# ---------------- Runtime ----------------
def run_compiled(py_src: str, funcs: dict[str, Callable[..., Any]]) -> None:
    tree = ast.parse(py_src, mode="exec")

    safe_globals = {
        "__builtins__": {
            "__import__": __import__,
            "print": print,
            "NameError": NameError,
            "TypeError": TypeError,
            "ValueError": ValueError,
            "Exception": Exception,
            "str": str,
            "int": int,
            "float": float,
            "len": len,
            "range": range,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "getattr": getattr,
            "hasattr": hasattr,
            "callable": callable,
        },
        "tk": tk,
        "ctk": ctk,
    }

    local_env: dict[str, Any] = {}
    exec(compile(tree, filename="<solar_lang>", mode="exec"), safe_globals, local_env)

    vars_: dict[str, Any] = {}
    local_env["__run"](vars_, funcs)


def default_funcs() -> dict[str, Callable[..., Any]]:
    funcs: dict[str, Callable[..., Any]] = {}

    def add(a, b):
        print(a + b)

    def mul(a, b):
        print(a * b)

    def print_many(*items):
        out = []
        for it in items:
            try:
                if hasattr(it, "get") and callable(it.get):
                    out.append(it.get())
                else:
                    out.append(it)
            except Exception:
                out.append(it)
        print(*out)

    funcs["add"] = add
    funcs["mul"] = mul
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
