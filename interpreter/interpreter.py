# Solar Programming Language - Version 1.0
from __future__ import annotations

import argparse # for parsing file
import ast
import shlex
import tkinter as tk
from dataclasses import dataclass
from typing import Any, Callable

# ast nodes
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


# ----- UI AST nodes (new) -----
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


# parser 
def parse_prog(src: str) -> list[Stmt]:
    program: list[Stmt] = []
    for lineno, raw_line in enumerate(src.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        
        # shlex so quotes work
        parts = shlex.split(line)
        if not parts:
            continue
        
        head = parts[0]

        if head == "let":

            if len(parts) < 4 or parts[2] != "=":
                raise SyntaxError(f"Oh noes! Solar threw an error: Line {lineno}: expected `let <name> = <expr>`")
            name = parts[1]
            expr = parse_expr(parts[3], lineno)
            program.append(Let(name, expr))
        
        elif head == "print":
            if len(parts) < 2:
                raise SyntaxError(f"Oh noes! Solar threw an error: Line {lineno}: expected `print <expr>`")
            # allow printing multiple things: print a b c
            # prints each evaluated value separated by spaces
            if len(parts) == 2:
                program.append(Print(parse_expr(parts[1], lineno)))
            else:
                # pack multiple prints as a function call to built-in "print_many"
                args = [parse_expr(p, lineno) for p in parts[1:]]
                program.append(Call("print_many", args))
        
        elif head == "call":
            if len(parts) < 2:
                raise SyntaxError(f"Oh noes! Solar threw an error: Line {lineno}: expected `call <func> [args...]`")
            func_name = parts[1]
            args = [parse_expr(p, lineno) for p in parts[2:]]
            program.append(Call(func_name, args))

        elif head == "ui":
            if len(parts) < 3:
                raise SyntaxError(f"Oh noes! Solar threw an error: Line {lineno}: bad ui statement")

            cmd = parts[1]

            if cmd == "window":
                # ui window main
                program.append(UiWindow(parts[2]))

            elif cmd == "title":
                # ui title main "Solar App"
                program.append(UiTitle(parts[2], parse_expr(parts[3], lineno)))

            elif cmd == "size":
                # ui size main 420 240
                program.append(UiSize(parts[2], parse_expr(parts[3], lineno), parse_expr(parts[4], lineno)))

            elif cmd == "bg":
                # ui bg main "#202020"
                program.append(UiBg(parts[2], parse_expr(parts[3], lineno)))

            elif cmd == "fg":
                # ui fg main "#ffffff"
                program.append(UiFg(parts[2], parse_expr(parts[3], lineno)))

            elif cmd == "label":
                # ui label win name text at x y
                if "at" not in parts:
                    raise SyntaxError(f"Oh noes! Solar threw an error: Line {lineno}: label needs `at x y`")
                at_i = parts.index("at")
                win = parts[2]
                name = parts[3]
                text = parse_expr(parts[4], lineno)
                x = parse_expr(parts[at_i + 1], lineno)
                y = parse_expr(parts[at_i + 2], lineno)
                program.append(UiLabel(win, name, text, x, y))

            elif cmd == "button":
                # ui button win name text at x y do func args...
                if "at" not in parts or "do" not in parts:
                    raise SyntaxError(f"Oh noes! Solar threw an error: Line {lineno}: button needs `at x y do ...`")
                at_i = parts.index("at")
                do_i = parts.index("do")

                win = parts[2]
                name = parts[3]
                text = parse_expr(parts[4], lineno)
                x = parse_expr(parts[at_i + 1], lineno)
                y = parse_expr(parts[at_i + 2], lineno)

                func_name = parts[do_i + 1]
                args = [parse_expr(p, lineno) for p in parts[do_i + 2:]]
                on_call = Call(func_name, args)

                program.append(UiButton(win, name, text, x, y, on_call))

            elif cmd == "entry":
                # ui entry win name at x y
                if "at" not in parts:
                    raise SyntaxError(f"Oh noes! Solar threw an error: Line {lineno}: entry needs `at x y`")
                at_i = parts.index("at")
                program.append(UiEntry(parts[2], parts[3], parse_expr(parts[at_i + 1], lineno), parse_expr(parts[at_i + 2], lineno)))

            elif cmd == "slider":
                # ui slider win name from a to b at x y
                if "from" not in parts or "to" not in parts or "at" not in parts:
                    raise SyntaxError(f"Oh noes! Solar threw an error: Line {lineno}: slider needs `from a to b at x y`")
                from_i = parts.index("from")
                to_i = parts.index("to")
                at_i = parts.index("at")
                program.append(
                    UiSlider(
                        parts[2],
                        parts[3],
                        parse_expr(parts[from_i + 1], lineno),
                        parse_expr(parts[to_i + 1], lineno),
                        parse_expr(parts[at_i + 1], lineno),
                        parse_expr(parts[at_i + 2], lineno),
                    )
                )

            elif cmd == "checkbox":
                # ui checkbox win name "text" at x y
                if "at" not in parts:
                    raise SyntaxError(f"Oh noes! Solar threw an error: Line {lineno}: checkbox needs `at x y`")
                at_i = parts.index("at")
                win = parts[2]
                name = parts[3]
                text = parse_expr(parts[4], lineno)
                x = parse_expr(parts[at_i + 1], lineno)
                y = parse_expr(parts[at_i + 2], lineno)
                program.append(UiCheckbox(win, name, text, x, y))

            elif cmd == "bind":
                # ui bind win Key do func args...
                if "do" not in parts:
                    raise SyntaxError(f"Oh noes! Solar threw an error: Line {lineno}: bind needs `do ...`")
                do_i = parts.index("do")
                key = parts[3]
                func = parts[do_i + 1]
                args = [parse_expr(p, lineno) for p in parts[do_i + 2:]]
                program.append(UiBind(parts[2], key, Call(func, args)))

            elif cmd == "text":
                # ui text widgetName "new text"
                program.append(UiText(parts[2], parse_expr(parts[3], lineno)))

            elif cmd == "set":
                # ui set varname value
                program.append(UiSet(parts[2], parse_expr(parts[3], lineno)))

            elif cmd == "get":
                # ui get varname into target
                if len(parts) < 5 or parts[3] != "into":
                    raise SyntaxError(f"Oh noes! Solar threw an error: Line {lineno}: expected `ui get <var> into <name>`")
                program.append(UiGetInto(parts[2], parts[4]))

            elif cmd == "run":
                # ui run main
                program.append(UiRun(parts[2]))

            else:
                raise SyntaxError(f"Oh noes! Solar threw an error: Line {lineno}: unknown ui command: {cmd}")

        else:
            func_name = head
            args = [parse_expr(p, lineno) for p in parts[1:]]
            program.append(Call(func_name, args))
        
    return program

def parse_expr(token: str, lineno: int) -> Expr:
    # shlex already removed quotes, still for good measure we can detect string literals by attempting some shitty numeric conversion or idk what was it called
    # this is a minimal version, i'd need to tokenize properly; but i dont have time for that shit.
    try:
        if "." in token:
            return Num(float(token))
        return Num(int(token))
    except ValueError:
        # if it looks like an identifier but you just cant prove it, the interpreter treats it as a var, otherwise we (yes we) think its a string.
        if token.isidentifier():
            return Var(token)
        return String(token)


# actual interpreter (ast -> python ast -> python source)
def actual_interpreter_func(program: list[Stmt]) -> str:
    # this will generrate python code that uses
    # 'vars_' dict for variables
    # 'funcs' dict for dynamic functions
    # 'print' is allowed
    lines: list[str] = []
    lines.append("def __run(vars_, funcs):") # i believe this structures the whole running the program logic
    lines.append("    # vars_: variable storage, funcs: callable registry") # some comment that has no right to be there but still putting it in for good measure
    lines.append("    __wins = {}")
    lines.append("    __widgets = {}")
    lines.append("    __uivars = {}")

    for st in program:
        if isinstance(st, Let):
            py_expr = expr_to_py(st.expr)
            lines.append(f"    vars_[{st.name!r}] = {py_expr}")

        elif isinstance(st, Print):
            py_expr = expr_to_py(st.expr)
            lines.append(f"    print({py_expr})")

        elif isinstance(st, Call):
            args = ", ".join(expr_to_py(a) for a in st.args)
            # call from funcs registry; error if missing
            lines.append(f"    _fn = funcs.get({st.func_name!r})")
            lines.append(f"    if _fn is None: raise NameError('Oh noes! Solar threw an error: Unknown function: {st.func_name}')")
            lines.append(f"    _fn({args})")

        elif isinstance(st, UiWindow):
            lines.append(f"    __wins[{st.name!r}] = tk.Tk()")

        elif isinstance(st, UiTitle):
            lines.append(f"    __wins[{st.win!r}].title({expr_to_py(st.title)})")

        elif isinstance(st, UiSize):
            lines.append(f"    __wins[{st.win!r}].geometry(str({expr_to_py(st.w)}) + 'x' + str({expr_to_py(st.h)}))")

        elif isinstance(st, UiBg):
            lines.append(f"    __wins[{st.win!r}].configure(bg={expr_to_py(st.color)})")

        elif isinstance(st, UiFg):
            lines.append(f"    __wins[{st.win!r}].configure(fg={expr_to_py(st.color)})")

        elif isinstance(st, UiLabel):
            lines.append(f"    __widgets[{st.name!r}] = tk.Label(__wins[{st.win!r}], text={expr_to_py(st.text)})")
            lines.append(f"    __widgets[{st.name!r}].place(x={expr_to_py(st.x)}, y={expr_to_py(st.y)})")

        elif isinstance(st, UiButton):
            fn = st.on_call.func_name
            args = ", ".join(expr_to_py(a) for a in st.on_call.args)
            lines.append(f"    def __cb_{st.name}():")
            lines.append(f"        _fn = funcs.get({fn!r})")
            lines.append(f"        if _fn is None: raise NameError('Oh noes! Solar threw an error: Unknown function: {fn}')")
            lines.append(f"        _fn({args})")
            lines.append(f"    __widgets[{st.name!r}] = tk.Button(__wins[{st.win!r}], text={expr_to_py(st.text)}, command=__cb_{st.name})")
            lines.append(f"    __widgets[{st.name!r}].place(x={expr_to_py(st.x)}, y={expr_to_py(st.y)})")

        elif isinstance(st, UiEntry):
            lines.append(f"    __uivars[{st.name!r}] = tk.StringVar()")
            lines.append(f"    __widgets[{st.name!r}] = tk.Entry(__wins[{st.win!r}], textvariable=__uivars[{st.name!r}])")
            lines.append(f"    __widgets[{st.name!r}].place(x={expr_to_py(st.x)}, y={expr_to_py(st.y)})")
            lines.append(f"    vars_[{st.name!r}] = __uivars[{st.name!r}]")

        elif isinstance(st, UiSlider):
            lines.append(f"    __uivars[{st.name!r}] = tk.IntVar()")
            lines.append(f"    __widgets[{st.name!r}] = tk.Scale(__wins[{st.win!r}], from_={expr_to_py(st.minv)}, to={expr_to_py(st.maxv)}, orient='horizontal', variable=__uivars[{st.name!r}])")
            lines.append(f"    __widgets[{st.name!r}].place(x={expr_to_py(st.x)}, y={expr_to_py(st.y)})")
            lines.append(f"    vars_[{st.name!r}] = __uivars[{st.name!r}]")

        elif isinstance(st, UiCheckbox):
            # checkbox stores 0/1 in an IntVar
            lines.append(f"    __uivars[{st.name!r}] = tk.IntVar()")
            lines.append(f"    __widgets[{st.name!r}] = tk.Checkbutton(__wins[{st.win!r}], text={expr_to_py(st.text)}, variable=__uivars[{st.name!r}])")
            lines.append(f"    __widgets[{st.name!r}].place(x={expr_to_py(st.x)}, y={expr_to_py(st.y)})")
            lines.append(f"    vars_[{st.name!r}] = __uivars[{st.name!r}]")

        elif isinstance(st, UiBind):
            fn = st.call.func_name
            args = ", ".join(expr_to_py(a) for a in st.call.args)
            lines.append(f"    def __bind_{fn}(event=None):")
            lines.append(f"        _fn = funcs.get({fn!r})")
            lines.append(f"        if _fn is None: raise NameError('Oh noes! Solar threw an error: Unknown function: {fn}')")
            lines.append(f"        _fn({args})")
            lines.append(f"    __wins[{st.win!r}].bind('<{st.key}>', __bind_{fn})")

        elif isinstance(st, UiText):
            # change text on widgets (label/button/checkbox etc)
            lines.append(f"    __w = __widgets.get({st.widget!r})")
            lines.append(f"    if __w is None: raise NameError('Oh noes! Solar threw an error: Unknown widget: {st.widget}')")
            lines.append(f"    __w.config(text={expr_to_py(st.text)})")

        elif isinstance(st, UiSet):
            # set ui variable value (entry/slider/checkbox)
            # works if vars_[name] is a tk variable (StringVar/IntVar)
            lines.append(f"    __v = vars_.get({st.varname!r})")
            lines.append(f"    if __v is None: raise NameError('Oh noes! Solar threw an error: Unknown ui var: {st.varname}')")
            lines.append(f"    try:")
            lines.append(f"        __v.set({expr_to_py(st.value)})")
            lines.append(f"    except Exception:")
            lines.append(f"        vars_[{st.varname!r}] = {expr_to_py(st.value)}")

        elif isinstance(st, UiGetInto):
            # get ui variable value into a normal solar variable
            lines.append(f"    __v = vars_.get({st.varname!r})")
            lines.append(f"    if __v is None: raise NameError('Oh noes! Solar threw an error: Unknown ui var: {st.varname}')")
            lines.append(f"    try:")
            lines.append(f"        vars_[{st.target!r}] = __v.get()")
            lines.append(f"    except Exception:")
            lines.append(f"        vars_[{st.target!r}] = __v")

        elif isinstance(st, UiRun):
            lines.append(f"    __wins[{st.win!r}].mainloop()")

        else:
            raise TypeError(f"Oh noes! Solar threw an error: Unknown statement: {st}")
        
    lines.append("")
    lines.append("# end")
    return "\n".join(lines)


# solar expression to py
def expr_to_py(expr: Expr) -> str:
    if isinstance(expr, Num):
        return repr(expr.value)
    if isinstance(expr, String):
        return repr(expr.value)
    if isinstance(expr, Var):
        # variables live in vars_
        # if it's a tk variable, .get() will be called at runtime by funcs you write,
        # but we also support printing tk vars by auto .get() in print_many below.
        return f"vars_.get({expr.name!r})"
    raise TypeError(f"Oh noes! Solar threw an error: Unknown expression: {expr}")

# runtime: sandbox-ish exec
def run_compiled(py_src: str, funcs: dict[str, Callable[..., Any]]) -> None:
    # parse to ensure its valid py code and optionally inspect ast for safety
    tree = ast.parse(py_src, mode="exec")

    # this is not a true sandbox
    # it just limits some stuff that we put into globals
    safe_globals = {
        "__builtins__": {
            "print": print,
            "NameError": NameError,
            "TypeError": TypeError,
            "ValueError": ValueError,
            "Exception": Exception,
            "str": str,
            "int": int,
            "float": float,
        },
        "tk": tk,
    }

    local_env: dict[str, Any] = {}
    exec(compile(tree, filename="<solar_lang>", mode="exec"), safe_globals, local_env)
    vars_: dict[str, Any] = {}
    local_env["__run"](vars_, funcs)


    
    local_env: dict[str, Any] = {}
    exec(compile(tree, filename="<solar_lang>", mode="exec"), safe_globals, local_env)
    vars_: dict[str, Any] = {}
    local_env["__run"](vars_, funcs)

# dynamic function registry
def default_funcs() -> dict[str, Callable[..., Any]]:
    funcs: dict[str, Callable[..., Any]] = {}

    def add(a, b):
        print(a + b)
    
    def mul(a, b):
        print(a * b)

    # helper: print multiple things nicely
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
