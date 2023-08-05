# -*- coding: utf-8 -*-

"""
User interface for the Carte package (Text based, Tkinter).


Some mocking functions (delai, canvas et classes de core) ::

  >>> Delai.attendre = lambda x: 'attendre'
  >>> delai = Delai()

  >>> def create_image(*args, **kwargs):
  ...     print('Affiche image', args[1:3])  # displaying position
  >>> Canvas.create_image = create_image

  >>> Carte = type('CarteMock', (), dict(couleur='COEUR', valeur=1))
  >>> Tas = type('TasMock', (), dict(cards=[Carte(), Carte()]))
  >>> Etat = type('EtatMock', (), dict(tas=[Tas(), Tas()]))


Création et utilisation d'un afficheur texte ::

  >>> afficheur = AfficheurTexte.create(delai)
  >>> etat = Etat()
  >>> afficheur.affiche(etat)
  <__main__.EtatMock object at ...>
  ----


Création d'un afficheur graphique ::

  >>> afficheur = AfficheurGraphique.create(delai)


Les cartes sont chargées ::

  >>> len(afficheur.cards_data)
  52


Affichage d'un état ::

  >>> afficheur.affiche(Etat())
  Affiche image (0, 576...)
  Affiche image (0, 552...)
  Affiche image (102, 576...)
  Affiche image (102, 552...)


Utilisation du pattern singleton (toujours la même instance) ::

  >>> second = AfficheurGraphique.create(delai)
  >>> second is afficheur
  True

"""

from __future__ import print_function

import glob
import os
import time

try:    
    # This is python 2 ?
    from thread import start_new_thread
except ImportError:   
    # This is python 3
    from _thread import start_new_thread

try:  
    # This is python 2 ?
    from Tkinter import Tk
    from Tkinter import Canvas
    from Tkinter import SW
    from Tkinter import ALL
    from Tkinter import PhotoImage
except ImportError:
    try:
        # This is python 3 ?
        from tkinter import Tk
        from tkinter import Canvas
        from tkinter import SW
        from tkinter import ALL
        from tkinter import PhotoImage
    except ImportError:
        assert False, 'Tkinter semble manquer.'


__author__ = '{martin.monperrus,raphael.marvie}@univ-lille1.fr'
__date__ = 'Fri Jun 15 16:46:28 2012'


CARDHEIGHT = 96
CARDWIDTH = 72

PILEDIFF = CARDHEIGHT / 4
TASSEP = 30

HEIGHT = CARDHEIGHT * 6
WIDTH = CARDWIDTH * 4 + 3 * TASSEP

BASEDIR = os.path.dirname(__file__)

UNE_SECONDE = 1.0


class Delai(object):

    def __init__(self, valeur=UNE_SECONDE):
        self.valeur = valeur

    def attendre(self):
        time.sleep(self.valeur)


class AfficheurGraphique(object):

    afficheur = None

    def __init__(self, delai):
        self.delai = delai

    def threadmain(self):
        master = Tk()
        self.canvas = Canvas(master, width=WIDTH, height=HEIGHT)
        self.canvas.pack()
        self.load_cards()
        master.mainloop()

    def load_cards(self):
        self.cards_data = {}
        pattern = os.path.join(BASEDIR, 'images', '*.gif')
        for x in glob.glob(pattern):
            path, filename = os.path.split(x)
            key, ext = os.path.splitext(filename)
            self.cards_data[key] = PhotoImage(file=x)

    def affiche(self, etat):
        self.canvas.delete(ALL)
        for indice, tas in enumerate(etat.tas):
            self.affiche_tas(tas, indice)
        self.canvas.update()  # Required by OSX problem re Tk/threads
        self.delai.attendre()

    def affiche_tas(self, tas, indice):
        for position, carte in enumerate(tas.cards):
            key = carte.couleur + str(carte.valeur)
            self.canvas.create_image(
                indice * (CARDWIDTH + TASSEP),
                HEIGHT - position * PILEDIFF,
                image=self.cards_data[key], anchor=SW)

    @classmethod
    def create(cls, delai):
        if cls.afficheur:
            return cls.afficheur
        cls.afficheur = AfficheurGraphique(delai)
        start_new_thread(cls.afficheur.threadmain, ())
        time.sleep(1)  # so the thread has time to initialize properly
        return cls.afficheur


class AfficheurTexte(object):

    def __init__(self, delai):
        self.delai = delai

    def affiche(self, etat):
        print(etat)
        print('----')

    @classmethod
    def create(cls, delai):
        return AfficheurTexte(delai)


def testmod():
    import doctest
    optionflags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
    doctest.testmod(optionflags=optionflags, verbose=False)
    return


if __name__ == '__main__':
    testmod()

# eof
