#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys 
sys.path.append("../..")

import Data

class Model(object):
	def __init__(self):
		pass

	def strip(self, occurence, lemma):
		if not isinstance(occurence, Data.Models.documents.Occurence):
			raise TypeError("Occurence is not a Data.Models.documents.Occurence")
		if not isinstance(lemma, Data.Models.lang.Lemma):
			raise TypeError("Lemma is not a Data.Models.lang.Lemma")
		raise NotImplementedError("Strip is not part of the class")