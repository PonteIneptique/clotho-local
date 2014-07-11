#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import codecs 
import json
import hashlib
import os

#Other libraries
from progressbar import ProgressBar, Counter, Timer

#Clotho Classes
from classes.cache import Cache
from classes.initiate import Initiate
from classes.query import Query
from classes.SQL import SQL
from classes.text import Text
from classes.morph import Morph
from classes.results import Results
from classes.export import Export

#Clotho Class opening
init = Initiate()
if init.check() == False:
	if init.initiate() == False:
		print "Unable to initiate the program. Check your rights on this folder."
		sys.exit()

q = Query()
c = Cache()
s = SQL()
t = Text()
m = Morph()
r = Results(cache = True)
modes = ["mysql"]

try:
	import classes.PyLucene as PyL
	if PyL.luceneImport:
		modes.append("lucene")
		luc = PyL.PyLucene()
except:
	print "Lucene is not available"


"""
	Start of the "real" code
"""
q.welcome()

if s.check() == False:
	q.deco()
	print "Setting up your database"
	s.create()
	q.deco()

filename = raw_input("Path to the file? \n ->")
with codecs.open(filename, "r", "utf-8") as f:
	source = json.load(f)
	print "opened"
	f.close()

q.q["name"] = filename
q.q["mode"] = raw_input("Mode (Lemma, Entities)? \n ->")
for data in source:
	q.q["terms"].append(data)

saved = False
if q.process():
	#PROCESS
	terms =  {}
	"""
		terms : {
			term : [
				[form, lemma, text, sentence]
			]
		}
	"""
	terms = {}
	for term in q.q["terms"]:
		print term
		terms[term] = []
		sentences = [item for item in source[term] if "text" in item and len(item["text"]) > 2]
		#For each sentence, we now update terms
		for item in sentences:
			sentence = item["text"]
			lemma = c.sentence(sentence)

			if lemma == False:
				lemma = t.lemmatize(sentence, mode = q.q["mode"], terms = q.q["terms"])
				c.sentence(sentence, data = lemma)
				
			lemma = t.m.filter(lemma, terms = terms, mode = q.q["mode"].lower(), stopwords = t.stopwords)

			for lem in lemma:
				terms[term].append([lem[0], lem[1], item["author"], item["text"]])

	#Caching results
	if c.search(q.q, data = terms) == False:
		print "Unable to cache results. Check your rights on folder /cache/search"

	q.deco()
	if q.saveResults():
		r.clean()
		for term in terms:
			r.save(terms[term])
		print "Results saved"
		saved = True

exportOnGoing = False
#To be done
if saved == True:
	exportOnGoing = True
else:
	jsonExists = c.search(q.q, check = True)
	if jsonExists:
		terms = c.search(q.q)
		exportOnGoing = True
		
		if not c.nodes(q.q, check = True):
			r.clean()
			print "Saving"
			for term in terms:
				r.save(terms[term])
	else:
		print "Cache doesnt exist. Unable to load any data for export"



if exportOnGoing == True:
	e = Export(q.q)
	e.nodification()
	while q.exportResults():
		print "Nodification done"

		exportMean = q.exportMean()


		if exportMean != "mysql":
			if q.cleanProbability():
				e.cleanProbability();

			if exportMean  not in q.exportLemma:
				gephiMode = "sentence"
				if q.exportLinkType() == "lemma":
					gephiMode = "lemma"
					e.lemma(terms = q.q["terms"])
			else:
				e.lemma(terms = q.q["terms"])
			
		if exportMean == "gephi":
			e.gephi(gephiMode)
			print "Export Done"

		elif exportMean == "mysql":
			e.ClothoWeb(terms = terms, query = q.q["terms"])
			print "SQL export done"

		elif exportMean == "d3js-matrix":

			cluster = q.clustering()

			threshold = q.thresholdOne()

			e.D3JSMatrix(threshold = threshold, cluster = cluster)
			filepath = os.path.dirname(os.path.abspath(__file__)) + "/data/D3JS/index.html"
			try:
				import webbrowser
				webbrowser.open("file://"+filepath,new=2)
			except:
				print "File available at " + filepath

		elif exportMean == "semantic-matrix":
			# It is needed for Export.semanticMatrix() to have lemma-lemma links """
			e.semanticMatrix(terms = q.q["terms"])

		elif exportMean == "tfidf-distance":
			# It is needed for Export.semanticMatrix() to have lemma-lemma links """
			e.tfidfDistance(terms = q.q["terms"])

		elif exportMean == "semantic-gephi":
			e.semanticGephi(terms = q.q["terms"])

		elif exportMean == "corpus":
			e.corpus(data = terms)