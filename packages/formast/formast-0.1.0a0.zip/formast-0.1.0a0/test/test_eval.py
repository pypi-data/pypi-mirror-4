"""Test parser with an evaluator-like visitor."""

import nose.tools
import formast

class Evaluator(formast.Visitor):
    def __init__(self):
        formast.Visitor.__init__(self)
        self.stack = []

    def top_class(self, c):
        if c.stats.is_initialized():
            self.stats(c.stats.get())

    def stats_if(self, if_):
        self.expr(if_.expr)
        self.stats(if_.then)
        if if_.else_.is_initialized():
            self.stats(if_.else_.get())

    def expr_uint(self, v):
        self.stack.append(v)

    def expr_add(self, left, right):
        self.expr(left)
        self.expr(right)
        self.stack.append(self.stack.pop() + self.stack.pop())

    def expr_sub(self, left, right):
        self.expr(right)
        self.expr(left) # will pop first!
        self.stack.append(self.stack.pop() - self.stack.pop())

    def expr_mul(self, left, right):
        self.expr(left)
        self.expr(right)
        self.stack.append(self.stack.pop() * self.stack.pop())

    def expr_div(self, left, right):
        self.expr(right)
        self.expr(left) # will pop first!
        self.stack.append(self.stack.pop() // self.stack.pop())

    def expr_neg(self, right):
        self.expr(right)
        self.stack.append(-self.stack.pop())

    def expr_pos(self, right):
        pass

class TestEvaluator:
    def setup(self):
        self.parser = formast.XmlParser()
        self.evaluator = Evaluator()

    def check(self, inp , out):
        top = formast.Top()
        inp = (
            "<niftoolsxml><compound name=\"Test\">"
            "<add type=\"uint\" name=\"test\" cond=\"" + inp + "\" />"
            "</compound></niftoolsxml>"
            )
        self.parser.parse_string(inp, top)
        self.evaluator.top(top)
        nose.tools.assert_equal(len(self.evaluator.stack), 1)
        nose.tools.assert_equal(self.evaluator.stack[0], out)

    def test_uint(self):
        self.check("99", 99)
    
    def test_add(self):
        self.check("1+2", 3)

    def test_complicated(self):
        self.check("1+(2*3+4)*6/(3-4)", -59)
