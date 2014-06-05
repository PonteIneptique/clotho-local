#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import codecs
import hashlib
import os
import sys

class Cache(object):
	def __init__(self):
		self.folder = {
			"sentence" : "./cache/sentence/",
			"search" : "./cache/search/",
			"form" : "./cache/form/"
		}
	def tUoB(self, obj, encoding='utf-8'):
		if isinstance(obj, basestring):
			if not isinstance(obj, unicode):
				obj = unicode(obj, encoding)
		return obj

	def hash(self, sentence, mode = "sentence"):
		""" Find the hash for a given query or mode	

		Keyword arguments:
		sentence --- A string by default in mode sentence or a dictionary in mode search
		mode --- Type of hash to retrieve (default = sentence)
		"""
		if mode == "search":
			sentence = " ".join([term for term in sentence["terms"]]) + " " + sentence["name"] + " " + sentence["mode"]

		sentence = hashlib.md5(sentence.encode("utf-8")).hexdigest()
		return sentence

	def filename(self, sentence, mode = "sentence"):
		""" Return the file name given a sentence or a query

		Keyword arguments:
		sentence --- A string by default in mode sentence or a dictionary in mode search
		mode --- Type of hash to retrieve (default = sentence)
		"""
		return self.hash(sentence, mode = mode) + ".json"


	def cache(self, query, mode, data = False, check = False):
		filename = self.filename(query, mode)
		filename = self.folder[mode] + filename

		if data == False:
			if os.path.isfile(filename):
				if check == True:
					return True
				else:
					with codecs.open(filename, "r") as f:
						d = json.load(f)
						f.close()
						return d
			return False
		else:
			with codecs.open(filename, "w") as f:
				d = f.write(json.dumps(data))
				f.close()
			return True	

	def form(self, word, data = False, check = False):
		return self.cache(word, "form", data, check)

	def sentence(self, sentence, data = False, check = False):
		"""	Return a boolean given the functionnality asked: can either check if cache is available, retrieve or write cache

		Keyword arguments:
		sentence --- A string 
		data --- If false, will retrieve or check if cache exists, if set, will write cache
		check --- if data is false and check is true (default), will only check if a cached version of the sentence is available
		"""
		return self.cache(sentence, "sentence", data, check)

	def search(self, query, data = False, check = False):
		"""	Return a boolean given the functionnality asked: can either check if cache is available, retrieve or write cache

		Keyword arguments:
		query --- A query dictionary
		data --- If false, will retrieve or check if cache exists, if set, will write cache
		check --- if data is false and check is true (default), will only check if a cached version of the sentence is available
		"""
		return self.cache(query, "search", data, check)