#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import codecs 
import json
import hashlib
import os

modes = ["mysql"]
try:
	import classes.query as Q
	q = Q.Query()
except:
	print "Unable to load Query dependency"
	sys.exit()

try:
	import classes.SQL as S
	s = S.SQL()
except:
	print "Unable to load SQL dependency"
	sys.exit()
try:
	import classes.text as T
	t = T.Text()
except:
	print "Unable to load Text dependency"
	sys.exit()

try:
	import classes.morph as M
	m = M.Morph()
except:
	print "Unable to load Morphology dependency"
	sys.exit()

try:
	import classes.results as R
	r = R.Results()
except:
	print "Unable to load Results dependency"
	sys.exit()

try:
	import classes.export as Export
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
					lemma = t.lemmatize(sentence, q.q["mode"], q.q["terms"])

					#CACHING FOR TEST
					"""
					name = "./cache/" + hashlib.md5(sentence).hexdigest() + ".json"
					with codecs.open(name, "w") as f:
						f.write(json.dumps(lemma))
						f.close()
					"""


					for lem in lemma:
						terms[term].append([lem[0], lem[1], d[1], sentence])

	pbar.finish()

	q.deco()
	if q.saveResults():
		r.clean()
		for term in terms:
			r.save(terms[term])
		print "Results saved"
		saved = True

#To be done
if saved == True or q.alreadySaved() == True:
	if q.exportResults():
		e = Export.Export()
		e.nodification()
		print "Nodification done"

		if q.cleanProbability():
			e.cleanProbability();

		gephiMode = "sentence"
		if q.exportLinkType() == "lemma":
			gephiMode = "lemma"
			e.lemma(terms = q.q["terms"])
			print "Link Lemma->Form->Sentence transformed to Lemma1->Lemma2 if Lemma1 and Lemma2 share a same sentence"


		exportMean = q.exportMean()
		if exportMean == "gephi":
			e.gephi(gephiMode)
			print "Export Done"
		elif exportMean == "d3js-matrix":
			e.D3JSMatrix()
			filepath = os.path.dirname(os.path.abspath(__file__)) + "/data/index.html"
			try:
				import webbrowser
				webbrowser.open("file://"+filepath,new=2)
			except:
				print "File available at " + filepath