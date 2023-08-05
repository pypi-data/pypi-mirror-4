# -*- coding: utf-8 -*-

"""
Core objects for the carte library.
"""


from __future__ import print_function

from Cartes.model import *
from Cartes.parser import Parser
from Cartes.ui import AfficheurGraphique
from Cartes.ui import AfficheurTexte

try:
    # Is this python 2 ?
    wait_for_input = raw_input
except NameError:
    # This is python 3
    wait_for_input = input

__author__ = '{martin.monperrus,raphael.marvie}@univ-lille1.fr'
__date__ = 'Thu Jun 14 18:16:34 2012'


class Core(object):

    def __init__(self, etat, delai):
        self.etat = etat
        self.afficheurs = []
        self.delai = delai

    def pause(self, message=""):
        wait_for_input(message + " (appuyez sur la touche Entree pour continuer)")

    def init_tas(self, num_tas, chaine):
        self.etat.init_tas(num_tas - 1, chaine)
        self.maj_affichage()

    def deplacer_sommet(self, num_tas1, num_tas2):
        self.etat.deplacer_sommet(num_tas1 - 1, num_tas2 - 1)
        self.maj_affichage()

    def maj_affichage(self):
        if self.afficheurs == []:
            self.affichage_en_mode_graphique()
        for afficheur in self.afficheurs:
            afficheur.affiche(self.etat)

    def couleur_sommet(self, num_tas):
        return self.etat.couleur_sommet(num_tas - 1)

    def tas_vide(self, num_tas):
        return self.etat.tas_vide(num_tas - 1)

    def tas_non_vide(self, num_tas):
        return not self.etat.tas_vide(num_tas - 1)

    def sommet_trefle(self, num_tas):
        return self.couleur_sommet(num_tas) == TREFLE

    def sommet_pique(self, num_tas):
        return self.couleur_sommet(num_tas) == PIQUE

    def sommet_coeur(self, num_tas):
        return self.couleur_sommet(num_tas) == COEUR

    def sommet_carreau(self, num_tas):
        return self.couleur_sommet(num_tas) == CARREAU

    def superieur(self, num_tas1, num_tas2):
        return self.etat.est_superieur(num_tas1 - 1, num_tas2 - 1)

    def affichage_en_mode_texte(self):
        self.afficheurs = [AfficheurTexte.create(self.delai)]

    def affichage_en_mode_graphique(self):
        self.afficheurs = [AfficheurGraphique.create(self.delai)]

    def affichage_en_mode_texte_et_graphique(self):
        self.afficheurs = [
            AfficheurTexte.create(self.delai),
            AfficheurGraphique.create(self.delai)]

    def fixer_delai(self, delai):
        self.delai.valeur = delai


class Etat(object):
    """
     >>> etat = Etat()
     >>> etat
     []
     []
     []
     []

     >>> etat.init_tas(0,'C')
     >>> etat
     [Carte<COEUR, ...>]
     []
     []
     []

     >>> etat.deplacer_sommet(0,1)
     >>> etat
     []
     [Carte<COEUR, ...>]
     []
     []

     >>> etat.tas_vide(0)
     True
     >>> etat.tas_vide(1)
     False
     >>> etat.est_superieur(0,1)
     Traceback (most recent call last):
       ...
     AssertionError: Le tas est vide.

     >>> etat.tas[0].ajouter_carte(Carte(COEUR, 1))
     >>> etat.tas[1].ajouter_carte(Carte(PIQUE, 2))
     >>> etat.est_superieur(1, 0)
     True

    """
    def __init__(self):
        self.tas = [Tas() for i in range(4)]

    def init_tas(self, num_tas, chaine):
        self.tas[num_tas].init_tas(chaine)

    def couleur_sommet(self, num_tas):
        return self.tas[num_tas].couleur_sommet()

    def deplacer_sommet(self, num_tas1, num_tas2):
        carte = self.tas[num_tas1].prendre_carte()
        self.tas[num_tas2].ajouter_carte(carte)

    def tas_vide(self, num_tas):
        return self.tas[num_tas].est_vide()

    def est_superieur(self, num_tas1, num_tas2):
        return self.tas[num_tas1].sommet() >= self.tas[num_tas2].sommet()

    def __repr__(self):
        return '\n'.join(repr(x) for x in self.tas)


class Tas(object):
    """
      >>> tas = Tas()
      >>> tas.init_tas('')
      >>> tas
      []
      >>> tas.est_vide()
      True
      >>> tas.init_tas('C')
      >>> tas.est_vide()
      False
      >>> tas
      [Carte<COEUR, ...>]
      >>> tas.init_tas('CK')
      >>> tas
      [Carte<COEUR, ...>, Carte<CARREAU, ...>]
      >>> tas.couleur_sommet()
      'CARREAU'
      >>> carte = tas.prendre_carte()
      >>> tas
      [Carte<COEUR, ...>]
      >>> tas.ajouter_carte(carte)
      >>> tas
      [Carte<COEUR, ...>, Carte<CARREAU, ...>]
    """

    def __init__(self):
        self.cards = list()
        self.parser = Parser()

    def init_tas(self, chaine):
        self.cards = self.parser.parse(chaine)

    def couleur_sommet(self):
        return self.sommet().couleur

    def ajouter_carte(self, carte):
        self.cards.append(carte)

    def prendre_carte(self):
        assert self.cards, "Le tas source est vide."
        return self.cards.pop()

    def est_vide(self):
        return self.cards == []

    def sommet(self):
        assert self.cards, "Le tas est vide."
        return self.cards[-1]

    def __repr__(self):
        return repr(self.cards)


if __name__ == '__main__':
    import doctest
    optionflags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
    doctest.testmod(optionflags=optionflags, verbose=False)

# eof
