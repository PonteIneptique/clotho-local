#!/usr/bin/python
# -*- coding: utf-8 -*-

#Python CORE
import re
import codecs

#Python Libraries
from bs4 import BeautifulSoup
import nltk

#Shared class through Clotho
from classes.SQL import SQL
from classes.results import Results
from classes.morph import Morph

#Specific class

#Python Warning



class Text(object):
	def __init__(self):

		#Instances
		self.sql = SQL()
		self.m = Morph()
		self.r = Results(cache=True)

		self.cache = True


		#Data
		self.learning = {}
		self.dots = "".join([',', '.', '...', '"', "'", ':', ';', '!', '?','-', "(", ")", "[", "]"])
		self.processed = []

		#Processed data
		f = open("./morph/stopwords.txt")
		self.stopwords = f.read().encode("UTF-8").split(",")
		f.close()

		#Reg Exp
		self.regexp = re.compile("Perseus:text:([0-9]{4}\.[0-9]{2}\.[0-9]{4})")


	def BCEtoInt(self, date):
		""" Convert a string identifying a date using the BCE suffix by an int formatted date 

		Keyword arguments:
		date -- a list of string
		"""
		toReturn = []
		for d in date:
			if "BCE" in d:
				d = -1 * int(d.replace("BCE", ""))
			else:
				d = int(d)
			toReturn.append(d)
		return toReturn

	def inDateRange(self, metadata, dateRange):
		""" Return a bolean given the metadata of a text and a given date range

		Keyword arguments:
		metadata -- a set of metadata (dictionary)
		dateRange -- a given date range (tuple of int)
		"""
		dateRecognition = re.compile("([0-9]+(?:BCE)?)(?:\-([0-9]+(?:BCE)?))?")
		if "dc:Date:Created" in metadata:
			date = dateRecognition.search(metadata["dc:Date:Created"]).groups()
			date = BCEtoInt(date)
			if len(date) == 2: #We have here a range for the date of creation so we check if one of the two dates are in our own range
				if (date[0] >= dateRange[0] and date[0] <= dateRange[1]) or (date[1] >= dateRange[0] and date[1] <= dateRange[1]):
					return True
			elif len(date) == 1: #If we have only one date
				if (date[0] >= dateRange[0] and date[0] <= dateRange[1]):
					return True
		return False	#any other situation, including  not aving the metadata should return False

	def metadata(self, identifier):
		""" Returns the metadata for a given text using the MySQL database instead of the XML metadata

		Keyword arguments:
		identifier -- A list of identifier given by Lucene or MYSQL
		"""
		data , l = self.sql.metadata(identifier[1])
		r = { "identifier" : identifier[1]}

		if l > 0:
			for d in data:
				r[d[0]] = d[1]

		return r

	def path(self, identifier):
		""" Define the path of a file given its identifier

		Keyword arguments:
		identifier -- A list of identifier given by Lucene or MYSQL
		"""
		p = "./texts/"
		identifier = self.regexp.search(identifier).group(1)
		#Typical data : Perseus:text:2008.01.0558
		identifier = identifier.split(".")
		p += ".".join(identifier[:2]) + "/" + ".".join(identifier) + ".xml"

		return p

	def find(self, text, forms):
		""" Return a list of sentence given some forms

		Keyword arguments:
		text -- The text in a string format
		forms -- A list of forms corresponding to the declined query lemma
		"""
		sentences = nltk.tokenize.sent_tokenize(text)
		correct = []
		for form in forms:

			i = 0
			while i < len(sentences):
				#Last condition ensure that sentences has not been processed
				if form in nltk.tokenize.word_tokenize(sentences[i]) and sentences[i] not in self.processed:
					self.processed.append(sentences[i])
					correct.append(sentences.pop(i))
				else:
					i += 1
		return correct

	def chunk(self, identifier, mode = "mysql"):
		""" Return the full text given its identifiers

		Keyword arguments:
		identifier -- A list of identifier given by Lucene or MYSQL
		mode -- A string indicating the mode used, as both identifier have different depth and structure
		"""

		if(mode == "mysql"):
			f = codecs.open(self.path(identifier[1]), "r", "UTF-8")
			text = f.read()
			f.close()

			self.text = text;

			return self.section(identifier)
		elif(mode == "lucene"):
			f = codecs.open(self.path(identifier), "r", "UTF-8")
			text = f.read()
			f.close()

			self.text = text;

			return self.section(identifier, mode = mode)


	def section(self, identifier, mode = "mysql"):
		""" Return the BeautifulSoup section/node of a text where an occurence should be found

		Keyword arguments:
		identifier -- A list of identifier given by Lucene or MYSQL
		mode -- A string indicating the mode used, as both identifier have different depth and structure
		"""
		if mode == "mysql":
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
				return ""
		else:
			t = BeautifulSoup(self.text)
			return t.text

	def lemmatize(self, sentence = "", mode = "Lemma", terms = []):
		"""Given a sentence (string), tokenize it into words 
			and return a list with the following structure 
			[form, [list of corresponding [lemma, type of lemma]]]

		Keyword arguments:
		sentence -- A sentence to lemmatize (string)
		mode -- Either Lemma or Auctoritas, will return all corresponding lemma or only those who are proper nouns (default : "Lemma")
		terms -- A list of terms which are our query terms
		"""
		data = []

		cached = False
		#Caching
		#if self.cache == True:
		#	cached = self.r.sentence(sentence, boolean = True)

		if cached:
			print cached
			#Loading Id of this sentence
			S = self.r.sentence(sentence)
			#Loading data
			tempData = self.r.load(S)
			data = []
			#Caching some of this data
			safe = True
			
			for row in tempData:
				m = row[1]
				self.learning[row[0]] = m
				data.append([row[0], m])
				safe = False
		else:
			#Registering sentence
			S = self.r.sentence(sentence)
			#Cleaning sentence
			sentence = sentence.strip()
			for dot in self.dots:
				sentence = sentence.replace(dot, " ")

			sentence = nltk.tokenize.word_tokenize(sentence)
			safe = True
			for word in sentence:

				lower = word.lower()
				if lower not in self.stopwords:
					if word not in self.learning:
						m = self.m.morph(word)

						if m == False:
							d = False
						else:
							if self.cache == True:
								F = self.r.form(word)

								for Lem in m:
									L = self.r.lemma(Lem)

									#Make Link
									self.r.relationship(S, F, L)

							if "Auctoritas" in mode:
								m = self.m.filter(word, m, safe, terms)

							d = [word, m]
							self.learning[word] = m
					else:
						#print "Using cache for " + word
						F = self.r.form(word)

						for Lem in self.learning[word]:
							L = self.r.lemma(Lem)
							self.r.relationship(S, F, L)

						d = [word, self.learning[word]]

					if d != False:
						data.append(d)
				safe = False
		

		return data