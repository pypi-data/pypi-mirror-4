# -*- coding: utf-8 -*-

from Cartes import *

fixer_delai(.2)


def trier(tas_origine, tas_destination, tas_temporaire):
    """Tri les carte par valeur

    Tri le tas_origine dans tas_destination en tas_temporaire
    Contrat d'utilisation: tas_destination et tas_temporaire sont vides.
    """
    while tas_non_vide(tas_origine):
        deplacer_plus_petite(tas_origine, tas_destination, tas_temporaire)
        replacer_les_cartes(tas_temporaire, tas_origine)


def deplacer_plus_petite(tas_origine, tas_destination, tas_temporaire):
    deplacer_sommet(tas_origine, tas_destination)
    while tas_non_vide(tas_origine):
        if superieur(tas_origine, tas_destination):
            deplacer_sommet(tas_origine, tas_temporaire)
        else:
            deplacer_sommet(tas_destination, tas_temporaire)
            deplacer_sommet(tas_origine, tas_destination)


def replacer_les_cartes(tas_origine, tas_destination):
    while tas_non_vide(tas_origine):
        deplacer_sommet(tas_origine, tas_destination)


# le premier tas est initialisé avec des cartes aléatoires

init_tas(1, "[C+P+T+K]")

# tri des cartes du tas 1 vers le tas 2 en utilisant le 3 comment tampon

trier(1, 2, 3)

# on profite de l'affichage

pause("Terminé")

# eof
