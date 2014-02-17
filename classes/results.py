#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys

try:
	import classes.SQL as SQL
except:
	print "MySQLdb not installed. \n apt-get install python-mysqldb"
	sys.exit()

class Results(object):
	def __init__(self):
		self.s = SQL.SQL()
		self.con = self.s.resConnection()
		self.saved = {"lemma" : {}, "sentence" : {}, "form": {}}

	def lemma(self, lemma):
		if lemma in self.saved["lemma"]:
			return self.saved["lemma"][lemma]
		else:
			with self.con:
				cur = self.con.cursor()
				cur.execute("SELECT id_lemma FROM lemma WHERE text_lemma = %s LIMIT 1", [lemma])
				d = cur.fetchone()

				if d != None:
					if len(d) == 1:
						return d[0]
				else:
					cur.execute("INSERT INTO lemma (text_lemma) VALUES (%s)", [lemma])
					r = self.con.insert_id()
					self.saved["lemma"][lemma] = r
					return r

	def form(self, form):
		if form in self.saved["form"]:
			return self.saved["form"][form]
		else:
			with self.con:
				cur = self.con.cursor()
				cur.execute("SELECT id_form  FROM form WHERE text_form = '" + form + "'")
				d = cur.fetchone()

				if d != None:
					if len(d) == 1:
						return d[0]
				else:
					cur.execute("INSERT INTO form (text_form) VALUES ('" + form + "')")
					r = self.con.insert_id()
					self.saved["form"][form] = r
					return r

	def sentence(self, sentence, text):
		if sentence in self.saved["sentence"]:
			return self.saved["sentence"][sentence]
		else:
			print sentence
			with self.con:
				cur = self.con.cursor()
				cur.execute("SELECT id_sentence FROM sentence WHERE text_sentence = %s AND id_document = %s LIMIT 1", [sentence, text])
				d = cur.fetchone()

				if d != None:
					if len(d) == 1:
						return d[0]
				else:
					cur.execute("INSERT INTO sentence (text_sentence, id_document) VALUES ( %s, '" + text + "')", [sentence])
					r = self.con.insert_id()
					self.saved["sentence"][sentence] = r
					return r

	def relationship(self, sentence, form, lemma):
			with self.con:
				cur = self.con.cursor()
				cur.execute("INSERT INTO `results`.`lemma_has_form` (`id_lemma`,`id_form`,`id_sentence`)VALUES(%s, %s, %s)", [lemma,form,sentence])
				return True

	def save(self, rows):
		#
		#	rows = [
		#		[form, lemma, text, sentence]
		#	]
		#
		for row in rows:
			if row[1] != False:
				for lemma in row[1]:
					s = self.sentence(row[3], row[2])
					l = self.lemma(lemma)
					f = self.form(row[0])

					self.relationship(s,f,l)

