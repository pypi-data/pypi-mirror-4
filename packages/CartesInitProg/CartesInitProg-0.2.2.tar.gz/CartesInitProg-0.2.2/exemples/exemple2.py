# -*- coding: utf-8 -*-

from Cartes import *


def sommet_rouge(tas):
    """retourne vrai si la carte du sommet est rouge"""
    return sommet_coeur(tas) or sommet_carreau(tas) 


def trier_par_couleur(tas, tas_rouge, tas_noir):
    """tri les carte de tas en fonction de leur couleur"""
    while tas_non_vide(tas):
        if sommet_rouge(tas):
            deplacer_sommet(tas, tas_rouge)
        else:
            deplacer_sommet(tas, tas_noir)


# initialisation du premier tas avec des cartes au hasard (les autres sont vides)
init_tas(1,"[C+P+T+K]")


# tri par couleurs du tas 1 vers les tas 2 (rouge) et 3 (noir)
trier_par_couleur(1, 2, 3)

# on profite de l'affichage
pause("Terminé")

# eof
