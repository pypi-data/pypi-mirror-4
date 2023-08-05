# -*- coding: utf-8 -*-

"""
Les principaux elements du Module Cartes
----------------------------------------
* init_tas : numero_tas * string -> unit
     init_tas(num_tas,chaine) : initialise le tas num_tas
     avec la description donnee par chaine.

* deplacer_sommet : numero_tas * numero_tas -> unit
     deplacer_sommet(num_tas1,num_tas2) :  deplace la carte au
     sommet du tas num_tas1 vers le tas num_tas2.

* tas_vide : numero_tas -> bool
     tas_vide(num_tas) = vrai si le tas num_tas est vide, faux sinon.

* tas_non_vide : numero_tas -> bool
     tas_non_vide(num_tas) = vrai si le tas num_tas n'est pas vide,
     faux sinon.

* couleur_sommet : numero_tas -> couleur
     couleur_sommet(num_tas) = couleur au sommet du tas num_tas.

* sommet_trefle : numero_tas -> bool
     sommet_trefle(num_tas) = vrai si la carte au sommet du tas num_tas
     est un trefle, faux sinon.

* sommet_carreau : numero_tas -> bool
     sommet_carreau(num_tas) = vrai si la carte au sommet du tas num_tas
     est un carreau, faux sinon.

* sommet_coeur : numero_tas -> bool
     sommet_coeur(num_tas) = vrai si la carte au sommet du tas num_tas
     est un coeur, faux sinon.

* sommet_pique : numero_tas -> bool
     sommet_pique(num_tas) = vrai si la carte au sommet du tas num_tas
     est un pique, faux sinon.

* superieur : numero_tas * numero_tas -> bool
     superieur(num_tas1,num_tas2) = vrai si la carte au sommet
     du tas num_tas1 est superieure ou egale a celle du tas num_tas2,
     faux sinon.
"""


from Cartes.core import Core
from Cartes.core import Etat
from Cartes.model import *
from Cartes.ui import *


__author__ = '{martin.monperrus,raphael.marvie}@univ-lille1.fr'
__date__ = 'Thu Jun 14 18:08:41 2012'


__all__ = [
    'COEUR', 'CARREAU', 'PIQUE', 'TREFLE',
    'init_tas',
    'deplacer_sommet',
    'couleur_sommet',
    'tas_vide',
    'tas_non_vide',
    'sommet_trefle',
    'sommet_pique',
    'sommet_coeur',
    'sommet_carreau',
    'superieur',
    'affichage_en_mode_graphique',
    'affichage_en_mode_texte',
    'affichage_en_mode_texte_et_graphique',
    'fixer_delai',
    'pause'
]


# Cartes' API from OO to procedural

CORE = Core(Etat(), Delai())


def pause(message=''):
    """Pause l'exécution du programme."""
    CORE.pause(message)


def init_tas(num_tas, chaine):
    """Initialise le tas <num_tas> avec la spécification <chaine>"""
    CORE.init_tas(num_tas, chaine)


def deplacer_sommet(num_tas1, num_tas2):
    """Déplace la carte au sommet du tas <num_tas1> vers le tas <num_tas2>"""
    CORE.deplacer_sommet(num_tas1, num_tas2)


def maj_affichage():
    """Met à jour l'affichage des cartes"""
    CORE.maj_affichage()


def couleur_sommet(num_tas):
    """Retourne la couleur du tas <num_tas"""
    return CORE.couleur_sommet(num_tas)


def tas_vide(num_tas):
    """Retourne True si le tas <num_tas> est vide, False sinon"""
    return CORE.tas_vide(num_tas)


def tas_non_vide(num_tas):
    """Retourne True si le tas <num_tas> est non vide, False sinon"""
    return CORE.tas_non_vide(num_tas)


def sommet_trefle(num_tas):
    """Retourne True si le sommet du tas <num_tas> est un trèfle, False sinon"""
    return CORE.sommet_trefle(num_tas)


def sommet_pique(num_tas):
    """Retourne True si le sommet du tas <num_tas> est un pique, False sinon"""
    return CORE.sommet_pique(num_tas)


def sommet_coeur(num_tas):
    """Retourne True si le sommet du tas <num_tas> est un coeur, False sinon"""
    return CORE.sommet_coeur(num_tas)


def sommet_carreau(num_tas):
    """Retourne True si le sommet du tas <num_tas> est un carreau, False sinon"""
    return CORE.sommet_carreau(num_tas)


def superieur(num_tas1, num_tas2):
    """Retourne True si le sommet du tas <num_tas> est supérieur au sommet de <num_tas2>"""
    return CORE.superieur(num_tas1, num_tas2)


def affichage_en_mode_texte():
    """Active l'affichage en mode texte"""
    CORE.affichage_en_mode_texte()


def affichage_en_mode_graphique():
    """Active l'affichage en mode graphique"""
    CORE.affichage_en_mode_graphique()


def affichage_en_mode_texte_et_graphique():
    """Active l'affichage en mode texte et en mode graphique"""
    CORE.affichage_en_mode_texte_et_graphique()


def fixer_delai(delai):
    """Fixe le delai d'affichage entre deux mouvements"""
    CORE.fixer_delai(delai)

# eof
