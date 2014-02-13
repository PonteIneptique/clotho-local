#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
try:
	from bs4 import BeautifulSoup
except:
	print "BS not installed"
	sys.exit()

try:
	import classes.SQL as SQL
except:
	print "Error importing MYSQL tool"
	sys.exit()

class Text(object):
	def __init__(self):
		print "Loading text"
		self.sql = SQL.SQL()

	def metadata(self, identifier):
		data , l = self.sql.metadata(identifier[1])
		r = { "identifier" : identifier[1]}

		if l > 0:
			for d in data:
				r[d[0]] = d[1]

		return r

	def path(self, identifier):
		print identifier
		p = "../texts/"

		#Typical data : Perseus:text:2008.01.0558

		identifier = identifier.lower().replace("perseus:text:", "")
		identifier = identifier.split(".")
		p += ".".join(identifier[:2]) + "/" + ".".join(identifier) + ".xml"

		return p

	def chunk(self, identifier):
		f = open(self.path(identifier[1]), "rt")
		text = f.read()
		f.close()

		self.text = text;

		self.section(identifier)

	def section(self, identifier):
		print identifier
		model = BeautifulSoup(identifier[8]+identifier[9])
		tags = model.find_all(True)

		print tags[-1]

		t = BeautifulSoup(self.text)
		div1 = t.find(tags[-1].name, tags[-1].attrs)
		div2 = div1.find(True,{"type" : identifier[3], "n" : identifier[4]})
		
		return div2.text.encode("UTF-8")



