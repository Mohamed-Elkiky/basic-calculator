# Basic Calculator (Python + Tkinter)

A clean, dark-themed desktop calculator built with **Python + Tkinter**, featuring **safe expression evaluation (no `eval`)**, keyboard controls, and a small calculation history.

## Features
- Dark UI with hoverable buttons and clear visual grouping (numbers / operators / actions)
- Safe math evaluation via Python `ast` (no `eval()`)
- Supports:
  - `+  -  *  /  %`
  - Parentheses `( )`
  - Power `^` (stored internally as `**`)
- Utilities:
  - Clear (`C`) and Backspace (`⌫`)
  - `+/-` toggles sign of the most recent number
  - `%` converts the last number into a percentage (`/100`)
  - `ANS` inserts the last answer
- Keyboard support:
  - Digits `0–9`
  - Operators `+ - * /`
  - Parentheses `( )`
  - Decimal `.`
  - `Enter` evaluates
  - `Backspace` deletes
  - `Esc` clears
  - `^` power

## Requirements
- Python 3.x
- Tkinter (usually bundled with Python; no pip installs required)

## Run
```bash
python main.py