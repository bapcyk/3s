#-------------------------------------------------------------------------------
# Name:        utils.py
#
# Descr:
#
# Author:      5442
#
# Created:     21.05.2022
# Copyright:   (c) 5442 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from __future__ import annotations
from typing import *

Char = str


T = TypeVar('T')

OrderedSetItems = Dict[T, None]

class OrderedSet(Generic[T]):
    """Limited implementation of an ordered set"""
    __items: OrderedSetItems[T]

    def __init__(self, items:Optional[Iterable[T]]=None) -> None:
        self.__items = {}
        if items is not None:
            for i in items:
                self.add(i)

    def __iter__(self) -> Iterator[T]:
        return iter(self.__items)

    def add(self, item:T) -> OrderedSet[T]:
        self.__items[item] = None
        return self

    def clear(self) -> OrderedSet[T]:
        self.__items.clear()
        return self


##class Missing: pass
##MISSING = Missing()

##T = TypeVar('T')
##
##
##class Linear(Generic[T]):
##    _items:List[T] = []
##    _pos:int = 0
##
##
##    def __init__(self, items:List[T]):
##        self._items = list(items)
##        self._pos = 0
##
##
##    def has_next(self) -> bool:
##        return self._pos < len(self._items)
##
##
##    def has_prev(self) -> bool:
##        return self._pos > 0
##
##
##    def next(self) -> Union[T, NoReturn]:
##        if self.has_next():
##            res = self._items[self._pos]
##            self._pos += 1
##            return res
##        else:
##            raise StopIteration
##
##
##    def back(self) -> Union[T, NoReturn]:
##        if self.has_prev():
##            res = self._items[self._pos]
##            self._pos -= 1
##            return res
##        else:
##            raise StopIteration
