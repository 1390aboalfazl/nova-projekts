import unittest
from nova.compiler import run_source
from nova.parser import parse
from nova.runtime import NovaRuntimeError

class NovaV02Tests(unittest.TestCase):
    def execute(self, body):
        output=[]
        run_source('forge program "test" begin\n'+body+'\nend', output=output.append, input_fn=lambda _: 'Test')
        return output
    def test_math_and_loop(self):
        self.assertEqual(self.execute('let total: Int = 0\nfor i in 1..5 begin\n total += i\nend\nshow total'), ['10'])
    def test_if_else(self):
        self.assertEqual(self.execute('let x = 7\nif x > 5 begin\n show "yes"\nend else begin\n show "no"\nend'), ['yes'])
    def test_function_recursion(self):
        src='function fact(n: Int) -> Int begin\n if n <= 1 begin\n return 1\n end\n return n * fact(n-1)\nend\nshow fact(5)'
        self.assertEqual(self.execute(src), ['120'])
    def test_list_and_index(self):
        self.assertEqual(self.execute('let xs = [2, 4]\nappend(xs, 6)\nshow xs[2]\nshow len(xs)'), ['6','3'])
    def test_class_method(self):
        src='class Person begin\n function init(name: Text) begin\n self.name = name\n end\n function greet() begin\n return "Hi " + self.name\n end\nend\nlet p = new Person("Ada")\nshow p.greet()'
        self.assertEqual(self.execute(src), ['Hi Ada'])
    def test_type_error(self):
        with self.assertRaises(NovaRuntimeError): self.execute('let x: Int = "wrong"')
    def test_const(self):
        with self.assertRaises(NovaRuntimeError): self.execute('const x = 1\nx = 2')

if __name__=='__main__': unittest.main()
