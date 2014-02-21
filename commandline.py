#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

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
		occ, l = s.occurencies(term)

		if pbar != False:
			pbar.finish()
		pbar = ProgressBar(widgets=widget, maxval=l).start()
		progress = 0

		terms[term] = []

		#We get the morph
		morphs = m.all(term)

		if l > 0:
			for o in occ:
				#Just Viz stuff
				progress += 1
				pbar.update(progress)

				#Getting the chunk
				d, l = s.chunk(o)

				#Reading chunk
				section = t.chunk(d)
				#Now search for our term
				sentences = t.find(section, morphs)
				#For each sentence, we now update terms
				for sentence in sentences:
					lemma = t.lemmatize(sentence, q.q["mode"], q.q["terms"])
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
			e.lemma()
			print "Link Lemma->Form->Sentence transformed to Lemma1->Lemma2 if Lemma1 and Lemma2 share a same sentence"


		exportMean = q.exportMean()
		if exportMean == "gephi":
			e.gephi(gephiMode)
			print "Export Done"

			