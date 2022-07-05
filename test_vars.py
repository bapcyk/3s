#-------------------------------------------------------------------------------
# Name:        test_vars.py
#
# Descr:
#
# Author:      5442
#
# Created:     28.05.2022
# Copyright:   (c) 5442 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import unittest
import scanner
from vars import *


################################################################################
#                                   TestAst
class TestVar(unittest.TestCase):
    def test_fact(self):
        v = Var(term=scanner.Term('alex'))
        self.assertTrue(v.unified)
        self.assertEqual(v.name, 'alex')
        self.assertEqual(v.value, 'alex')

    def test_explicit_var(self):
        v = Var(name='alex')
        self.assertFalse(v.unified)
        self.assertEqual(v.name, 'alex')
        self.assertIsNone(v.value)

    def test_var(self):
        v = Var(term=scanner.Term('$alex'))
        self.assertFalse(v.unified)
        self.assertEqual(v.name, 'alex')
        self.assertIsNone(v.value)

    def test_set(self):
        v = Var(name='man')
        v._value = 'alex'
        self.assertTrue(v.unified)
        self.assertEqual(v.name, 'man')
        self.assertEqual(v.value, 'alex')


################################################################################
#                                   TestAst
class TestVars(unittest.TestCase):
    def test_add(self):
        vs = Vars()
        vs.add('name').add('age')
        self.assertEqual(vs.names, {'name', 'age'})

    def test_get1(self):
        vs = Vars()
        vs.add('name')
        self.assertEqual(vs.get('name').name, 'name')
        self.assertFalse(vs.get('name').unified)

    def test_get2(self):
        vs = Vars()
        vs.add('name')
        self.assertEqual(vs['name'].name, 'name')
        self.assertFalse(vs['name'].unified)

    def test_unify1(self):
        vs = Vars()
        vs.add('name').add('alex')
        vs['name']._value = 'alex'
        res = vs.unify('name', 'alex')
        self.assertEqual(vs['alex'].value, 'alex')
        self.assertTrue(res)

    def test_unify2(self):
        vs = Vars()
        vs.add('name').add('alex')
        vs['name']._value = 'alex'
        res = vs.unify('alex', 'name')
        self.assertEqual(vs['alex'].value, 'alex')
        self.assertTrue(res)

    def test_unify3(self):
        vs = Vars()
        vs.add('name1').add('name2')
        vs['name1']._value = 'alex'
        vs['name2']._value = 'john'
        res = vs.unify('name1', 'name2')
        self.assertFalse(res)

    def test_unify4(self):
        vs = Vars()
        vs.add('name1').add('name2')
        vs['name1']._value = 'alex'
        vs['name2']._value = 'alex'
        res = vs.unify('name1', 'name2')
        self.assertTrue(res)

    def test_unify5(self):
        vs = Vars()
        vs.add('name1').add('name2')
        res = vs.unify('name1', 'name2')
        self.assertTrue(res)
        self.assertEqual(vs.synonyms('name1'), {'name2'})
        self.assertEqual(vs.synonyms('name2'), {'name1'})

    def test_unify6(self):
        vs = Vars()
        vs.add('name1').add('name2').add('alex')
        vs['alex']._value = 'alex'
        res = vs.unify('name1', 'name2')
        self.assertTrue(res)
        res = vs.unify('name2', 'alex')
        self.assertTrue(res)
        self.assertEqual(vs['name1'].value, 'alex')
        self.assertEqual(vs['name2'].value, 'alex')
        self.assertEqual(vs['alex'].value, 'alex')


if __name__ == '__main__':
    suite = unittest.TestSuite()
    tests = unittest.TestLoader()
    for tc in (TestVar, TestVars):
        suite.addTests(tests.loadTestsFromTestCase(tc))
    runner = unittest.TextTestRunner()
    runner.run(suite)