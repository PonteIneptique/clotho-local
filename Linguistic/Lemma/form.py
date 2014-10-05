#!/usr/bin/python
# -*- coding: utf-8 -*-

class Lemmatizer(object):
	def __init__(self):
		pass

	def check(self):
		#No error has it might not be used if there is no configuration
		return True

	def install(self):
		raise NotImplementedError("install not implemented")

	def getForms(self, lemma):
		raise NotImplementedError("getForms not implemented")

	def getLemmatized(self, occurence):
		#Should return an Occurence with a list of lemma in Occurence.lemmatized
		raise NotImplementedError("getLemmatized is not implemented")