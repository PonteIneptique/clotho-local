#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys 
sys.path.append("../..")

from common import Model
import Data.Models
import nltk


#Data.Models.lang.Lemma()
#Data.Models.documents.Occurence()
class Sentence(Model):

	def __init__(self):
		self.mode = "Sentence"

	def strip(self, occurence, lemma):
		sentences = nltk.tokenize.sent_tokenize(occurence.text)
		correct = []

		i = 0
		while i < len(sentences):
			#Last condition ensure that sentences has not been processed
			if form in nltk.tokenize.word_tokenize(sentences[i]) and sentences[i] not in self.processed:
				self.processed.append(sentences[i])
				correct.append(sentences.pop(i))
			else:
				i += 1
		return correct