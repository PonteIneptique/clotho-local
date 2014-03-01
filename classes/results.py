#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys

try:
	import classes.SQL as SQL
except:
	print "MySQL Class not available"
	sys.exit()

class Results(object):
	def __init__(self, cache = False, web = False):
		self.s = SQL.SQL(cache = cache, web = web)
		self.con = self.s.con
		self.saved = {"lemma" : {}, "sentence" : {}, "form": {}}

	def lemma(self, lemma):
		if lemma[0] in self.saved["lemma"]:
			return self.saved["lemma"][lemma[0]]
		else:
			with self.con:
				cur = self.con.cursor()
				cur.execute("SELECT id_lemma FROM lemma WHERE text_lemma = %s LIMIT 1", [lemma[0]])
				d = cur.fetchone()

				if d != None:
					if len(d) == 1:
						return d[0]
				else:
					cur.execute("INSERT INTO lemma (text_lemma, type_lemma) VALUES (%s, %s)", [lemma[0],lemma[1]])
					r = self.con.insert_id()
					self.saved["lemma"][lemma[0]] = r
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

	def sentence(self, sentence, text = False, boolean = False):
		if sentence in self.saved["sentence"]:
			if boolean:
				return True
			else:
				return self.saved["sentence"][sentence]
		else:
			with self.con:
				cur = self.con.cursor()
				if text:
					cur.execute("SELECT id_sentence FROM sentence WHERE text_sentence = %s AND id_document = %s LIMIT 1", [sentence, text])
				else:
					cur.execute("SELECT id_sentence FROM sentence WHERE text_sentence = %s LIMIT 1", [sentence])

				d = cur.fetchone()

				if d != None:
					if len(d) == 1:
						if boolean:
							return True
						else:
							return d[0]
				else:
					if boolean:
						return False
					else:
						if text:
							cur.execute("INSERT INTO sentence (text_sentence, id_document) VALUES ( %s, %s )", [sentence, text])
						else:
							cur.execute("INSERT INTO sentence (text_sentence) VALUES ( %s )", [sentence])
						r = self.con.insert_id()
						self.saved["sentence"][sentence] = r
						return r

	def load(self, sentence):
		with self.con:
			d = {}
			cur = self.con.cursor()
			cur.execute("SELECT f.text_form, l.text_lemma, l.type_lemma FROM lemma_has_form lf, form f, lemma l WHERE l.id_lemma = lf.id_lemma AND f.id_form = lf.id_form AND lf.id_sentence = %s", [sentence])
			rows = cur.fetchall()

			for row in rows:
				if row[0] not in d:
					d[row[0]] = []
				d[row[0]].append([row[1], row[2]])

			return [[form, d[form]] for form in d]

	def clean(self):
		"""
			Clean the table or create them

		"""
		operations = [
			'CREATE TABLE IF NOT EXISTS form (    id_form int(11) NOT NULL AUTO_INCREMENT,    text_form varchar(255) DEFAULT NULL,    PRIMARY KEY (id_form))  ENGINE=InnoDB DEFAULT CHARSET=utf8;'
			'CREATE TABLE IF NOT EXISTS lemma (    id_lemma int(11) NOT NULL AUTO_INCREMENT,    text_lemma varchar(255) DEFAULT NULL,    type_lemma varchar(45) DEFAULT NULL,    PRIMARY KEY (id_lemma))  ENGINE=InnoDB DEFAULT CHARSET=utf8;',
			'CREATE TABLE IF NOT EXISTS lemma_has_form (    id_lemma int(11) NOT NULL,    id_form int(11) NOT NULL,    id_sentence int(11) DEFAULT NULL,    KEY lhf_lemma (id_lemma),    KEY lhf_form (id_form),    KEY lhf_sentence (id_sentence))  ENGINE=InnoDB DEFAULT CHARSET=utf8;',
			'CREATE TABLE IF NOT EXISTS sentence (    id_sentence int(11) NOT NULL AUTO_INCREMENT,    text_sentence text,    id_document varchar(255) DEFAULT NULL,    PRIMARY KEY (id_sentence))  ENGINE=InnoDB DEFAULT CHARSET=utf8;',
			'TRUNCATE TABLE form;',
			'TRUNCATE TABLE lemma;',
			'TRUNCATE TABLE sentence;',
			'TRUNCATE TABLE lemma_has_form;'
		]
		with self.con:
			for op in operations:
				try:
					cur = self.con.cursor()
					cur.execute(op)
					cur.close()
				except:
					log = op

	def relationship(self, sentence, form, lemma):
		with self.con:
			cur = self.con.cursor()
			cur.execute("INSERT INTO `lemma_has_form` (`id_lemma`,`id_form`,`id_sentence`)VALUES(%s, %s, %s)", [lemma,form,sentence])
			return True

	def save(self, rows):
		#
		#	rows = [
		#		[form, lemma, text, sentence]
		#	]
		#
		for row in rows:
			if row[1] != False:
				if len(row[1]) == 0:
					s = self.sentence(row[3], row[2])
					l = 0
					f = self.form(row[0])

					self.relationship(s,f,l)
				else:
					for lemma in row[1]:

						s = self.sentence(row[3], row[2])
						l = self.lemma(lemma)
						f = self.form(row[0])

						self.relationship(s,f,l)

