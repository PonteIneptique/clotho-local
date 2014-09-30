#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

print os.path.dirname(__file__)

sys.path.append("../")

from Data import Models
import Linguistic.lang as lang
import Linguistic.Perseus

Perseus = Linguistic.Perseus.MySQL
Lemma = Linguistic.Perseus.MySQL.Lemma


######################################
#
#
#	Test for Lemma
#
#
######################################
l = Lemma()
search = l.search("azerty")

assert len(search) == 0, "No Pedicare form found"

test_lemma = Models.lang.Lemma(None, "azerty", "Clavier")
test_lemma.uid = l.new(test_lemma)

assert isinstance(test_lemma.uid, long), "Inserting a new lemma and return a UID is false"

search = l.search("azerty")
assert (len(search) == 1 and search[0].toString() == "azerty"), "No azerty form found"
assert len(l.search("azert", strict = True)) == 0, "Strict search should not have found azert"

assert l.remove(Models.lang.Lemma(None, "azerty", "Clavier")), "Can't remove last lemma"



######################################
#
#
#	Test for Occurencies
#
#
######################################