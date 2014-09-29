#!/usr/bin/python
# -*- coding: utf-8 -*-

class Lemma(object):
	def __init__(self):
		pass

	def search(self, query, uid = False, strict = False):
		""" This function should return a list of [Data.Models.lang.Lemma]

		"""
		raise NotImplementedError()

	def new(self, lemma):
		if not(isinstance(lemma, Models.lang.Lemma)):
			raise TypeError("Lemma is not an instance of Models.lang.Lemma")
		raise NotImplementedError()

		
	def remove(self, lemma):
		if not(isinstance(lemma, Models.lang.Lemma)):
			raise TypeError("Lemma is not an instance of Models.lang.Lemma")
		raise NotImplementedError()