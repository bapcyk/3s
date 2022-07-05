#-------------------------------------------------------------------------------
# Name:        query.py
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
from dataclasses import dataclass
from typing import *
import scanner
import dataset
import vars
from utils import *


################################################################################
#                                    Matcher
class Matcher(dataset.Dataset):
    def __init__(self, data:OrderedSet[scanner.Tri]) -> None:
        super().__init__(data)


    def run(self, crit: Tuple[vars.Var, vars.Var, vars.Var], *, no:bool=False) \
            -> Iterator[Tuple[vars.Var, vars.Var, vars.Var]]:
        """`no` is to inverse the search. vars can be either already unified or not
        """
        val0, val1, val2 = (v.value for v in crit)
        for i, tri in enumerate(self.linear_iterator()):
            ts = tuple(vars.Var(term=t) for t in tri.terms())
            crit1 = tuple(c.copy() for c in crit)  # FIXME optimize without to copy
            # list is required to evaluate all vars unification, BCS any()/all()
            # works only until the 1st failing item
            unify_res = [c.unify(t) for c,t in zip(crit1, ts)]
            if no:
                if any(not r for r in unify_res):
                    yield i, tuple(t if c.is_const else c for c,t in zip(crit1, ts))
            else:
                if all(unify_res):
                    yield i, crit1


################################################################################
#                                 NumeratedChapter
@dataclass
class NumeratedChapter:
    name: str
    data: List[Tuple[int, scanner.Tri]]

    def __repr__(self) -> str:
        title = self.name
        if ' ' in self.name: title = '"' + title + '"'
        title = f'Chapter title {title}.'
        return '\n'.join([title] + [repr(d[1]) for d in self.data])


################################################################################
#                                     Chapters
class Chapters(dataset.Dataset):
    _chapters: List[NumeratedChapter]


    def __init__(self, data:OrderedSet[scanner.Tri]) -> None:
        super().__init__(data)
        self._chapters = []


    def __repr__(self) -> str:
        return '\n'.join(repr(nc) for nc in self._chapters)


    @property
    def chapters(self) -> List[NumeratedChapter]:
        return self._chapters


    def mark_by(self, crit: Tuple[vars.Var, vars.Var, vars.Var],
            name: Callable[[Tuple[vars.Var, vars.Var, vars.Var]], str]) -> Chapters:
        "Marks all chapters"
        self._chapters = []
        chap: List[Tuple[int, scanner.Tri]] = []
        chapname: str = 'Unnamed'
        ts: Optional[Tuple[vars.Var, vars.Var, vars.Var]] = None
        for i, tri in enumerate(self.linear_iterator()):
            ts = tuple(vars.Var(term=t) for t in tri.terms())
            crit1 = tuple(c.copy() for c in crit)  # FIXME optimize without to copy
            # list is required to evaluate all vars unification, BCS any()/all()
            # works only until the 1st failing item
            unify_res = [c.unify(t) for c,t in zip(crit1, ts)]
            if all(unify_res):
                if chap:
                    numchap = NumeratedChapter(chapname, chap)
                    self._chapters.append(numchap)
                chapname = name(ts)
                chap = []
            chap.append((i, tri))
        if chap:
            numchap = NumeratedChapter(chapname, chap)
            self._chapters.append(numchap)
        return self


################################################################################
#                                     Query
class Query(dataset.Dataset):
    _query: Optional[str]


    def __init__(self, data:OrderedSet[scanner.Tri], query: str) -> None:
        super().__init__(data)
        self._query = query
