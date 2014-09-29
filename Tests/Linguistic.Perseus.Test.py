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

l = Lemma()

#######################################
#Just in case setting up
original_lemmas = l.search("pedicare")
if len(original_lemmas) > 0:
	for lemma in original_lemmas:
		l.remove(lemma)
#######################################

search = l.search("pedicar")

assert len(search) == 0, "No Pedicare form found"

test_lemma = Models.lang.Lemma(None, "pedicare", "Sodomiser")
test_lemma.uid = l.new(test_lemma)

assert isinstance(test_lemma.uid, long), "Inserting a new lemma and return a UID is false"

search = l.search("pedicar")
assert (len(search) == 1 and search[0].toString() == "pedicare"), "No Pedicare form found"
assert len(l.search("pedicar", strict = True)) == 0, "Strict search should not have found pedicar"

assert l.remove(Models.lang.Lemma(None, "pedicare", "Sodomiser")), "Can't remove last lemma"

#######################################
#Just in case backing up
"""
if len(original_lemmas) > 0:
	for lemma in original_lemmas:
		l.new(lemma)
"""
#######################################