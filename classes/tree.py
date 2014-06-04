#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys

try:
	from treetagger import TreeTagger
except:
	print "TreeTagger is not installed or doesn't work properly"
	sys.exit()

class TT(object):
	def __init__(self, terms = [], query_terms = []):
		try:
			self.treetagger = TreeTagger(encoding='latin-1',language='latin')
		except:
			print "Unable to load latin dependency of treetagger"

	