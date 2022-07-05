#-------------------------------------------------------------------------------
# Name:        test_scanner.py
#
# Descr:       Tests
#
# Author:      5442
#
# Created:     14.05.2022
# Copyright:   (c) 5442 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from scanner import *
import unittest
from utils import *


################################################################################
#                            TestContext
class TestContext(unittest.TestCase):
    def test_fact(self):
        ctx = Context().another_subj('alex')
        self.assertEqual(['alex.'], ctx.descr())

    def test_pred(self):
        ctx = Context().another_subj('alex').set_pred('has')
        self.assertEqual(['alex has.'], ctx.descr())

    def test_obj(self):
        ctx = Context().another_subj('alex').set_pred('has') \
            .set_obj('car')
        self.assertEqual(['alex has car.'], ctx.descr())

    def test_another_subj1(self):
        ctx = Context().another_subj('alex').set_pred('has') \
            .set_obj('car').another_subj('john')
        self.assertEqual(['alex has car.', 'john.'], ctx.descr())

    def test_another_subj2(self):
        ctx = Context().another_subj('alex', 'has', 'car') \
            .another_subj('john').set_pred('age').set_obj('20')
        self.assertEqual(['alex has car.', 'john age 20.'], ctx.descr())

    def test_another_pred(self):
        ctx = Context().another_subj('alex').set_pred('has') \
            .set_obj('car').another_pred('age', '30')
        self.assertEqual(['alex has car.', 'alex age 30.'], ctx.descr())

    def test_another_obj(self):
        ctx = Context().another_subj('alex').set_pred('has') \
            .set_obj('car').another_obj('cat')
        self.assertEqual(['alex has car.', 'alex has cat.'], ctx.descr())

    def test_which_pred(self):
        ctx = Context().another_subj('alex').set_pred('has') \
            .set_obj('car').which_pred('is', 'big')
        self.assertEqual(['alex has car.', 'car is big.'], ctx.descr())

    def test_complex(self):
        ctx = Context().another_subj('alex').set_pred('has') \
            .set_obj('car').which_pred('is', 'big') \
            .another_pred('color').set_obj('red') \
            .another_obj('metallic')
        self.assertEqual(['alex has car.', 'car is big.', 'car color red.',
            'car color metallic.'], ctx.descr())


################################################################################
#                                   TestTri
class TestTri(unittest.TestCase):
    def test_fact(self):
        s = repr(Tri('alex'))
        self.assertEqual('alex.', s)

    def test_improper_tri(self):
        s = repr(Tri('alex', 'age'))
        self.assertEqual('alex age.', s)

    def test_tri(self):
        s = repr(Tri('alex', 'age', '30'))
        self.assertEqual('alex age 30.', s)


################################################################################
#                                   TestAst
class TestAst(unittest.TestCase):
    def test_ast(self):
        ast = Ast([Tri('me', 'age', '100'), Tri('alex', 'age', '30')])
        s = repr(ast)
        self.assertEqual('me age 100.\nalex age 30.', s)


################################################################################
#                            TestScanner
class TestScanner(unittest.TestCase):
    def test_single(self):
        d = Scanner('a has b.').run()._ctx.descr()
        self.assertEqual(['a has b.'], d)

    def test_multiple_obj(self):
        d = Scanner('a has b, c, d.').run()._ctx.descr()
        self.assertEqual(['a has b.', 'a has c.', 'a has d.'], d)

    def test_multiple_pred(self):
        d = Scanner('a has1 b, has2 c, has3 d.').run()._ctx.descr()
        self.assertEqual(['a has1 b.', 'a has2 c.', 'a has3 d.'], d)

    def test_transitive1(self):
        d = Scanner('a has1 b has2 c has3 d.').run()._ctx.descr()
        self.assertEqual(['a has1 b.', 'b has2 c.', 'c has3 d.'], d)

    def test_complex1(self):
        d = Scanner('a has1 b has2 c, d.').run()._ctx.descr()
        self.assertEqual(['a has1 b.', 'b has2 c.', 'b has2 d.'], d)

    def test_complex2(self):
        d = Scanner('a has1 b, has2 c has3 d.').run()._ctx.descr()
        self.assertEqual(['a has1 b.', 'a has2 c.', 'c has3 d.'], d)

    def test_complex3(self):
        d = Scanner('c age 30, has d has e has f has g, i.').run()._ctx.descr()
        self.assertEqual(['c age 30.', 'c has d.', 'd has e.', 'e has f.', 'f has g.',
            'f has i.'], d)

    def test_complex4(self):
        d = Scanner('a has z, b, has c.').run()._ctx.descr()
        self.assertEqual(['a has z.', 'a has b.', 'a has c.'], d)

    def _test_complex5(self):
        d = Scanner('c has x, d age 30.').run()._ctx.descr()
        self.assertEqual(['c has x.', 'c has d.', 'd age 30.'], d)

    def test_complex6(self):
        d = Scanner('a has z, b, has c has x.').run()._ctx.descr()
        self.assertEqual(['a has z.', 'a has b.', 'a has c.', 'c has x.'], d)

    def test_complex7(self):
        d = Scanner('any with age > 50, < 30.').run()._ctx.descr()
        self.assertEqual(['any with age.', 'age > 50.', 'age < 30.'], d)



if __name__ == '__main__':
    suite = unittest.TestSuite()
    tests = unittest.TestLoader()
    for tc in (TestContext, TestTri, TestAst, TestScanner):
        suite.addTests(tests.loadTestsFromTestCase(tc))
    runner = unittest.TextTestRunner()
    runner.run(suite)