from pathlib import Path
from .parser import parse
from .runtime import Interpreter, NovaRuntimeError
from .lexer import LexError
from .parser import ParseError

def run_source(source, output=print, input_fn=input):
    tree=parse(source); Interpreter(output=output,input_fn=input_fn).run(tree)

def run_file(path):
    path=Path(path)
    try: source=path.read_text(encoding='utf-8')
    except OSError as e: raise NovaRuntimeError(f'خواندن فایل ممکن نیست: {e}')
    return run_source(source)

__all__=['parse','run_source','run_file','NovaRuntimeError','LexError','ParseError']
