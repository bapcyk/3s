#-------------------------------------------------------------------------------
# Name:        lexer.py
#
# Descr:
#
# Author:      5442
#
# Created:     14.05.2022
# Copyright:   (c) 5442 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from __future__ import annotations
import enum
from typing import *
from utils import *


################################################################################
#                                    TokenName
@enum.unique
class TokenName(enum.Enum):
    ATOM = enum.auto()
    STRING = enum.auto()
    COMMA = enum.auto()
    DOT = enum.auto()
    LBR = enum.auto()
    RBR = enum.auto()

    def short(self) -> str:
        return str(self).split('.')[1]


################################################################################
#                                      Token
class Token:
    def __init__(self, name:TokenName, value:str):
        self.name = name
        self.value = value
    def __repr__(self) -> str:
        return f'{self.name.short()} {self.value}'
    def __eq__(self, oth:object) -> bool:
        if isinstance(oth, Token):
            return self.name is oth.name and self.value == oth.value
        else:
            raise NotImplementedError


################################################################################
#                                      State
@enum.unique
class State(enum.Enum):
    NORMAL = enum.auto()
    ESCAPED = enum.auto()
    STRING = enum.auto()


################################################################################
#                                      Error
class Error(Exception):
    pass


################################################################################
#                                      Lexer
class Lexer:
    """Scanner for tokens like a has b, (c has (d has e has f has g, i), \"(x)\"), z.
    """
    _input:str
    _tokens:List[Token]
    _ln:int
    _col:int
    _value:str
    _state:State


    def __init__(self, text:str):
        self._input = text
        self._tokens = []
        self._ln = 1
        self._col = 1
        self._value = ''
        self._state = State.NORMAL


    def _reset_state(self) -> None:
        self._tokens = []
        self._ln = 1
        self._col = 1
        self._value = ''
        self._state = State.NORMAL


    def _reset_token(self) -> None:
        self._value = ''


    def _push_token(self, name:TokenName, value:Optional[str]=None) -> None:
        v = value or self._value
        if v:
            tok = Token(name, value or self._value)
            self._tokens.append(tok)
        self._reset_token()


    def _error(self, msg:str) -> NoReturn:
        raise Error(f'Error {self._ln}:{self._col}: {msg}')


    def _update_pos(self, ch:Char) -> None:
        if ch == '\n':
            self._col = 1
            self._ln += 1
        else:
            self._col += 1


    def run(self) -> Lexer:
        self._reset_state()
        for ch in self._input:
            if self._state is State.NORMAL:
                if ch == '"':
                    self._push_token(TokenName.ATOM)
                    self._state = State.STRING
                elif ch == ',':
                    self._push_token(TokenName.ATOM)
                    self._push_token(TokenName.COMMA, ch)
                elif ch == '.':
                    self._push_token(TokenName.ATOM)
                    self._push_token(TokenName.DOT, ch)
                elif ch == '(':
                    self._push_token(TokenName.ATOM)
                    self._push_token(TokenName.LBR, ch)
                elif ch == ')':
                    self._push_token(TokenName.ATOM)
                    self._push_token(TokenName.RBR, ch)
                elif ch in ' \r\t\n':
                    self._push_token(TokenName.ATOM)
                elif ch == '\\':
                    self._error('Unexpected escape sequence, allowed only in strings')
                else:
                    self._value += ch

            elif self._state is State.STRING:
                if ch == '"':
                    self._push_token(TokenName.STRING)
                    self._state = State.NORMAL
                elif ch == '\\':
                    self._state = State.ESCAPED
                else:
                    self._value += ch

            elif self._state is State.ESCAPED:
                if ch == 't':
                    self._value += '\t'
                elif ch == 'n':
                    self._value += '\n'
                elif ch == 'r':
                    self._value += '\r'
                else:
                    self._value += ch
                self._state = State.STRING

            self._update_pos(ch)

        if self._value:
            self._error(f'Incompleted expression (missing DOT?)')
        return self


    def all_tokens(self) -> List[Token]:
        return self._tokens
