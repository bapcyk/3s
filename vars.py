#-------------------------------------------------------------------------------
# Name:        vars.py
#
# Descr:
#
# Author:      5442
#
# Created:     28.05.2022
# Copyright:   (c) 5442 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from __future__ import annotations
from typing import *
import enum
import scanner


################################################################################
#                                    Unified
@enum.unique
class Unified(enum.Enum):
    FIRST = enum.auto()   # 1st got a value from the 2nd
    SECOND = enum.auto()  # 2nd got a value from the 1st
    NONE = enum.auto()    # both are without values so no one got a value
    EQUAL = enum.auto()   # both are with values and are equal
    UNEQUAL = enum.auto() # both are with values and are unequal

    def __bool__(self) -> bool:
        return self in (Unified.FIRST, Unified.SECOND, Unified.NONE, Unified.EQUAL)


################################################################################
#                                      Var
class Var:
    PREFIX = '$'
    _name: scanner.Term
    _value: Optional[scanner.Term]
    _initial_value: Optional[scanner.Term]

    @property
    def name(self) -> scanner.Term:
        return self._name


    @property
    def value(self) -> Optional[scanner.Term]:
        return self._value


    @value.setter
    def value(self, v:scanner.Term) -> None:
        self._value = v


    def __eq__(self, oth:object) -> bool:
        if isinstance(oth, Var):
            return self._name == oth._name and self._value == oth._value
        else:
            raise NotImplementedError


    def __hash__(self) -> int:
        return hash((self._name, self._value))


    def __repr__(self) -> str:
        return f'{self._name}={self._value}'


    @classmethod
    def is_var(cls, term:scanner.Term) -> bool:
        return str(term).startswith(cls.PREFIX)


    @classmethod
    def try_name(cls, term:scanner.Term) -> Optional[str]:
        """Try to extract a name from a term that must look like <PREFIX>something"""
        if cls.is_var(term):
            return str(term)[1:]
        else:
            return None


    def __init__(self, *, name:Optional[str]=None, term:Optional[scanner.Term]=None) -> None:
        if name is not None:
            self._name = scanner.Term(name)
            self._value = None
        elif term is not None:
            if (name := self.try_name(term)):
                self._name = scanner.Term(name)
                self._value = None
            else:
                self._name = term
                self._value = term
        else:
            raise ValueError('either name or term arg is mandatory')
        self._initial_value = self._value


    @property
    def is_const(self):
        return self._value == self._name


    def reinit(self) -> None:
        self._value = self._initial_value


    def copy(self) -> Var:
        v = Var(name=self.name)
        v._value = self.value
        return v


    @property
    def unified(self) -> bool:
        return self._value is not None


    def unify(self, oth:Var) -> Unified:
        if (not self.unified) and oth.unified:
            self._value = oth.value
            return Unified.FIRST  # 1st = itself
        elif self.unified and (not oth.unified):
            oth._value = self.value
            return Unified.SECOND
        elif self.unified and oth.unified:
            return Unified.EQUAL if self._value == oth.value else Unified.UNEQUAL
        elif (not self.unified) and (not oth.unified):
            return Unified.NONE
        else:
            raise RuntimeError('Unhandled Unified enum value')


################################################################################
#                                    Vars
class Vars:
    _items: Dict[scanner.Term, Var]
    _synonyms: Dict[scanner.Term, List[Var]]


    def __init__(self) -> None:
        self._items = {}
        self._synonyms = {}


    @property
    def names(self) -> Set[str]:
        return {str(k) for k in self._items}


    def add(self, name:str) -> Vars:
        self._items[scanner.Term(name)] = Var(name=name)
        return self


    def tryadd(self, term:scanner.Term) -> Vars:
        """Like add() but adds a term and only if it looks as a variable, ie.
        started with `Var.PREFIX`
        """
        if (name := Var.try_name(term)):
            self.add(name)
        return self


    def synonyms(self, name:str) -> Set[str]:
        return {str(v.name) for v in self._synonyms.get(scanner.Term(name), [])}


    def get(self, name:str) -> Optional[Var]:
        return self._items.get(scanner.Term(name))


    def __getitem__(self, name:str) -> Var:
        res = self.get(name)
        if res is None:
            raise KeyError(f'no such var {name}')
        else:
            return res


    def unify(self, name1:str, name2:str) -> bool:
        v1 = self.get(name1)
        v2 = self.get(name2)
        if v1 is None:
            raise ValueError(f'No 1st var named {name1}')
        if v2 is None:
            raise ValueError(f'No 2st var named {name1}')

        res = v1.unify(v2)
        if res == Unified.FIRST:
            for v in self._synonyms.get(v1.name, []):
                v.value = v2.value
        elif res == Unified.SECOND:
            for v in self._synonyms.get(v2.name, []):
                v.value = v1.value
        elif res == Unified.EQUAL:
            pass
        elif res == Unified.UNEQUAL:
            pass
        elif res == Unified.NONE:
            self._synonyms.setdefault(v1.name, []).append(v2)
            self._synonyms.setdefault(v2.name, []).append(v1)
        return bool(res)

