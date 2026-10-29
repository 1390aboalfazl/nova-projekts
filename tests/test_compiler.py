import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from nova.compiler import compile_source
from nova.errors import NovaSyntaxError, NovaTypeError

VALID = '''forge program "Test"
begin
    let count: Int = 2
    let price: Float = 3.5
    let active: Bool = true
    let title: Text = "ok"
    show count + 3
    show price * 2.0
    show active
    show title
end
'''

class CompilerTests(unittest.TestCase):
    def test_generates_c(self):
        c = compile_source(VALID)
        self.assertIn("int main(void)", c)
        self.assertIn("printf", c)
        self.assertIn("const int64_t count", c)

    def test_unknown_variable_fails(self):
        with self.assertRaises(NovaTypeError):
            compile_source('forge program "Bad"\nbegin\n show missing\nend\n')

    def test_type_mismatch_fails(self):
        with self.assertRaises(NovaTypeError):
            compile_source('forge program "Bad"\nbegin\n let x: Int = "text"\nend\n')

    def test_missing_end_fails(self):
        with self.assertRaises(NovaSyntaxError):
            compile_source('forge program "Bad"\nbegin\n show 1\n')

    @unittest.skipUnless(shutil.which("cc") or shutil.which("gcc") or shutil.which("clang"),
                         "C compiler not installed")
    def test_native_program(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfile, exe = Path(tmp) / "test.c", Path(tmp) / "test"
            cfile.write_text(compile_source(VALID), encoding="utf-8")
            cc = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
            subprocess.run([cc, "-std=c11", str(cfile), "-o", str(exe)], check=True)
            output = subprocess.check_output([str(exe)], text=True)
            self.assertEqual(output.splitlines(), ["5", "7", "true", "ok"])

if __name__ == "__main__":
    unittest.main()
