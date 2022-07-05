#-------------------------------------------------------------------------------
# Name:        scanner.py
#
# Descr:
#
# Author:      5442
#
# Created:     14.05.2022
# Copyright:   (c) 5442 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# Examples:
#
# house.
#
# man name Ivan, age 30, hobbies dance, boxing.
#
#   man
#    +--name--Ivan
#    +--age--30
#    +--hobbies--+--dance
#                `--boxing
#
# man has business, wife, is old, owns car, house.
#
#   man--has--+--business
#    |        `--wife
#    +--is--old
#    `--owns--+--car
#             `--house
#
# Ivan friends Oleg, Alex.
#
#   Ivan--friends--+--Oleg
#                  `--Alex
#
# a has b, has c has d has e has f has g, i.
# a has b, has c has d has e has f has g, has i.   <-- or this?
# c has x. a has z.
#
# a has z, b, has c has x, d has e has f has g, has i.
# a has z, b, c has x, d has e has f has g, i.
#
#  a--has--z
#       +--b
#       `--c--has--x
#               `--d--has--e--has--f--has--g
#                                       `--i
#
#  a
#  +--has--b
#  +--has--c--has--d--has--e--has--f--has--g
#  |       |                       `--has--j
#  |       `--has--x
#  `--has--z

from __future__ import annotations
import enum
from typing import *
import lexer
from utils import *


################################################################################
#                                      State
@enum.unique
class State(enum.Enum):
    SUBJ = enum.auto()  # wait for a subj
    PRED = enum.auto()  # wait for a pred
    OBJ = enum.auto()  # wait for an obj
    AFTER_OBJ = enum.auto()  # wait for after obj
    AFTER_COMMA = enum.auto()  # wait for after comma

    def short(self) -> str:
        return str(self).split('.')[1]


################################################################################
#                                      Term
class Term(str):
    pass


################################################################################
#                                      Tri
class Tri:
    subj: Term
    pred: Optional[Term]
    obj: Optional[Term]

    def __init__(self,
            subj:Term, pred:Optional[Term]=None, obj:Optional[Term]=None) -> None:
        self.subj = subj
        self.pred = pred
        self.obj = obj


    @staticmethod
    def simple(s:str) -> Tri:
        args = (Term(p) for p in s.split())
        return Tri(*args)


    def terms(self) -> List[Optional[Term]]:
        return [self.subj, self.pred, self.obj]


    def replace(self,
            subj:Optional[Term]=None,
            pred:Optional[Term]=None,
            obj:Optional[Term]=None) -> Tri:
        tri = Tri(
            self.subj if subj is None else subj,
            self.pred if pred is None else pred,
            self.obj if obj is None else obj)
        return tri

    def __repr__(self) -> str:
        s = str(self.subj)
        if self.pred: s += f' {self.pred}'
        if self.obj: s += f' {self.obj}'
        s += '.'
        return s

    def __eq__(self, oth: object) -> bool:
        if isinstance(oth, Tri):
            return (
                self.subj == oth.subj
                and self.pred == oth.pred
                and self.obj == oth.obj)
        else:
            raise NotImplementedError

    def __hash__(self) -> int:
        return hash((self.subj, self.pred, self.obj))


################################################################################
#                                      Ast
class Ast:
    __items: OrderedSet[Tri]

    @property
    def items(self) -> OrderedSet[Tri]:
        return self.__items

    def __init__(self, items:Optional[List[Tri]]=None) -> None:
        self.__items = OrderedSet(items)

    def __repr__(self) -> str:
        return '\n'.join(repr(t) for t in self.__items)

    def add_tri(self, tri:Tri) -> Ast:
        self.__items.add(tri)
        return self

    def clear(self) -> Ast:
        self.__items.clear()
        return self


################################################################################
#                                      Error
class Error(Exception):
    pass


################################################################################
#                                     Context
class Context:
    "Scanning context"
    _ast: Ast
    _tri: Optional[Tri]

    def __init__(self) -> None:
        self._ast = Ast()
        self._tri = None

    def clear(self) -> Context:
        self._ast.clear()
        self._tri = None
        return self

    @property
    def subj(self) -> Optional[Term]:
        return self._tri.subj if self._tri else None

    @property
    def pred(self) -> Optional[Term]:
        return self._tri.pred if self._tri else None

    @property
    def obj(self) -> Optional[Term]:
        return self._tri.obj if self._tri else None

    def descr(self) -> List[str]:
        return [repr(s) for s in self._ast.items]

    def another_subj(self, subj:Term, pred:Optional[Term]=None,
            obj:Optional[Term]=None) -> Context:
        "SUBJ"
        self._tri = Tri(subj, pred, obj)
        self._ast.add_tri(self._tri)
        return self

    def set_pred(self, pred:Term) -> Context:
        "_ PRED"
        assert self._tri
        self._tri.pred = pred
        return self

    def set_obj(self, obj:Term) -> Context:
        "_ _ OBJ"
        assert self._tri
        self._tri.obj = obj
        return self

    def another_pred(self, pred:Term, obj:Optional[Term]=None) -> Context:
        "_ _ _, PRED [OBJ]"
        assert self._tri
        self._tri = self._tri.replace(pred=pred, obj=obj)
        self._ast.add_tri(self._tri)
        return self

    def another_obj(self, obj:Term) -> Context:
        "_ _ _, OBJ"
        assert self._tri
        self._tri = self._tri.replace(obj=obj)
        self._ast.add_tri(self._tri)
        return self

    def which_pred(self, pred:Term, obj:Optional[Term]=None) -> Context:
        "_ _ _ PRED [OBJ]"
        assert self._tri
        assert self._tri.obj
        self._tri = Tri(self._tri.obj, pred, obj)
        self._ast.add_tri(self._tri)
        return self


