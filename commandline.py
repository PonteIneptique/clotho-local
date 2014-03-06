#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import codecs 
import json
import hashlib
import os

try:
	from classes.initiate import Initiate
	init = Initiate()
	if init.check() == False:
		if init.initiate() == False:
			print "Unable to initiate the program. Check your rights on this folder."
			sys.exit()

except:
	print "Unable to initiate the program. Check your rights on this folder."
	sys.exit()

modes = ["mysql"]
try:
	from classes.query import Query
	q = Query()
except:
	print "Unable to load Query dependency"
	sys.exit()

try:
	from classes.SQL import SQL
	s = SQL()
except:
	print "Unable to load SQL dependency"
	sys.exit()
try:
	from classes.text import Text
	t = Text()
except:
	print "Unable to load Text dependency"
	sys.exit()

try:
	from classes.morph import Morph
	m = Morph()
except:
	print "Unable to load Morphology dependency"
	sys.exit()

try:
	from classes.results import Results
	r = Results(cache = True)
except:
	print "Unable to load Results dependency"
	sys.exit()

try:
	from classes.export import Export
except:
	print "Unable to load Export dependency"
	sys.exit()

try:
	from progressbar import ProgressBar, Counter, Timer
except:
	print "Unable to load ProgressBar dependency"
	sys.exit()

try:
	import classes.PyLucene as PyL
	if PyL.luceneImport:
		modes.append("lucene")
		luc = PyL.PyLucene()
except:
	print "Lucene is not available"

try:
	from classes.cache import Cache
	c = Cache()
except:
	print "Unable to load Cache dependency"
	sys.exit()

q.deco()
print "\t\tWelcome to Arachne"
print "\t\tDeveloped by Thibault Clerice (KCL-ENC)"
q.deco()

if s.check() == False:
	q.deco()
	print "Setting up your database"
	s.create()
	q.deco()

goQuery = raw_input("Do you want to make a new query ? y/n \n - ")

if goQuery.lower() == "y":
	q.config()
	q.lemmas()
	#Save
	q.save()

else:
	q.load()

q.deco()

saved = False
if q.process():
	mode = q.databaseMode(modes)
	#PROCESS
	terms =  {}
	"""
		terms = {
			term = [
				[form, lemma, text, sentence]
			]
		}
	"""
	widget = ['Processing ocurrence n°', Counter(), ' ( ', Timer(), ' ) ']
	pbar = False
	terms = {}
	for term in q.q["terms"]:

		#We get the morph
		morphs = m.all(term)

		"""
		if len(morphs) == 0:
			newmorphs = q.newmorphs(term)
			if len(newmorphs) > 0:
				m.save(newmorphs)
		"""
				
		if mode == "mysql":
			occ, l = s.occurencies(term)
		elif mode == "lucene":
			occ, l = luc.occurencies(term, morphs)

		if pbar != False:
			pbar.finish()
		pbar = ProgressBar(widgets=widget, maxval=l).start()
		progress = 0

		terms[term] = []


		if l > 0:
			for o in occ:
				#Just Viz stuff
				progress += 1
				pbar.update(progress)

				#Getting the chunk
				if mode == "mysql":
					d, l = s.chunk(o)
				elif mode == "lucene":
					d, l = luc.chunk(o)

				#Reading chunk
				section = t.chunk(d, mode = mode)
				#Now search for our term
				sentences = t.find(section, morphs)
				#For each sentence, we now update terms
				for sentence in sentences:
					sentence = sentence.encode("UTF-8")
					lemma = c.sentence(sentence)

					if lemma == False:
						lemma = t.lemmatize(sentence, mode = q.q["mode"], terms = q.q["terms"])
						c.sentence(sentence, data = lemma)

					lemma = t.m.filter(lemma, terms = terms, mode = q.q["mode"], stopwords = t.stopwords)

					for lem in lemma:
						terms[term].append([lem[0], lem[1], d, sentence])

	pbar.finish()

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
		r.clean()
		print r.db()
		print "Going to save"
		for term in terms:
			r.save(terms[term])
	else:
		print "Cache doesnt exist. Unable to load any data for export"



if exportOnGoing == True:
	while q.exportResults():
		e = Export()
		e.nodification()
		print "Nodification done"


		exportMean = q.exportMean()


		if exportMean != "mysql":
			if q.cleanProbability():
				e.cleanProbability();

			gephiMode = "sentence"
			if q.exportLinkType() == "lemma":
				gephiMode = "lemma"
				e.lemma(terms = q.q["terms"])
			
		if exportMean == "gephi":
			e.gephi(gephiMode)
			print "Export Done"

		elif exportMean == "mysql":
			e.ClothoWeb(terms = terms)
			print "SQL export done"

		elif exportMean == "d3js-matrix":

			cluster = q.clustering()

			threshold = q.thresholdOne()

			e.D3JSMatrix(threshold = threshold, cluster = cluster)
			filepath = os.path.dirname(os.path.abspath(__file__)) + "/data/index.html"
			try:
				import webbrowser
				webbrowser.open("file://"+filepath,new=2)
			except:
				print "File available at " + filepath