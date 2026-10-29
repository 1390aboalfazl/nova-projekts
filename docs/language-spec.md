# Nova v0.2 — language reference

## Program structure
A source file starts with `forge program "optional title" begin` and ends with `end`.

## Declarations
`let age: Int = 18`; `const appName: Text = "Nova"`. Types are optional. Supported annotations: `Int`, `Float`, `Bool`, `Text`, `List`.

## Statements
- `show expression`
- `if condition begin ... end else begin ... end`
- `while condition begin ... end`
- `for item in start..stop begin ... end`; stop is exclusive. Optional `by step` controls step size.
- `function name(param: Type) -> ReturnType begin ... end`
- `return expression`, `break`, `continue`
- `class Name begin ... end`; methods are functions; use `self.field` and `new Name(args)`.

## Expressions
Numbers, quoted strings, `true`, `false`, `null`, lists, calls, property access, indexing, unary `-` and `not`; arithmetic `+ - * / %`; comparisons `== != < <= > >=`; boolean `and`, `or`; membership `in`.

## Built-ins
`input(prompt)`, `len(value)`, `str(value)`, `int(value)`, `float(value)`, `abs(value)`, `sqrt(value)`, `round(value)`, `range(stop)` / `range(start, stop)`, `append(list, value)`, `remove(list, value)`, `clear(list)`.

## Desktop GUI
`gui_window(title, width, height)`, `gui_label(text)`, `gui_button(text)`. Requires Tkinter. Buttons currently do not invoke Nova callbacks.
