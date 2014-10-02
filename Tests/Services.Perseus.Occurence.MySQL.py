#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

sys.path.append("../")

from Data import Models
import Services.Perseus

Perseus = Services.Perseus.MySQL
Lemma = Services.Perseus.MySQL.Lemma

Occurence = Services.Perseus.MySQL.Occurence
L = Lemma()
r = L.search("habeo", strict = True)
habeo = r[0]
O = Occurence()
R = O.search(habeo)
assert len(R) == 30, "Fails but buggy test"