# Nova v0.2

Nova is a custom, console-first programming language. Version 0.2 is implemented as a Python interpreter so that language features can be expanded quickly and predictably. It does **not** target the web and does not use HTML, JavaScript, or a browser. Optional desktop windows use Python's built-in Tkinter where available.

## Requirements
- Python 3.10+
- For desktop GUI: a Python build with Tkinter and a desktop session

## Install from source
```bash
python -m pip install -e .
```

## Run
```bash
nova examples/full_demo.nova
nova --check examples/full_demo.nova
nova --repl
```
If you don't install the package, run from this directory with `PYTHONPATH=src python -m nova examples/full_demo.nova`.

## Syntax at a glance
```nova
forge program "Hello"
begin
    let name: Text = "Nova"
    show "Hello, " + name

    if name == "Nova" begin
        show "Welcome!"
    end else begin
        show "Who are you?"
    end

    for i in 0..3 begin
        show i
    end
end
```

## Language features in v0.2
- Variables (`let`) and constants (`const`), optional primitive type annotations
- `Int`, `Float`, `Bool`, `Text`, and `List` runtime type checks
- Arithmetic, comparison, boolean operators, string concatenation
- `if / else if / else`, `while`, numeric `for ... in start..stop by step`
- Functions, parameters, return values, recursion, lexical scopes
- Classes, instances, fields, methods, `self`, and `new`
- Lists, indexing, mutation, `append`, `remove`, `clear`, `len`
- Console output (`show`) and input (`input`)
- Native desktop GUI basics: `gui_window`, `gui_label`, `gui_button`
- `break`, `continue`, helpful Persian-language error messages

## GUI example
```nova
forge program "Window"
begin
    gui_window("Nova", 500, 300)
    gui_label("Hello desktop")
    gui_button("Click me")
end
```
GUI support is optional and depends on Tkinter/display availability. In this initial GUI layer, buttons are visual controls; event handlers and layout management are planned for a later release.

## Current limitations
This version is an interpreter, not the C code-generating compiler from v0.1. Type checking is primarily runtime for annotated variables and parameters. No web backend exists by design. Advanced generics, inheritance, exceptions, modules, packages, file I/O, a garbage collector for compiled binaries, and GUI event callbacks are not implemented yet.
