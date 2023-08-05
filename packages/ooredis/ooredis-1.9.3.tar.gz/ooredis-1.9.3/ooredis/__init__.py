# coding: utf-8

__all__ = [
    'connect', 'get_client',
    'type_case',
    'Dict', 'Set', 'SortedSet', 'String', 'Counter', 'Deque',
    '__version__',
]

import type_case

from client import connect, get_client

from key.dict import Dict
from key.set import Set
from key.sorted_set import SortedSet
from key.string import String
from key.counter import Counter
from key.deque import Deque

__version__ = "1.9.3"
