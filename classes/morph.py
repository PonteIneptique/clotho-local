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

try:
	from progressbar import ProgressBar, Counter, Timer
except:
	print "Error importing progress bar "
	sys.exit()


class Morph(object):
	def __init__(self):
		self.s = SQL.SQL()
		self.widget = ['Words processed: ', Counter(), ' ( ', Timer() , ' )']
		self.pbar = False
		self.processed = 0

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
		if self.pbar == False:
			self.pbar = ProgressBar(widgets=self.widget, maxval=100000).start()

		with self.s.con:
			cur = self.s.con.cursor()

			req = cur.execute("SELECT morph.lemma_morph, hib_entities.entity_type FROM morph LEFT JOIN hib_entities ON (hib_entities.display_name = morph.lemma_morph AND hib_entities.entity_type != \"Lemma\") WHERE form_morph= %s ", [form])
			rows = cur.fetchall()
			data = [list(row) for row in rows]

			#Update Progress bar
			self.processed += 1
			self.pbar.update(self.processed)

			#Returning data
			return data
	
	def filter(self, form, data, safemode="", terms = []):
		#If we have no lemma corresponding to lemma
		if len(data) == 0:
			#But if it has a caps as first letter and safemode is off
			if form[0].isupper():# and safemode == False:
				#Just to be sure, if form has a caps, we ensure that it is sent back
				return []
			else:
				#If there is no caps first letter return false
				return False
		#If we do have data
		else:
			#We filter by != None
			personna = [row for row in data if row[1] != None]
			if len(personna) == 0:
				data = [row for row in data if row[0] in terms]
				if len(data) == 0:
					return False
				else:
					return data
			else:
				return personna


