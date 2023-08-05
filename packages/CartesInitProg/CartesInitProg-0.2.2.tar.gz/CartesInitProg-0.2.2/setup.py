# -*- coding: utf-8 -*-

"""
Setup for Cartes deployment

For sdist deployments, do not forget MANIFEST.in file to include data
files.
"""

from setuptools import setup

VERSION = '0.2.2'

__author__ = '{martin.monperrus,raphael.marvie}@univ-lille1.fr'
__date__ = 'Thu Jun 21 21:14:51 2012'


with open('README') as file:
    long_description = file.read()

setup(
    name='CartesInitProg',
    version=VERSION,
    description="Package Cartes pour le module d'InitProg.",
    long_description=long_description,
    author='Martin Monperrus & Raphael Marvie',
    author_email=__author__,
    url='http://www.fil.univ-lille1.fr/',
    packages=['Cartes'],
    include_package_data=True,
    package_data={'Cartes': ['Cartes/images/*.gif']},
    install_requires='pyparsing >= 1.5.6'
)



# eof
