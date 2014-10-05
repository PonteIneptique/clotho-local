#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys 
import inspect
sys.path.append("../..")

from Linguistic.Contextualiser.common import Model as Contextualiser
from Linguistic.Lemma.form import Lemmatizer as FormFinder
import Data.Models
import nltk

class Sentence(Contextualiser):

	def __init__(self, n = None, FormFinderClass = None):
		#Legacy, should be dropped
		self.processed = None

		if inspect.isclass(FormFinderClass) and issubclass(FormFinderClass, FormFinder):
			self.FormFinder = FormFinderClass()
		elif isinstance(FormFinderClass, FormFinder):
			self.FormFinder = FormFinderClass
		else:
			raise TypeError("FormFinder is not a FormFinder object or subsclass")

	def strip(self, occurence, lemma):
		#<- Setting up context
		lemma.forms = self.FormFinder.getForms(lemma)
		sentences = nltk.tokenize.sent_tokenize(occurence.text)
		correct = []
		#->

		# <- Finding answer with text
		i = 0
		while i < len(sentences):
			words = nltk.tokenize.word_tokenize(sentences[i])
			#Last condition ensure that sentences has not been processed
			if len([word for word in words if word.encode("utf-8") in lemma.getFormStringList()]) > 0:
				correct.append(sentences[i])

			i += 1
		# -> 

		# <- Converting to occurences
		occurences = [occurence for sentence in correct]
		i = 0
		while i < len(occurences):
			occurences[i].text = correct[i]
			i += 1
		# -> End of conversion

		return occurences