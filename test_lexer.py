#-------------------------------------------------------------------------------
# Name:        test_lexer.py
#
# Descr:       Tests
#
# Author:      5442
#
# Created:     14.05.2022
# Copyright:   (c) 5442 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from lexer import *
import unittest


class Test(unittest.TestCase):
    def test_single(self):
        res = Lexer('abc.').run().all_tokens()
        self.assertEqual(res, [
            Token(TokenName.ATOM, 'abc'),
            Token(TokenName.DOT, '.')])

    def test_str(self):
        res = Lexer('"abc".').run().all_tokens()
        self.assertEqual(res, [
            Token(TokenName.STRING, 'abc'),
            Token(TokenName.DOT, '.')])

    def test_str_with_esc(self):
        res = Lexer(r'"abc\r\"".').run().all_tokens()
        self.assertEqual(res, [
            Token(TokenName.STRING, 'abc\r"'),
            Token(TokenName.DOT, '.')])

    def test_multiline(self):
        res = Lexer('"abc"  \n .').run().all_tokens()
        self.assertEqual(res, [
            Token(TokenName.STRING, 'abc'),
            Token(TokenName.DOT, '.')])

    def test_with_brackets(self):
        res = Lexer(r'a has b, (c has (d has e has f has g, i), "(x\")"), z.') \
            .run().all_tokens()
        self.assertEqual(res, [
            Token(TokenName.ATOM, 'a'),
            Token(TokenName.ATOM, 'has'),
            Token(TokenName.ATOM, 'b'),
            Token(TokenName.COMMA, ','),
            Token(TokenName.LBR, '('),
            Token(TokenName.ATOM, 'c'),
            Token(TokenName.ATOM, 'has'),
            Token(TokenName.LBR, '('),
            Token(TokenName.ATOM, 'd'),
            Token(TokenName.ATOM, 'has'),
            Token(TokenName.ATOM, 'e'),
            Token(TokenName.ATOM, 'has'),
            Token(TokenName.ATOM, 'f'),
            Token(TokenName.ATOM, 'has'),
            Token(TokenName.ATOM, 'g'),
            Token(TokenName.COMMA, ','),
            Token(TokenName.ATOM, 'i'),
            Token(TokenName.RBR, ')'),
            Token(TokenName.COMMA, ','),
            Token(TokenName.STRING, '(x")'),
            Token(TokenName.RBR, ')'),
            Token(TokenName.COMMA, ','),
            Token(TokenName.ATOM, 'z'),
            Token(TokenName.DOT, '.')])

    def test_error(self):
        it = lambda: Lexer('"abc"  \n \n \\').run().all_tokens()
        self.assertRaisesRegex(Error, "Error 3:2: Unexpected escape sequence, allowed only in strings", it)


if __name__ == '__main__':
    unittest.main()