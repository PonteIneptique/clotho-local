#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

sys.path.append("../")

from Data import Models
import Services.Perseus
import Linguistic


Perseus = Services.Perseus.MySQL
Lemma = Services.Perseus.MySQL.Lemma
Contextualiser = Linguistic.Contextualiser.Sentence
Occurence = Services.Perseus.MySQL.Occurence


#Set up with real data
L = Lemma()
r = L.search("habeo", strict = True)
habeo = r[0]
O = Occurence()
R = O.search(habeo)[1]

#Context test
C = Contextualiser(FormFinderClass = Services.Perseus.MySQL.LatinFormFinder)
CCleaned = C.strip(R, habeo)
print CCleaned