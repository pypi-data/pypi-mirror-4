# -*- coding: utf-8 -*-

"""
Représentation d'une carte et des couleurs.

Création d'une carte avec une couleur et une valeur ::

  >>> a = Carte(COEUR, 2)
  >>> print(a)
  Carte<COEUR, 2>

Deux cartes peuvent être comparées ::

  >>> b = Carte(TREFLE, 4)
  >>> b >= a
  True
  >>> b >= b
  True
  >>> a >= b
  False

Création d'une carte avec son code couleur ::

  >>> Carte.create('C', 2)
  Carte<COEUR, 2>
  >>> Carte.create('A', 1)
  Traceback (most recent call last):
    ...
  AssertionError: Code couleur inconnue

Création d'une carte avec une valeur initiale aléatoire ::

  >>> Carte.create('T')
  Carte<TREFLE, ...>

"""

from __future__ import print_function

import random


__author__ = '{martin.monperrus,raphael.marvie}@univ-lille1.fr'
__date__ = 'Thu Jun 14 18:24:47 2012'


COEUR = 'COEUR'
CARREAU = 'CARREAU'
PIQUE = 'PIQUE'
TREFLE = 'TREFLE'

COULEURS = {
    'C': COEUR,
    'K': CARREAU,
    'P': PIQUE,
    'T': TREFLE
}


class Carte(object):

    def __init__(self, couleur, valeur):
        self.couleur = couleur
        self.valeur = valeur

    def __repr__(self):
        return 'Carte<{couleur}, {valeur}>'.format(
            couleur=self.couleur, valeur=self.valeur)

    def __ge__(self, other):
        return self.valeur >= other.valeur

    @classmethod
    def create(cls, lettre, valeur=None):
        assert lettre in 'CKPT', "Code couleur inconnue"
        valeur = valeur or random.randint(1, 13)
        return Carte(COULEURS[lettre], valeur)


def testmod():
    import doctest
    optionflags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
    doctest.testmod(optionflags=optionflags, verbose=False)


if __name__ == '__main__':
    testmod()

# eof
