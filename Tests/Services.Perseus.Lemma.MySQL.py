#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

sys.path.append("../")

from Data import Models
import Services.Perseus

Perseus = Services.Perseus.MySQL
Lemma = Services.Perseus.MySQL.Lemma

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