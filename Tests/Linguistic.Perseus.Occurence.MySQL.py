#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

sys.path.append("../")

from Data import Models
import Linguistic.lang as lang
import Linguistic.Perseus

Perseus = Linguistic.Perseus.MySQL
Lemma = Linguistic.Perseus.MySQL.Lemma

Occurence = Linguistic.Perseus.MySQL.Occurence
L = Lemma()
r = L.search("habeo", strict = True)
habeo = r[0]
O = Occurence()
R = O.search(habeo)
print len(R)