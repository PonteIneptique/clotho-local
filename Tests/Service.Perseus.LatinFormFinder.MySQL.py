#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

sys.path.append("../")

from Data import Models
import Services.Perseus
import Linguistic


from Services.Perseus import MySQL as Perseus
from Services.Perseus.MySQL import Lemma
from Services.Perseus.MySQL import LatinFormFinder as FormFinder

L = Lemma()
r = L.search("actum", strict = True)
habeo = r[0]

f = FormFinder()
print f.getForms(habeo)