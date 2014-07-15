#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import codecs 
import json
import os

#Other libraries

#Clotho Classes
from classes import Cache, Initiate, Query, SQL, Text, Morph, Results, Export, PyLucene, Setup

class Clotho(object):
	def __init__(self):
		#Clotho Class opening
		init = Initiate()
		if init.check() == False:
			if init.initiate() == False:
				print "Unable to initiate the program. Check your rights on this folder."
				sys.exit()

		#Import classes
		self.query = Query()
		self.cache = Cache()
		self.sql = SQL()
		self.text = Text()
		self.morph = Morph()
		self.results = Results(cache = True)
		self.setup = Setup()
		self.modes = ["mysql"]

		if PyLucene().lucene:
			self.modes.append("lucene")
			self.PyLucene = PyLucene()

		self.saved = False
		self.exportOnGoing = False
		self.processed = False
		self.query.welcome()
		self.mode = False
		self.terms = {}

		if self.sql.check() == False:
			self.query.deco()
			print "Setting up your database"
			self.sql.create()
			self.query.deco()

	def initiatSetup(self):
		self.query.setupExplanation()
		self.setup.conf["MySQL"]["identifiers"] = self.setup.sqlId()
		self.setup.write()
		self.query.deco()

		#Then the databases' name
		self.setup.dbs()
		self.setup.write()
		self.query.deco()

		#Then the table
		self.query.deco()
		self.setup.tables()
		self.query.deco()

		self.initialOptions()

	def initialOptions(self):
		"""Offers to 
			- Change Setup / Config
			- Do Perseus Query
			- Do JSON Load Query
		"""
		o = self.query.options("What action do you want to perform ?", ["Change Setup / Config", "Do Perseus Query", "Load a previous Perseus Query", "Do JSON Load Query"])

		if o == "Do JSON Load Query":
			self.loadJSON(raw_input("Path for the file : "))
		elif o == "Load a previous Perseus Query":
			self.loadQuery()
		elif o == "Do Perseus Query":
			self.perseusQuery()
		else:
			self.initiatSetup()
		return True

	def loadQuery(self):
		self.query.load()
		self.processPerseus()

	def perseusQuery(self):
		self.query.config()
		self.query.lemmas()
		#Save
		self.query.save()
		self.processPerseus()

	def loadJSON(self, filename = False):
		if not filename and self.filename:
			filename = self.filename
		with codecs.open(filename, "r", "utf-8") as f:
			self.source = json.load(f)
			self.query.q["name"] = filename
			for data in self.source:
				self.query.q["terms"].append(data)
			self.defineMode(False, self.processJson)
			f.close()

	def processPerseus(self):
		print self.query.q
		if self.query.process():
			mode = self.query.databaseMode(self.modes)
			#PROCESS
			terms =  {}
			for term in self.query.q["terms"]:

				#We get the morph
				morphs = self.morph.all(term)

				""" To add morphs ...
				if len(morphs) == 0:
					newmorphs = q.newmorphs(term)
					if len(newmorphs) > 0:
						m.save(newmorphs)
				"""
						
				if mode == "mysql":
					occ, l = self.sql.occurencies(term)
				elif mode == "lucene":
					occ, l = self.PyLucene.occurencies(term, morphs)

				terms[term] = []


				if l > 0:
					for o in occ:
						#Getting the chunk
						if mode == "mysql":
							d, l = self.sql.chunk(o)
						elif mode == "lucene":
							d, l = self.PyLucene.chunk(o)

						#Reading chunk
						section = self.text.chunk(d, mode = mode)
						#Now search for our term
						sentences = self.text.find(section, morphs)
						#For each sentence, we now update terms
						for sentence in sentences:
							lemma = self.cache.sentence(sentence)

							if lemma == False:
								lemma = self.text.lemmatize(sentence, mode = self.query.q["mode"], terms = self.query.q["terms"])
								self.cache.sentence(sentence, data = lemma)
								
							lemma = self.text.m.filter(lemma, terms = terms, mode = self.query.q["mode"], stopwords = self.text.stopwords)

							for lem in lemma:
								terms[term].append([lem[0], lem[1], d, sentence])
			self.cacheProcess(terms)
		else:
			jsonExists =self.cache.search(self.query.q, check = True)
			if jsonExists:
				terms = self.cache.search(self.query.q)
				self.exportOnGoing = True
			else:
				print "Cache doesnt exist. Unable to load any data for export"
				self.initialOptions()
				return True

		self.terms = terms
		self.processed = True

	def processJson(self):
		if self.query.process():
			terms = {}
			for term in self.query.q["terms"]:
				terms[term] = []
				sentences = [item for item in self.source[term] if "text" in item and len(item["text"]) > 2]
				#For each sentence, we now update terms
				for item in sentences:
					sentence = item["text"]
					lemma = self.cache.sentence(sentence)

					if lemma == False:
						lemma = self.text.lemmatize(sentence, mode = self.query.q["mode"], terms = self.query.q["terms"])
						self.cache.sentence(sentence, data = lemma)
						
					lemma = self.text.m.filter(lemma, terms = terms, mode = self.query.q["mode"].lower(), stopwords = self.text.stopwords)

					for lem in lemma:
						terms[term].append([lem[0], lem[1], item["author"], item["text"]])
			self.cacheProcess(terms)
		else:
			jsonExists =self.cache.search(self.query.q, check = True)
			if jsonExists:
				terms = self.cache.search(self.query.q)
				self.exportOnGoing = True
			else:
				print "Cache doesnt exist. Unable to load any data for export"
				self.processJson()
				return True
				
		self.terms = terms
		self.processed = True

	def defineMode(self, mode = False, callback = False):
		if mode ==True:
			self.query.q["mode"] = mode
		else:
			if self.mode == True:
				self.query.q["mode"] = mode
			else:
				self.query.q["mode"] = self.query.mode()

		t = str(type(callback))
		if t== "<type 'instancemethod'>" or t == "<type 'instancemethod'>":
			callback()

	def cacheProcess(self, terms = False):
		if terms == False:
			terms = self.terms
		if self.cache.search(self.query.q, data = terms) == False:
			print "Unable to cache results. Check your rights on folder /cache/search"

	def saveResults(self):
		self.query.deco()
		if self.query.saveResults():
			self.results.clean()
			for term in self.terms:
				self.results.save(self.terms[term])
			self.saved = True

	def preExport(self):
		#To be done
		if self.saved == True:
			self.exportOnGoing = True
		else:				
			if not self.cache.nodes(self.query.q, check = True):
				self.results.clean()
				print "Saving"
				for term in self.terms:
					self.results.save(self.terms[term])
		if self.exportOnGoing:
			self.exportation()

	def exportation(self):
		#Should depend on type of export...
		while self.query.exportResults():
			e = Export(self.query.q, self.query)
			exportMean = self.query.exportMean()
			e.terms = self.terms

			fn = e.options[exportMean]

			if fn["probability"] == 1 or (fn["probability"] == 0 and self.query.cleanProbability()):
				e.cleanProbability()

			if fn["nodification"] == 1 or(fn["nodification"] == 0 and self.query.nodification()):
				e.nodification()

			if fn["nodificationMode"] == True: #ASK
				graphMode = self.query.exportLinkType() 
			elif fn["nodificationMode"] == False: #NEVER
				graphMode = False
			else:
				graphMode = fn["nodificationMode"]

			if graphMode == "lemma":
				e.lemma(terms = self.query.q["terms"])


			fn["function"]()
			print "Export Done"


			if exportMean == "semantic-matrix":
				# It is needed for Export.semanticMatrix() to have lemma-lemma links 
				e.semanticMatrix(terms = self.query.q["terms"])

			elif exportMean == "tfidf-distance":
				# It is needed for Export.semanticMatrix() to have lemma-lemma links
				e.tfidfDistance(terms = self.query.q["terms"])

			elif exportMean == "semantic-gephi":
				e.semanticGephi(terms = self.query.q["terms"])

			elif exportMean == "corpus":
				e.corpus(data = self.terms)

C = Clotho()

cmds = []
if len(cmds) == 0:
	C.initialOptions()

if C.processed == True:
	C.saveResults()

C.preExport()
C.exportation()