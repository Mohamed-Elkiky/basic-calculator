# Basic Calculator - Tkinter UI
# Run: python main.py
# Requirements: Python 3.x with Tkinter (usually bundled). No pip install needed.

import ast
import re
import tkinter as tk
from tkinter import font as tkfont


# --- Safe evaluator (no eval) ---

ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow)
ALLOWED_UNARY = (ast.USub, ast.UAdd)


def safe_eval(expr: str):
    """
    Safely evaluate a numeric expression using ast.
    Only numbers, unary +/-, and binary + - * / % ** are allowed.
    Returns (result_float, None) on success or (None, error_message) on failure.
    """
    expr = expr.strip().replace("^", "**")
    if not expr:
        return None, "Empty expression"
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        return None, f"Invalid expression: {e.msg}"

    def eval_node(node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return float(node.value)
            return None
        if isinstance(node, ast.UnaryOp):
            if type(node.op) not in ALLOWED_UNARY:
                raise ValueError("Unsupported unary operator")
            val = eval_node(node.operand)
            if val is None:
                return None
            return -val if type(node.op) == ast.USub else val
        if isinstance(node, ast.BinOp):
            if type(node.op) not in ALLOWED_BINOPS:
                raise ValueError("Unsupported operator")
            left = eval_node(node.left)
            right = eval_node(node.right)
            if left is None or right is None:
                return None
            if type(node.op) == ast.Add:
                return left + right
            if type(node.op) == ast.Sub:
                return left - right
            if type(node.op) == ast.Mult:
                return left * right
            if type(node.op) == ast.Div:
                if right == 0:
                    raise ZeroDivisionError("Division by zero")
                return left / right
            if type(node.op) == ast.Mod:
                if right == 0:
                    raise ZeroDivisionError("Modulo by zero")
                return left % right
            if type(node.op) == ast.Pow:
                return left ** right
        raise ValueError("Unsupported expression node")

    try:
        result = eval_node(tree.body)
        if result is None:
            return None, "Invalid expression"
        return result, None
    except ZeroDivisionError as e:
        return None, str(e)
    except (ValueError, TypeError) as e:
        return None, str(e)


def format_result(value: float) -> str:
    """Format number: integers without .0, trim floating noise."""
    if value != value:  # NaN
        return "Error"
    if value == float("inf") or value == float("-inf"):
        return "Error"
    if isinstance(value, int) or (isinstance(value, float) and value == int(value)):
        return str(int(value))
    s = f"{value:.10g}"
    if "e" in s.lower():
        return s
    s = s.rstrip("0").rstrip(".")
    return s if s else "0"


def display_expr(expr: str) -> str:
    """Convert internal operators to display symbols: * -> ×, / -> ÷, ** -> ^."""
    s = expr.replace("**", "^").replace("*", "×").replace("/", "÷")
    return s


def internal_expr(display: str) -> str:
    """Convert display back to internal: × -> *, ÷ -> /, ^ -> **."""
    s = display.replace("×", "*").replace("÷", "/").replace("^", "**")
    return s


# --- Main App ---

class CalculatorApp:
    COLORS = {
        "bg": "#1a1b26",
        "panel": "#24283b",
        "display_bg": "#16161e",
        "display_fg": "#a9b1d6",
        "display_sub_fg": "#565f89",
        "num_bg": "#32344a",
        "num_fg": "#c0caf5",
        "num_hover": "#414868",
        "op_bg": "#394b70",
        "op_fg": "#7aa2f7",
        "op_hover": "#4a5f8a",
        "equals_bg": "#9ece6a",
        "equals_fg": "#1a1b26",
        "equals_hover": "#b9f27c",
        "danger_bg": "#f7768e",
        "danger_fg": "#1a1b26",
        "danger_hover": "#ff9db3",
        "special_bg": "#7dcfff",
        "special_fg": "#1a1b26",
        "special_hover": "#a5d6ff",
    }

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Calculator")
        self.root.configure(bg=self.COLORS["bg"])
        self.root.resizable(True, True)
        self.root.minsize(320, 420)

        self.expression = ""
        self.last_ans = None
        self.history_list: list[tuple[str, str]] = []  # (display_expr, result_str)
        self.sub_display_text = ""

        self._build_ui()
        self._bind_keys()

    def _build_ui(self):
        # Main container with padding
        main = tk.Frame(self.root, bg=self.COLORS["bg"], padx=12, pady=12)
        main.pack(fill=tk.BOTH, expand=True)

        # --- Displays ---
        disp_frame = tk.Frame(main, bg=self.COLORS["bg"])
        disp_frame.pack(fill=tk.X, pady=(0, 8))

        self.sub_display = tk.Label(
            disp_frame,
            text="",
            font=tkfont.Font(family="Consolas", size=11),
            fg=self.COLORS["display_sub_fg"],
            bg=self.COLORS["display_bg"],
            anchor="e",
            padx=12,
            pady=6,
        )
        self.sub_display.pack(fill=tk.X, pady=(0, 2))

        self.main_display = tk.Label(
            disp_frame,
            text="0",
            font=tkfont.Font(family="Consolas", size=28, weight="bold"),
            fg=self.COLORS["display_fg"],
            bg=self.COLORS["display_bg"],
            anchor="e",
            padx=12,
            pady=12,
        )
        self.main_display.pack(fill=tk.X)

        for w in (self.sub_display, self.main_display):
            w.bind("<Configure>", lambda e, w=w: w.config(wraplength=w.winfo_width() - 24))

        # --- History panel ---
        hist_frame = tk.Frame(main, bg=self.COLORS["panel"], padx=8, pady=6)
        hist_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        tk.Label(
            hist_frame,
            text="History",
            font=tkfont.Font(size=10, weight="bold"),
            fg=self.COLORS["display_sub_fg"],
            bg=self.COLORS["panel"],
        ).pack(anchor="w")
        self.history_label = tk.Label(
            hist_frame,
            text="",
            font=tkfont.Font(family="Consolas", size=10),
            fg=self.COLORS["display_sub_fg"],
            bg=self.COLORS["panel"],
            anchor="nw",
            justify=tk.LEFT,
        )
        self.history_label.pack(fill=tk.BOTH, expand=True, anchor="nw")
        self._update_history_display()

        # --- Buttons grid ---
        btn_frame = tk.Frame(main, bg=self.COLORS["bg"])
        btn_frame.pack(fill=tk.X)

        grid_spec = [
            ("C", "danger", "⌫", "danger", "(", "op", ")", "op", "%", "op"),
            ("7", "num", "8", "num", "9", "num", "÷", "op", "^", "op"),
            ("4", "num", "5", "num", "6", "num", "×", "op", "ANS", "special"),
            ("1", "num", "2", "num", "3", "num", "-", "op", "+/-", "special"),
            ("0", "num", ".", "num", "=", "equals", "+", "op", "", ""),
        ]

        for row_idx, row in enumerate(grid_spec):
            for col_idx in range(0, len(row), 2):
                label = row[col_idx]
                kind = row[col_idx + 1] if col_idx + 1 < len(row) else ""
                if not label:
                    continue
                btn = self._make_button(btn_frame, label, kind, row_idx, col_idx // 2)
                btn.grid(row=row_idx, column=col_idx // 2, padx=3, pady=3, sticky="nsew")

        for c in range(5):
            btn_frame.columnconfigure(c, weight=1)
        for r in range(5):
            btn_frame.rowconfigure(r, weight=1)

    def _make_button(self, parent, label: str, kind: str, row: int, col: int) -> tk.Button:
        if kind == "num":
            bg, fg, hover = self.COLORS["num_bg"], self.COLORS["num_fg"], self.COLORS["num_hover"]
        elif kind == "op":
            bg, fg, hover = self.COLORS["op_bg"], self.COLORS["op_fg"], self.COLORS["op_hover"]
        elif kind == "equals":
            bg, fg, hover = self.COLORS["equals_bg"], self.COLORS["equals_fg"], self.COLORS["equals_hover"]
        elif kind == "danger":
            bg, fg, hover = self.COLORS["danger_bg"], self.COLORS["danger_fg"], self.COLORS["danger_hover"]
        else:
            bg, fg, hover = self.COLORS["special_bg"], self.COLORS["special_fg"], self.COLORS["special_hover"]

        btn = tk.Button(
            parent,
            text=label,
            font=tkfont.Font(family="Segoe UI", size=14, weight="bold"),
            bg=bg,
            fg=fg,
            activebackground=hover,
            activeforeground=fg,
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            padx=8,
            pady=12,
            command=lambda l=label: self._on_button(l),
        )
        btn.bind("<Enter>", lambda e, b=btn, h=hover: b.config(bg=h))
        btn.bind("<Leave>", lambda e, b=btn, bg_=bg: b.config(bg=bg_))
        return btn

    def _on_button(self, key: str):
        if key == "C":
            self._clear()
        elif key == "⌫":
            self._backspace()
        elif key == "=":
            self._evaluate()
        elif key == "ANS":
            self._insert_ans()
        elif key == "+/-":
            self._toggle_sign()
        elif key == "%":
            self._percent()
        elif key in "0123456789.+-×÷^()":
            self._append(key)
        self._refresh_display()

    def _append(self, char: str):
        internal = internal_expr(char)
        self.expression += internal
        self.sub_display_text = ""

    def _clear(self):
        self.expression = ""
        self.sub_display_text = ""

    def _backspace(self):
        self.expression = self.expression[:-1]
        self.sub_display_text = ""  # clear error/status when editing

    def _insert_ans(self):
        if self.last_ans is not None:
            self.expression += format_result(self.last_ans)
        self.sub_display_text = ""

    def _toggle_sign(self):
        """Toggle sign of the rightmost number in expression."""
        if not self.expression:
            return
        # Find last number (possibly with leading minus)
        m = list(re.finditer(r"(?:^|[\+\-\*\/\%\(])\s*(-?\d+\.?\d*)\s*$", self.expression))
        if not m:
            # Try single number from start
            m2 = re.match(r"^(-?\d+\.?\d*)\s*$", self.expression)
            if m2:
                num = m2.group(1)
                prefix = "-" if num.startswith("-") else ""
                rest = num.lstrip("-")
                self.expression = ("-" if not prefix else "") + rest
            return
        span = m[-1].span(1)
        num_str = m[-1].group(1)
        if num_str.startswith("-"):
            new_num = num_str[1:]
        else:
            new_num = "-" + num_str
        self.expression = self.expression[: span[0]] + new_num + self.expression[span[1] :]
        self.sub_display_text = ""

    def _percent(self):
        """Replace last number with (num/100)."""
        if not self.expression:
            return
        m = list(re.finditer(r"(?:^|[\+\-\*\/\%\(])\s*(-?\d+\.?\d*)\s*$", self.expression))
        if not m:
            m2 = re.match(r"^(-?\d+\.?\d*)\s*$", self.expression)
            if m2:
                try:
                    v = float(m2.group(1)) / 100
                    self.expression = format_result(v)
                except Exception:
                    pass
            return
        span = m[-1].span(1)
        try:
            v = float(m[-1].group(1)) / 100
            self.expression = self.expression[: span[0]] + format_result(v) + self.expression[span[1] :]
        except Exception:
            pass
        self.sub_display_text = ""

    def _evaluate(self):
        if not self.expression.strip():
            self.main_display.config(text="0")
            self.sub_display.config(text="")
            return
        internal = internal_expr(self.expression)
        result, err = safe_eval(internal)
        if err is not None:
            self.sub_display_text = f"Error: {err}"
            self.main_display.config(text="Error")
            self.sub_display.config(text=self.sub_display_text)
            return
        self.last_ans = result
        result_str = format_result(result)
        self.history_list.insert(0, (display_expr(self.expression), result_str))
        self.history_list = self.history_list[:6]
        self._update_history_display()
        self.expression = result_str
        self.sub_display_text = display_expr(internal) + " ="
        self.main_display.config(text=result_str)
        self.sub_display.config(text=self.sub_display_text)

    def _refresh_display(self):
        if self.expression:
            self.main_display.config(text=display_expr(self.expression))
        else:
            self.main_display.config(text="0")
        self.sub_display.config(text=self.sub_display_text)

    def _update_history_display(self):
        lines = []
        for expr, res in self.history_list:
            lines.append(f"{expr} = {res}")
        self.history_label.config(text="\n".join(lines) if lines else "—")

    def _bind_keys(self):
        def on_key(e):
            k = e.keysym
            char = e.char
            if char in "0123456789.+-*/()":
                self._append(internal_expr(char) if char in "*/" else char)
                self._refresh_display()
                return "break"
            if k == "Return" or k == "KP_Enter":
                self._evaluate()
                return "break"
            if k == "BackSpace":
                self._backspace()
                self._refresh_display()
                return "break"
            if k == "Escape":
                self._clear()
                self._refresh_display()
                return "break"
            if char == "^" or (e.state & 0x1 and char == "6"):  # ^ key
                self._append("^")
                self._refresh_display()
                return "break"

        self.root.bind("<Key>", on_key)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = CalculatorApp()
    app.run()
