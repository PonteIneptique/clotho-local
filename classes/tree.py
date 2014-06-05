#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys


class TT(object):
	def __init__(self):
		try:
			self.tt = TreeTagger(encoding='latin-1',language='latin')
		except:
			print "Unable to load latin dependency of treetagger"

t = TT()