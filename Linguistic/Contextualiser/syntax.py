#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys 
import inspect
sys.path.append("../..")

import nltk
from Linguistic.Contextualiser.common import Model as Contextualiser
from Linguistic.Contextualiser.common import Dots as DotsList
from Linguistic.Lemma.form import Lemmatizer as FormFinder

class WordWindow(Contextualiser):

	def __init__(self, n = 4, FormFinderClass = None):
		self.n = n

		if inspect.isclass(FormFinderClass) and issubclass(FormFinderClass, FormFinder):
			self.FormFinder = FormFinderClass()
		elif isinstance(FormFinderClass, FormFinder):
			self.FormFinder = FormFinderClass
		else:
			raise TypeError("FormFinder is not a Form.Finder object or subsclass")


	def strip(self, occurence, lemma):
		#<- Setting up context
		lemma.forms = self.FormFinder.getForms(lemma)
		sentences = [w for w in nltk.tokenize.word_tokenize(occurence.text) if w not in DotsList]
		correct = []
		
		#->

		#<- Get the index where we have an occurence
		for i, j in enumerate(sentences):
			if j in lemma.getFormStringList():
				correct.append(sentences[max(i - self.n, 0):min(i + self.n + 1, len(sentences) -1)])
				#(i - self.n) takes n tokens but i + self.n takes only (n - 1) tokens as one of them is sentences[i]
				
		#->

		#<- Get the text
		#->
		

		# <- Converting to occurences
		occurences = [occurence for sentence in correct]
		i = 0
		while i < len(occurences):
			occurences[i].text = " ".join(correct[i])
			i += 1
		# -> End of conversion

		return occurences
