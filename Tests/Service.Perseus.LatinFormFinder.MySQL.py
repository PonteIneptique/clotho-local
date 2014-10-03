#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

sys.path.append("../")

from Data import Models
import Services.Perseus
import Linguistic


Perseus = Services.Perseus.MySQL
Lemma = Services.Perseus.MySQL.Lemma
Contextualiser = Linguistic.Contextualiser.WordWindow
FormFinder = Services.Perseus.MySQL.LatinFormFinder

L = Lemma()
r = L.search("actum", strict = True)
habeo = r[0]

f = FormFinder()
print f.getForms(habeo)