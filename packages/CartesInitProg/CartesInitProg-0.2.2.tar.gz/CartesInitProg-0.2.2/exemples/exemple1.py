# -*- coding: utf-8 -*-

from Cartes import *


# Intialisation d'un tas avec 4 carte et trois tas vides
init_tas(1,"CPCP")
init_tas(2,"")
init_tas(3,"")
init_tas(4,"")

# Nous savons que la carte du dessus est un Pique, donc va sur le tas 2
deplacer_sommet(1,2)

# La suivante est un coeur, donc va sur le tas 3
deplacer_sommet(1,3)

# La suivante est un pique, donc va sur le tas 2
deplacer_sommet(1,2)

# La dernière est un coeur, donc va sur le tas 3
deplacer_sommet(1,3)

# on profite de l'affichage
pause("Terminé")

# eof
