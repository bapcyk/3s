#-------------------------------------------------------------------------------
# Name:        dataset.py
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
from utils import *
import scanner


################################################################################
#                                     Dataset
class Dataset:
    _data: OrderedSet[scanner.Tri]

    def __init__(self, data:OrderedSet[scanner.Tri]) -> None:
        self._data = data


    def linear_iterator(self) -> Iterable[scanner.Tri]:
        return iter(self._data)