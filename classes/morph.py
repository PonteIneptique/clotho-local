#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

try:
	from xml.etree.cElementTree import iterparse
except:
	print "Unable to load xml.etree.cElementTree"
	sys.exit()

try:
	import classes.SQL as SQL
except:
	print "Error importing MYSQL tool"
	sys.exit()


class Morph(object):
	def __init__(self):
		print "Loading"
		self.s = SQL.SQL()

	def install(self):
		data = {"lemma" : "", "form" : ""}
		i = 0
		for event, elem in iterparse("./morph/latin.morph.xml"):
			if elem.tag == "analysis":
				for child in elem:
					if child.tag == "lemma":
						data["lemma"] = child.text
					elif child.tag == "form":
						data["form"] = child.text
					print child.tag + " = " + child.text
				try:
					self.s.saveMorph(data)
				except:
					continue
		print str(i) + " morph imported in database"

	def all(self,lemma):
		with self.s.con:
			cur = self.s.con.cursor()
			req = cur.execute("SELECT form_morph FROM morph WHERE lemma_morph = '" + lemma + "'")

			rows = cur.fetchall()
			data = []
			for row in rows:
				data.append(row[0])
			return data


	def morph(self, form):
		with self.s.con:
			cur = self.s.con.cursor()
			req = cur.execute("SELECT lemma_morph FROM morph WHERE form_morph = '" + form + "'")

			rows = cur.fetchall()
			data = [row[0] for row in rows]
			return data