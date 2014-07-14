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
		#self.morph = Morph()
		self.results = Results(cache = True)
		self.setup = Setup()
		self.modes = ["mysql"]

		if PyLucene().lucene:
			self.modes.append("lucene")
			self.luc = PyLucene()

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
		o = self.query.options("What action do you want to perform ?", ["Change Setup / Config", "Do Perseus Query", "Do JSON Load Query"])

		if o == "Do JSON Load Query":
			self.loadJSON(raw_input("Path for the file : "))
		elif o == "Do Perseus Query":
			self.perseusQuery()
		else:
			self.initiatSetup()
		return True

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
				
		self.terms = terms
		self.processed = True

	def defineMode(self, mode = False, callback = False):
		if mode ==True:
			self.query.q["mode"] = mode
		else:
			if self.mode == True:
				self.query.q["mode"] = mode
			else:
				self.query.q["mode"] = self.query.options("Mode :", ["Lemma", "Exempla"])

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
				for term in terms:
					self.results.save(terms[term])
		if self.exportOnGoing:
			self.exportation()

	def exportation(self):
		#Should depend on type of export...
		e = Export(self.query.q)
		e.nodification()
		while self.query.exportResults():
			print "Nodification done"

			exportMean = self.query.exportMean()


			if exportMean != "mysql":
				if self.query.cleanProbability():
					e.cleanProbability();

				if exportMean  not in self.query.exportLemma:
					gephiMode = "sentence"
					if self.query.exportLinkType() == "lemma":
						gephiMode = "lemma"
						e.lemma(terms = self.query.q["terms"])
				else:
					e.lemma(terms = self.query.q["terms"])
				
			if exportMean == "gephi":
				e.gephi(gephiMode)
				print "Export Done"

			elif exportMean == "mysql":
				e.ClothoWeb(terms = self.terms, query = self.query.q["terms"])
				print "SQL export done"

			elif exportMean == "d3js-matrix":
				cluster = self.query.clustering()
				threshold =self.query.thresholdOne()
				e.D3JSMatrix(threshold = threshold, cluster = cluster)
				filepath = os.path.dirname(os.path.abspath(__file__)) + "/data/D3JS/index.html"
				try:
					import webbrowser
					webbrowser.open("file://"+filepath,new=2)
				except:
					print "File available at " + filepath

			elif exportMean == "semantic-matrix":
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