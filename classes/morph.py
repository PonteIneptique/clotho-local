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
	from classes.SQL import SQL
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
		self.s = SQL()
		self.widget = ['Words processed: ', Counter(), ' ( ', Timer() , ' )']
		self.pbar = False
		self.processed = 0

		#Roman numeral regExp
		romanNumeral = "^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"
		self.num = re.compile(romanNumeral)

	def check(self):
		with self.s.con:
			cur = self.s.con.cursor()
			query = cur.execute("SELECT COUNT(*) CNT FROM morph LIMIT 10")
			data = cur.fetchone()
			cur.close()

			if int(data[0]) > 0:
				return True
			else:
				return False
		return False

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
	    """Given the form of a word, returns a list of lemma and their type

	    Keyword arguments:
	    form -- a lemma's form (string)
	    """
		if self.pbar == False:
			self.pbar = ProgressBar(widgets=self.widget, maxval=100000).start()

		if(self.num.search(form)):
			return False
		elif len(form) == 1:
			return False
		else:
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
	
	def filter(self, sentence, mode = "lemma", safemode="", terms = [], stopwords = []):
		returned = []

		#First filter stop words
		for word in sentence:
			keep = []
			for lemma in word[1]:
				sp = lemma[0].split("#")
				sp = sp[0].replace("-", "").lower()
				if sp not in stopwords:
					keep.append(lemma)
			if len(keep) > 0:
				returned.append([word[0], keep])

		if mode == "lemma":
			return returned

		else:
			sentence = returned
			returned = []
			for word in sentence:
				keep = []
				for lemma in word[1]:
					#if lemma[1] != None:
					#print lemma[0] + " | " + lemma[0][0]
					if lemma[0][0].isupper() == True:
						keep.append(lemma)
					elif lemma[0] in terms:
						keep.append(lemma)

				if len(keep) > 0:
					returned.append([word[0], keep])

			return returned
