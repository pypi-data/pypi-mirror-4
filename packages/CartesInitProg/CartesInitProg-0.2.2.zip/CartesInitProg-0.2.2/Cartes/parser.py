# -*- coding: utf-8 -*-

"""
Parser for heap initialization DSL.

  # mocking ast constructions
  >>> Or.eval = lambda x: [x]
  >>> Expr.eval = lambda x: x.what
  >>> Repeat.eval = lambda x: [x]
  >>> Color.eval = lambda x: [x]

Let's create a parser and parse somme expressions ::

  >>> parser = Parser()

  >>> parser.parse("")
  []

  >>> parser.parse("()")
  [Expr()]

  >>> parser.parse("K")
  [Color<K>]

  >>> parser.parse("CK")
  [Color<C>, Color<K>]

  >>> parser.parse("K+P")
  [Or(Color<K>, Color<P>)]

  >>> parser.parse("C+()")
  [Or(Color<C>, Expr())]

  >>> parser.parse("K+P+T")
  [Or(Color<K>, Color<P>, Color<T>)]

  >>> parser.parse("K+(P+T)")
  [Or(Color<K>, Expr(Or(Color<P>, Color<T>)))]

  >>> parser.parse("(CK)")
  [Expr(Color<C>, Color<K>)]

  >>> parser.parse("[CK]")
  [Repeat(Color<C>, Color<K>)]

  >>> parser.parse("[C+K]")
  [Repeat(Or(Color<C>, Color<K>))]

  >>> parser.parse("(C+P)K[C+T]")
  [Expr(Or(Color<C>, Color<P>)), Color<K>, Repeat(Or(Color<C>, Color<T>))]

  >>> parser.parse("((CK)+(PT))")
  [Expr(Or(Expr(Color<C>, Color<K>), Expr(Color<P>, Color<T>)))]

  >>> parser.parse("[[PK]+[CK]]")
  [Repeat(Or(Repeat(Color<P>, Color<K>), Repeat(Color<C>, Color<K>)))]

  >>> parser.parse("+P")
  Traceback (most recent call last):
    ...
  AssertionError: Expected Re:('[CcKkPpTt]') (at char 0), (line:1, col:1)

  >>> parser.parse("[]")
  Traceback (most recent call last):
    ...
  AssertionError: Expected Re:('[CcKkPpTt]') (at char 1), (line:1, col:2)

"""


from pyparsing import *

from Cartes.ast import *


__author__ = '{martin.monperrus,mirabelle.nebut,raphael.marvie}@univ-lille1.fr'
__date__ = 'Thu Jun 14 15:13:52 2012'


class ParseActions(object):

    def init(self):
        self.stack = [Expr()]

    @property
    def result(self):
        return flatten(self.stack[-1].eval())

    def literals(self, strg, location, tokens):
        name = tokens[0]
        self.stack[-1].append(Color(name))

    def nexpr(self, *args):
        # brackets' actions are enough to process this statement.
        pass

    def parexpr(self, *args):
        # parenthesis' actions are enough to process this statement.
        pass

    def orexpr(self, *args):
        right = self.stack[-1].pop()
        left = self.stack[-1].pop()
        if isinstance(left, Or):
            e = left.append(right)
        else:
            e = Or(left, right)
        self.stack[-1].append(e)

    def expr(self, *args):
        # expression are virtual, first one automatically created
        pass

    def lbrack(self, *args):
        self.stack.append(Repeat())

    def rbrack(self, *args):
        repeat = self.stack.pop()
        self.stack[-1].append(repeat)

    def lparen(self, *args):
        self.stack.append(Expr())

    def rparen(self, *args):
        expr = self.stack.pop()
        self.stack[-1].append(expr)


class Parser(object):

    actions = ParseActions()

    LPAREN = Suppress("(").setParseAction(actions.lparen)
    RPAREN = Suppress(")").setParseAction(actions.rparen)
    LBRACK = Suppress("[").setParseAction(actions.lbrack)
    RBRACK = Suppress("]").setParseAction(actions.rbrack)
    C = CaselessLiteral('C')
    K = CaselessLiteral('K')
    P = CaselessLiteral('P')
    T = CaselessLiteral('T')

    EXPR = Forward()
    LITERALS = oneOf('C c K k P p T t')
    GROUP = LPAREN + Optional(EXPR) + RPAREN
    REPEAT = LBRACK + EXPR + RBRACK
    ATOM = LITERALS ^ GROUP ^ REPEAT
    SEQATOM = OneOrMore(ATOM)
    OREXPRBLOCK = (Literal('+') + SEQATOM)
    OREXPR = SEQATOM + OneOrMore(OREXPRBLOCK)
    EXPR << OneOrMore(SEQATOM ^ OREXPR)

    LITERALS.setParseAction(actions.literals)
    OREXPRBLOCK.setParseAction(actions.orexpr)
    GROUP.setParseAction(actions.parexpr)
    REPEAT.setParseAction(actions.nexpr)
    EXPR.setParseAction(actions.expr)

    def parse(self, declaration):
        if not declaration:
            return list()
        self.actions.init()
        try:
            self.EXPR.parseString(declaration)
        except ParseException as e:
            raise AssertionError(e)
        return self.actions.result

class InitialisationIncorrecte(Exception):
    pass

def flatten(arg):
    """Applatisseur de liste

      >>> flatten([])
      []
      >>> flatten([1, 2, 3])
      [1, 2, 3]
      >>> flatten([1, ['a', ['b', 'c']], 3])
      [1, 'a', 'b', 'c', 3]
    """
    def lflat(lst, result):
        for e in lst:
            if isinstance(e, list):
                lflat(e, result)
            else:
                result.append(e)
        return result
    return lflat(arg, list())


def testmod():
    import doctest
    optionflags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
    doctest.testmod(optionflags=optionflags, verbose=False)


if __name__ == '__main__':
    testmod()

# eof
