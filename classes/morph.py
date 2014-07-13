#!/usr/bin/python
# -*- coding: utf-8 -*-


#Python CORE
import sys
import re
import json
from string import digits

#Python Libraries
from xml.etree.cElementTree import iterparse
from progressbar import ProgressBar, Counter, Timer
import requests

#Shared class through Clotho
from classes.SQL import SQL
from classes.cache import Cache

#Specific class

class Morph(object):
	def __init__(self):
		self.s = SQL()
		self.widget = ['Words processed: ', Counter(), ' ( ', Timer() , ' )']
		self.pbar = False
		self.processed = 0
		#
		self.web = True	#If set to true, use perseids database instead, crawling json
		self.cache = Cache()

		#Roman numeral regExp
		romanNumeral = "^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"
		self.num = re.compile(romanNumeral)

		self.r = requests

	def perseid(self, lemma):
		"""	Returns a lemma according to perseid morphology service
		***HIGHLY EXPERIMENTAL, use with care***


		"""
		url = "http://services.perseids.org/bsp/morphologyservice/analysis/word?word=" + lemma +"&lang=lat&engine=morpheuslat"
		headers = {
			'content-type': 'application/json',
			'accept' : 'application/json, text/javascript'
		}
		j = []
		r = self.r.get(url, headers=headers)
		r.raise_for_status()
		try:
			j = json.loads(r.text)
		except:
			print "Perseid returned unreadable json"
			print r.text
			sys.exit()

		if u'Body' in j[u'RDF'][u'Annotation']:
			responseBody = j[u'RDF'][u'Annotation'][u'Body']
			if isinstance(responseBody, list):
				ret = []
				for item in responseBody:
					try:
						ret.append(item[ u'rest'][u'entry'][u'dict'][u'hdwd'][u'$'].translate({ord(c): None for c in digits}))
					except:
						print item
						continue
				return ret
			else:
				try:
					return [j[u'RDF'][u'Annotation'][u'Body'][ u'rest'][u'entry'][u'dict'][u'hdwd'][u'$'].translate({ord(c): None for c in digits})]
				except:
					return []
		else:
			return []
		#http://services.perseids.org/bsp/morphologyservice/analysis/word?word=vos&lang=lat&engine=morpheuslat

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


	def cleanLemma(self, r):
		if r == None:
			return None
		if r[0]:
			l = r[0].split(u"#")[0]
		else:
			l = None
		if r[1] == None:
			return [l, None]
		else:
			return [l, r[1]]

	def cleanDuplicate(self, data):
		exist = []
		ret = []
		for d in data:
			if d[0] not in exist:
				exist.append(d[0])
				ret.append(d)
		return ret

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
			if self.web == True:
				#Check if cache exist
				data = self.cache.form(form)
				if data != False:
					return [[d, None] for d in data]

				#if not, check perseid
				data = self.perseid(form)

				#If we got data, cache it and return it
				if len(data) > 0:
					self.cache.form(form, data = data)
					return [[d, None] for d in data]
				else:
					self.cache.form(form, data = [])
			with self.s.con:
				cur = self.s.con.cursor()

				req = cur.execute("SELECT morph.lemma_morph, hib_entities.entity_type FROM morph LEFT JOIN hib_entities ON (hib_entities.display_name = morph.lemma_morph AND hib_entities.entity_type != \"Lemma\") WHERE form_morph= %s ", [form])
				rows = cur.fetchall()
				data = []

				for row in rows:
					r = list(row)
					data.append(self.cleanLemma(r))

				if isinstance(data, list):
					self.cleanDuplicate(data)

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
