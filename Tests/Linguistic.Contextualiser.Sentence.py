#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

sys.path.append("../")

from Data import Models
import Services.Perseus
import Linguistic

from Services.Perseus import MySQL as Perseus
from Services.Perseus.MySQL import Lemma
from Linguistic.Contextualiser.syntax import WordWindow as Contextualiser
from Services.Perseus.MySQL import Occurence
from Services.Perseus.MySQL import LatinLemmatizer as FormFinder

#Set up with real data
L = Lemma()
r = L.search("habeo", strict = True)
habeo = r[0]
O = Occurence()
R = O.search(habeo)[2]

#Context test
C = Contextualiser(FormFinderClass = FormFinder)
CCleaned = C.strip(R, habeo)
for occ in CCleaned:
	print occ.text