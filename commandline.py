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

print "Welcome to Perseus Networkizer"
print "Developed by Thibault Clerice (KCL-ENC)"

goQuery = raw_input("Do you want to make a new query ? y/n ")

if goQuery.lower() == "y":
	print q
	q.config()
	q.lemmas()
	#Save
	#q.save()

##############
#
#	Now we have a list of lemma
#
##############

for term in q.q["terms"]:
	print term
	occ, l = s.occurencies(term)
	if l > 0:
		for o in occ:
			d, l = s.chunk(o)
			if l > 0:
				metadata = t.metadata(d)
				print metadata

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