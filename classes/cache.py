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
			"form" : "./cache/form/",
			"dbpedia" : "./cache/dbpedia/",
			"rdf" : "./cache/rdf/",
			"definition" : "./cache/definition/"
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
		if mode == "rdf":
			return self.hash(sentence, mode = mode) + ".rdf"
		else:
			return self.hash(sentence, mode = mode) + ".json"


	def cache(self, query, mode, data = False, check = False):
		""" Read, write or check if there is a cache for given identifiers

		query -- filename
		mode -- An element from self.folder
		data -- Either a json convertable object,  an instance of file to be written or an instance of requests lib results
		check -- If set to true, only perform a check if cache is available or not.
		"""
		filename = self.filename(query, mode)
		filename = self.folder[mode] + filename

		if data == False:
			if os.path.isfile(filename):
				if check == True:
					if mode == "rdf":
						return filename
					return True
				else:
					with codecs.open(filename, "r", "utf-8") as f:
						d = json.load(f)
						f.close()
						return d
			return False
		else:
			with codecs.open(filename, "w", "utf-8") as f:
				if hasattr(data , "read"):
					d = f.write(data.read())
				elif hasattr(data , "text"):
					d = f.write(data.text)
				else:
					d = f.write(json.dumps(data))
				f.close()
			return True	

	def rdf(self, url, data = False, check = False):
		return self.cache(url, "rdf", data, check)

	def dbpedia(self, url, data = False, check = False):
		return self.cache(url, "dbpedia", data, check)

	def form(self, word, data = False, check = False):
		return self.cache(word, "form", data, check)

	def definition(self, url, data = False, check = False):
		return self.cache(url, "definition", data, check)

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