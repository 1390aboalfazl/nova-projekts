from pathlib import Path
from .parser import parse
from .semantic import check
from .codegen.c_backend import generate

def compile_source(source: str) -> str:
    program = parse(source)
    symbols = check(program)
    return generate(program, symbols)

def compile_file(source_path, output_path):
    source_path, output_path = Path(source_path), Path(output_path)
    generated = compile_source(source_path.read_text(encoding="utf-8"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(generated, encoding="utf-8")
    return output_path
