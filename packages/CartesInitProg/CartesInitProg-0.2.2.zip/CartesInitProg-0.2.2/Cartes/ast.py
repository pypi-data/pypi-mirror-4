# -*- coding: utf-8 -*-

"""
Heap initialization language AST as well as its evaluation.

Some mocking utilities for tests ::

  >>> class Dummy:
  ...   def __init__(self, name): self.name = name
  ...   def __repr__(self): return self.name
  ...   def eval(self): return self.name


Or permits to choose one element between 2 to n ::

  # mock random.choice to return last elements of Or
  >>> random.choice = lambda x: x[-1]

  >>> o = Or(Dummy('A'), Dummy('B'))
  >>> o.eval()
  'B'

  >>> o.append(Dummy('C'))
  Or(A, B, C)

  >>> o.eval()
  'C'

Expression permits to evaluate a sequence ::

  >>> e = Expr()
  >>> e.eval()
  []

  >>> e.append(Dummy('A'))
  >>> e.append(Dummy('B'))
  >>> e.eval()
  ['A', 'B']


Repeat permits to repeat a sequence of elements ::

  # mock random.randint to return 2
  >>> random.randint = lambda x, y: 2

  >>> r = Repeat([Dummy('A'), Dummy('B')])
  >>> r.eval()
  [['A', 'B'], ['A', 'B']]

  >>> r.append(Dummy('C'))
  >>> r.eval()
  [['A', 'B', 'C'], ['A', 'B', 'C']]


Color permit to create a card ::

  # mocking Carte.create
  >>> Carte.create = classmethod(lambda x, y: Dummy(y))

  >>> c = Color('A')
  >>> c.eval()
  A

"""

# TODO Refactor Repeat and Expr (code and bahavior in common)


import random

from Cartes.model import Carte


__author__ = '{martin.monperrus,mirabelle.nebut,raphael.marvie}@univ-lille1.fr'
__date__ = 'Thu Jun 21 10:54:56 2012'


class Color(object):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Color<{0}>'.format(self.name)

    def eval(self):
        return Carte.create(self.name)


class Or(object):

    def __init__(self, left, right):
        self.elements = [left, right]

    def append(self, value):
        self.elements.append(value)
        return self

    def __repr__(self):
        return 'Or({0})'.format(
            ', '.join(str(e) for e in self.elements))

    def eval(self):
        return random.choice(self.elements).eval()


class Repeat(object):

    def __init__(self, what=None):
        self.what = what or list()

    def __repr__(self):
        return 'Repeat({0})'.format(', '.join(repr(w) for w in self.what))

    def append(self, value):
        self.what.append(value)

    def pop(self):
        return self.what.pop()

    def eval(self):
        return [[w.eval() for w in self.what]
                for n in range(random.randint(0, 10))]


class Expr(object):

    def __init__(self, what=None):
        self.what = what or list()

    def append(self, value):
        self.what.append(value)

    def pop(self):
        return self.what.pop()

    def __len__(self):
        return len(self.what)

    def __repr__(self):
        return 'Expr({0})'.format(', '.join(repr(w) for w in self.what))

    def eval(self):
        return [w.eval() for w in self.what]


def testmod():
    import doctest
    optionflags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
    doctest.testmod(optionflags=optionflags, verbose=False)


if __name__ == '__main__':
    testmod()

# eof
