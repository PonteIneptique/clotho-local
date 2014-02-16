#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
try:
	from bs4 import BeautifulSoup
except:
	print "BS not installed"
	sys.exit()

try:
	import classes.SQL as SQL
except:
	print "Error importing MYSQL tool"
	sys.exit()

try:
	import classes.morph as Morph
except:
	print "Error importing MYSQL tool"
	sys.exit()

try:
	from  nltk.tokenize import word_tokenize, sent_tokenize
except:
	print "Unable to import nltk.tokenize"
	sys.exit()

class Text(object):
	def __init__(self):
		print "Loading text"
		self.sql = SQL.SQL()
		self.m = Morph.Morph()
		self.learning = {}
		self.dots = "".join([',', '.', '...', '"', "'", ':', ';', '!', '?'])

		f = open("./morph/stopwords.txt")
		self.stopwords = f.read().encode("UTF-8").split(",")
		f.close()

	def metadata(self, identifier):
		data , l = self.sql.metadata(identifier[1])
		r = { "identifier" : identifier[1]}

		if l > 0:
			for d in data:
				r[d[0]] = d[1]

		return r

	def path(self, identifier):
		p = "./texts/"

		#Typical data : Perseus:text:2008.01.0558

		identifier = identifier.lower().replace("perseus:text:", "")
		identifier = identifier.split(".")
		p += ".".join(identifier[:2]) + "/" + ".".join(identifier) + ".xml"

		return p

	def lemmatize(self, sentence):
		data = []
		#Cleaning sentence
		sentence = sentence.strip()
		for dot in self.dots:
			sentence = sentence.replace(dot, " ")

		sentence = word_tokenize(sentence)
		for word in sentence:
			word = word.lower()
			if word not in self.stopwords:
				if word not in self.learning:
					m = self.m.morph(word)
					d = [word, m]
					self.learning[word] = m
				else:
					print "Using cache for " + word
					d = [word, self.learning[word]]

				data.append(d)
		

		return data

	def find(self, text, forms):
		sentences = sent_tokenize(text)
		correct = []
		for form in forms:

			i = 0
			while i < len(sentences):
				if form in word_tokenize(sentences[i]):
					correct.append(sentences.pop(i))
				else:
					i += 1

		return correct

	def chunk(self, identifier):
		f = open(self.path(identifier[1]), "rt")
		text = f.read()
		f.close()

		self.text = text;

		return self.section(identifier)

	def section(self, identifier):
		model = BeautifulSoup(identifier[8]+identifier[9])
		tags = model.find_all(True)

		t = BeautifulSoup(self.text)
		div1 = t.find(tags[-1].name, tags[-1].attrs)
		div2 = div1.find(True,{"type" : identifier[3], "n" : identifier[4]})
		if div2:

			return div2.text.encode("UTF-8")
		elif div1:
			return div1.text.encode("UTF-8")

		else:
			print identifier[1]
			print div2
			return ""