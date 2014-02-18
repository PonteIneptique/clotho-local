#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re

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


	def morph(self, form, mode = "Lemma", safemode = False):
		with self.s.con:
			cur = self.s.con.cursor()

			req = cur.execute("SELECT morph.lemma_morph, hib_entities.entity_type FROM morph LEFT JOIN hib_entities ON (hib_entities.display_name = %s AND hib_entities.entity_type != \"Lemma\") WHERE form_morph= %s ", [form, form.split("#")[0]])
			rows = cur.fetchall()
			data = [list(row) for row in rows]

			if mode == "Lemma":
				return data
			else:
				if len(data) == 0:
					if form[0].isupper() and safemode == False:
						#Just to be sure, if form has a caps, we ensure that it is sent back
						return []
					else:
						return False
				else:
					data = [row for row in data if row[1] != None]
					if len(data) == 0:
						if form[0].isupper():
							#Just to be sure, if form has a caps, we ensure that it is sent back
							return []
						else:
							return False
					else:
						if form[0].isupper() and safemode == False:
							return data
						else:
							return False


