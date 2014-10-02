#!/usr/bin/python
# -*- coding: utf-8 -*-

class Finder(object):
	def __init__(self):
		pass

	def check(self):
		#No error has it might not be used if there is no configuration
		return True

	def install(self):
		raise NotImplementedError("install not implemented")

	def getForms(self, lemma):
		raise NotImplementedError("getForms not implemented")