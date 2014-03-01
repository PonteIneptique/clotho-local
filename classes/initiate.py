#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import os

try:
	from classes.morph import Morph
except:
	print "Unable to load morph class"
	sys.exit()

class Initiate(object):
	def __init__(self):
		self.z = True

	def check(self):

		if os.path.exists("./cache/sentence") == False:
			os.mkdir("./cache/sentence")

		if os.path.exists("./cache/search") == False:
			os.mkdir("./cache/search")

		if os.path.exists("./data/gephi") == False:
			os.mkdir("./data/gephi")

		if os.path.exists("./data/D3JS") == False:
			os.mkdir("./data/D3JS")

		if os.path.exists("./data/MySQL") == False:
			os.mkdir("./data/MySQL")

		M = Morph()
		if M.check() == False:
			M.install()

		return True