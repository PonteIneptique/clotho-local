#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import codecs

class Corpus(object):
	def __init__(self, data = {}, flexed = False):
		self.folder = "./data/corpus/"
		outputDictionary = {}
		if flexed:
			for term in data:
				outputDictionary[term] = " ".join([word[0] for word in data[term]])
		else:
			for term in data:
				outputDictionary[term] = []
				for word in data[term]:
					for w in word[1]:
						outputDictionary[term].append(w[0])

		for term in outputDictionary:
			outputDictionary[term] = " ".join(outputDictionary[term])
			with codecs.open("./data/corpus/" + term + ".txt", "w") as f:
				f.write(outputDictionary[term]);
				f.close()
				