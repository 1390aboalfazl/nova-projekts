# Nova v0.1

Experimental statically typed language compiler written in Python. Current backend emits C11.

## Requirements
- Python 3.10+
- GCC or Clang for native executable builds

## Setup
```bash
python -m pip install -e .
```

## Compile to C / build native executable
```bash
nova compile examples/hello.nova -o build/hello.c
nova build examples/hello.nova -o build/hello
./build/hello
```

## Tests
```bash
python -m unittest discover -s tests -v
```

Supported: `forge program`, `begin`/`end`, immutable `let`, `Int`, `Float`, `Bool`,
`Text`, `show`, arithmetic, static type checking, C11 generation.

Not implemented yet: reassignment, functions, conditionals, loops, garbage collection,
optimization, and WebAssembly backend. The project structure is ready to extend.