################################################################################
#                                     Scanner
class Scanner:
    _input: str
    _state: State
    _lexer: lexer.Lexer
    _ctx: Context


    def __init__(self, text:str):
        self._input = text
        self._lexer = lexer.Lexer(text)
        self._ctx = Context()
        self._reset_state()


    def _reset_state(self) -> None:
        self._state = State.SUBJ
        self._ctx.clear()


    def _error(self, itok:int, msg:str) -> NoReturn:
        raise Error(f'In {self._state.short()}, {itok}th token at {self._lexer._ln}:{self._lexer._col}: {msg}')


    @staticmethod
    def term(*args) -> Term:
        if len(args) == 1:
            token = args[0]
            assert token is not None
            return Term(token.value)
        elif len(args) == 2:
            tokens, i = args
            assert i < len(tokens)
            return Term(tokens[i].value)
        else:
            raise ValueError('Invalid arguments, must be term(token:Token) | term(tokens:List[Token], i:int)')


    def _after_comma_ended(self, itok:int, tokens:List[lexer.Token], after_comma:int) -> bool:
        """Updates context for the state after the comma when it reached another
        comma or a dot
        """
        itok_after_comma: int
        if after_comma == 0:
            return False
        else:
            itok_after_comma = itok - after_comma
            if after_comma % 2 == 1:
                self._ctx.another_obj(self.term(tokens, itok_after_comma))
                i = itok_after_comma + 1
            else:
                i = itok_after_comma
            j = 0
            while i < itok:
                if j == 0:
                    self._ctx.another_pred(
                        self.term(tokens, i), self.term(tokens, i + 1))
                else:
                    self._ctx.which_pred(
                        self.term(tokens, i), self.term(tokens, i + 1))
                i += 2
                j += 1
            return True


    def run(self) -> Scanner:
        self._reset_state()
        self._lexer.run()
        tokens:List[lexer.Token] = self._lexer.all_tokens()
        itok = 0
        after_comma = 0

        while itok < len(tokens):
            tok = tokens[itok]

            if self._state == State.SUBJ:
                if tok.name in (lexer.TokenName.ATOM, lexer.TokenName.STRING):
                    self._ctx.another_subj(self.term(tok))
                    self._state = State.PRED
                else:
                    self._error(itok,
                        f'Unexpected token {tok}, expected ATOM/STRING/DOT')

            elif self._state == State.PRED:
                if tok.name in (lexer.TokenName.ATOM, lexer.TokenName.STRING):
                    self._ctx.set_pred(self.term(tok))
                    self._state = State.OBJ
                elif tok.name == lexer.TokenName.DOT:
                    self._state = State.SUBJ
                else:
                    self._error(itok,
                        f'Unexpected token {tok}, expected ATOM/STRING')

            elif self._state == State.OBJ:
                if tok.name in (lexer.TokenName.ATOM, lexer.TokenName.STRING):
                    self._ctx.set_obj(self.term(tok))
                    self._state = State.AFTER_OBJ
                else:
                    self._error(itok,
                        f'Unexpected token {tok}, expected ATOM/STRING')

            elif self._state == State.AFTER_OBJ:
                if tok.name == lexer.TokenName.DOT:
                    self._state = State.SUBJ
                elif tok.name == lexer.TokenName.COMMA:
                    self._state = State.AFTER_COMMA
                elif tok.name in (lexer.TokenName.ATOM, lexer.TokenName.STRING):
                    self._ctx.which_pred(self.term(tok))
                    self._state = State.OBJ
                else:
                    self._error(itok,
                        f'Unexpected token {tok}, expected DOT/COMMA/ATOM/STRING')

            elif self._state == State.AFTER_COMMA:
                if tok.name in (lexer.TokenName.ATOM, lexer.TokenName.STRING):
                    after_comma += 1
                elif tok.name == lexer.TokenName.DOT:
                    self._after_comma_ended(itok, tokens, after_comma)
                    after_comma = 0
                    self._state = State.SUBJ
                elif tok.name == lexer.TokenName.COMMA:
                    self._after_comma_ended(itok, tokens, after_comma)
                    after_comma = 0
                else:
                    self._error(itok,
                        f'Unexpected token {tok}, expected ATOM/STRING/DOT/COMMA')

            itok += 1

        return self


################################################################################
#                                   term()
