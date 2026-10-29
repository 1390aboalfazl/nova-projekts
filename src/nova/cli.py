import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from .compiler import compile_file
from .errors import NovaError

def main(argv=None):
    parser = argparse.ArgumentParser(prog="nova", description="Nova v0.1 compiler")
    subs = parser.add_subparsers(dest="command", required=True)
    c = subs.add_parser("compile", help="compile Nova source to C")
    c.add_argument("source")
    c.add_argument("-o", "--output", required=True)
    b = subs.add_parser("build", help="compile and build native executable")
    b.add_argument("source")
    b.add_argument("-o", "--output", required=True)
    b.add_argument("--cc", default=None)
    args = parser.parse_args(argv)
    try:
        if args.command == "compile":
            result = compile_file(args.source, args.output)
            print(f"Nova: generated {result}")
            return 0
        cc = args.cc or shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
        if not cc:
            print("Nova error: install GCC or Clang first", file=sys.stderr)
            return 2
        output = Path(args.output)
        cfile = output.with_name(output.stem + ".generated.c")
        compile_file(args.source, cfile)
        output.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run([cc, "-std=c11", "-Wall", "-Wextra", str(cfile), "-o", str(output)])
        if result.returncode:
            return result.returncode
        print(f"Nova: built {output}")
        return 0
    except (NovaError, OSError) as exc:
        print(f"Nova error: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
