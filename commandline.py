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

##############
#
#	Now we have a list of lemma
#
##############

terms =  {}

#
#Structure
#
"""
#	terms = {
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

	"""
	#<Debug
	occ = occ[0:10]
	#Debug>
	"""


	if l > 0:
		for o in occ:
			progress += 1
			pbar.update(progress)
			d, l = s.chunk(o)
			
			"""
			#Metadata retrieving
			if l > 0:
				metadata = t.metadata(d)
				print metadata
				sys.exit()
			"""

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
#Then we save all thos results :
for term in terms:
	r.save(terms[term])
			

"""
chunk, l = test.chunk(occ[0])
"""



#<DEV#
"""
test = Query()
if test.lemmas():
	print test.q

	t = text.Text()
	t.terms = test.q["terms"]
"""
#DEV>#