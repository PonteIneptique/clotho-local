#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

sys.path.append("../")

from Data import Models

from Services.Perseus import MySQL as Perseus
from Services.Perseus.MySQL import Lemma
from Services.Perseus.MySQL import Occurence

L = Lemma()
r = L.search("habeo", strict = True)
habeo = r[0]
O = Occurence()
R = O.search(habeo)
assert len(R) == 30, "Fails but buggy test"