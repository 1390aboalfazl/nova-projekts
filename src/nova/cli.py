import argparse, sys
from pathlib import Path
from .compiler import run_file, run_source
from .runtime import NovaRuntimeError
from .lexer import LexError
from .parser import ParseError

def main(argv=None):
    ap=argparse.ArgumentParser(prog='nova',description='Nova v0.2 — زبان برنامه‌نویسی کنسولی و دسکتاپ')
    ap.add_argument('file',nargs='?',help='فایل .nova برای اجرا')
    ap.add_argument('--version',action='version',version='Nova 0.2.0')
    ap.add_argument('--check',action='store_true',help='فقط بررسی نحو فایل')
    ap.add_argument('--repl',action='store_true',help='ورود به محیط تعاملی')
    a=ap.parse_args(argv)
    try:
        if a.repl:
            print('Nova 0.2 REPL — برای خروج exit را وارد کنید')
            while True:
                try: line=input('nova> ')
                except EOFError: break
                if line.strip() in ('exit','quit'): break
                try: run_source('forge program "repl" begin\n'+line+'\nend')
                except (LexError,ParseError,NovaRuntimeError) as e: print(f'خطا: {e}',file=sys.stderr)
            return 0
        if not a.file: ap.error('یک فایل بدهید یا از --repl استفاده کنید')
        source=Path(a.file).read_text(encoding='utf-8')
        if a.check: from .parser import parse; parse(source); print('Syntax OK'); return 0
        run_source(source); return 0
    except (OSError,LexError,ParseError,NovaRuntimeError) as e:
        print(f'Nova error: {e}',file=sys.stderr); return 1
if __name__=='__main__': raise SystemExit(main())
