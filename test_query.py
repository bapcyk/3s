#-------------------------------------------------------------------------------
# Name:        test_query.py
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
import vars
from query import *


################################################################################
#                                   TestMatcher
class TestMatcher(unittest.TestCase):
    @staticmethod
    def v3(s):
        ss = s.split()
        assert len(ss) == 3
        return tuple(vars.Var(term=t) for t in ss)

    @staticmethod
    def vstr(vs):
        return [f'{a} {b} {c}' for _i, (a,b,c) in vs]

    @classmethod
    def setUpClass(cls):
        cls.data = OrderedSet([
            scanner.Tri.simple('alex is 30'),
            scanner.Tri.simple('alex has car'),
            scanner.Tri.simple('car is red'),
            scanner.Tri.simple('john is 40')
        ])

    def test_run1(self):
        res = self.vstr(Matcher(self.data).run(self.v3('alex is 30')))
        self.assertEqual(res, ['alex=alex is=is 30=30'])

    def test_run2(self):
        res = self.vstr(Matcher(self.data).run(self.v3('alex is $age')))
        self.assertEqual(res, ['alex=alex is=is age=30'])

    def test_run3(self):
        res = self.vstr(Matcher(self.data).run(self.v3('alex $pred $obj')))
        self.assertListEqual(res, ['alex=alex pred=is obj=30', 'alex=alex pred=has obj=car'])

    def test_run4(self):
        res = self.vstr(Matcher(self.data).run(self.v3('$subj is $obj')))
        self.assertListEqual(res, ['subj=alex is=is obj=30', 'subj=car is=is obj=red',
            'subj=john is=is obj=40'])

    def test_run5(self):
        res = self.vstr(Matcher(self.data).run(self.v3('$subj was $obj')))
        self.assertListEqual(res, [])

    def test_run6(self):
        res = self.vstr(Matcher(self.data).run(self.v3('$subj is $obj'), no=True))
        self.assertListEqual(res, ['subj=alex has=has obj=car'])

    def test_run7(self):
        res = self.vstr(Matcher(self.data).run(self.v3('$subj was $obj'), no=True))
        self.assertListEqual(res, ['subj=alex is=is obj=30', 'subj=alex has=has obj=car',
            'subj=car is=is obj=red', 'subj=john is=is obj=40'])


################################################################################
#                                   TestMatcher
class TestChapters(unittest.TestCase):
    @staticmethod
    def v3(s):
        ss = s.split()
        assert len(ss) == 3
        return tuple(vars.Var(term=t) for t in ss)


    @classmethod
    def setUpClass(cls):
        cls.data = OrderedSet([
            scanner.Tri.simple('story of s1'),
            scanner.Tri.simple('alex is 30'),
            scanner.Tri.simple('alex has car'),
            scanner.Tri.simple('story of s2'),
            scanner.Tri.simple('car is red'),
            scanner.Tri.simple('john is 40')
        ])

    def test_run1(self):
        ch = Chapters(self.data).mark_by(self.v3('story of $str'), lambda vs: vs[2].name)
        self.assertEqual(2, len(ch.chapters))
        self.assertEqual(repr(ch), '''\
Chapter title s1.
story of s1.
alex is 30.
alex has car.
Chapter title s2.
story of s2.
car is red.
john is 40.''')


################################################################################
#                                   TestQuery
class TestQuery(unittest.TestCase):
    def test_xxx(self):
        pass



if __name__ == '__main__':
    suite = unittest.TestSuite()
    tests = unittest.TestLoader()
    for tc in (TestMatcher, TestQuery, TestChapters):
        suite.addTests(tests.loadTestsFromTestCase(tc))
    runner = unittest.TextTestRunner()
    runner.run(suite)