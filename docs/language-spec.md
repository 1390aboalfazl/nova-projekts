# Nova Language Specification — v0.1

A program has the form:

```text
forge program "ProgramName"

begin
    let count: Int = 42
    show count
end
```

Primitive types: `Int` (signed 64-bit), `Float` (double), `Bool`, `Text`.
Statements: `let name: Type = expression` declares an immutable variable; `show expression`
prints one value followed by a newline.

Expressions support literals, variable references, parentheses, unary minus, and numeric
`+`, `-`, `*`, `/`. Integer values can be promoted to Float when initializing a Float.
Duplicate names and unknown names are errors. Integer division returns Float.

Not supported in v0.1: assignment, functions, control flow, modules, automatic memory
management, optimizations, and WebAssembly output.
