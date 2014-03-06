#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

class Clotho(object):
	def __init__(self, terms = False):
		try:
			from classes.SQL import SQL
			self.sql = SQL(web=True)
			self.con = self.sql.con

			self.origin = SQL()

		except:
			print "Unable to load SQL dependecy"
		self.terms = terms
		self.saved = {"lemma" : {}, "sentence" : {}, "form": {}}
		self.url = {"thesaurus" : "http://www.perseus.tufts.edu/hopper/"}
		self.pythonUser = 1
		self.edges = []

	def save(self):

		#First save every form , sentence, lemma
		#Then save their relationships
		#In the same time, we do some kind of nice thesaurus config
		for term in self.terms:
			self.query(self.terms[term])

		#So now, we kind of need the vote for lemma isn't it ?
		#Then save their vote	def lemma(self, lemma):
		self.form_vote()

		#Then we save the metadata:
		self.metadata()

	def metadata(self):
		with self.con:
			cur = self.con.cursor()
			cur.execute("SELECT id_document FROM sentence GROUP BY id_document")
			documents = [str(row[0]) for row in cur.fetchall()]
			documents = list(set(documents))
		with self.origin.con:
			cur2 = self.origin.con.cursor()
			for document in documents:
				cur2.execute("SELECT * FROM metadata WHERE document_id = %s ", [document])
				meta = cur2.fetchall()
				for data in meta:
					cur.execute("INSERT INTO metadata VALUES ( %s , %s , %s , %s , %s , %s , %s )", list(data))



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
					cur.execute("INSERT INTO lemma (text_lemma) VALUES (%s)", [lemma[0]])
					r = self.con.insert_id()
					self.saved["lemma"][lemma[0]] = r

					if lemma[1] != None:
						self.thesaurus(r, lemma[1], vote = True)
					return r

	def thesaurus(self, id_lemma, name_thesaurus, vote = False):
		with self.con:
			cur = self.con.cursor()
			cur.execute("INSERT INTO thesaurus (id_lemma, url_thesaurus, name_thesaurus) VALUES ( %s , %s , %s ) ", [id_lemma, self.url["thesaurus"], name_thesaurus])
			r = self.con.insert_id()
			if vote == True:
				self.thesaurus_vote(r)


	def thesaurus_vote(self, id_thesaurus):
		with self.con:
			cur = self.con.cursor()
			cur.execute("INSERT INTO thesaurus_vote (id_thesaurus, id_user, value) VALUES ( %s , %s , %s ) ", [id_thesaurus, self.pythonUser, 1])

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
		
	def relationship(self, sentence, form, lemma):
		with self.con:
			cur = self.con.cursor()
			cur.execute("INSERT INTO `lemma_has_form` (`id_lemma`,`id_form`,`id_sentence`)VALUES(%s, %s, %s)", [lemma,form,sentence])
			#edg = self.con.insert_id()


			self.edges.append([form, sentence, "form-sentence"])
			self.edges.append([lemma, form, "lemma-form"])

			return True

	def query(self, rows):
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


	"""
	def nodification(self):
		nodes = [] # [id, label, type, document_id]
		edges = []

		cache = {"lemma" : [], "sentence" : [], "form": []}
		with self.con:
			cur = self.con.cursor()
			cur.execute("SELECT id_lemma, id_form, id_sentence, id_lemma_has_form FROM lemma_has_form")

			rows = cur.fetchall()
			for row in rows:
				#Lemma, Form, Sentence
				lem = row[0]
				frm = row[1]
				sen = row[2]
				edg = row[3]

				I think it is not useful
				#Lemma :
				if lem not in cache["lemma"]:
					nodes.append([lem, "lemma"])
				else:
					cache["lemma"].append(lem)
				if sen not in cache["form"]:
					nodes.append([sen, "sentence"])
				else:
					cache["lemma"].append(lem)
				if frm not in cache["form"]:
					nodes.append([frm, "form"])

				edges.append([frm, sen, "form-sentence", edg])
				edges.append([lem, frm, "lemma-form", edg])

		self.edges = edges
	"""

	def form_vote_sql(self, edges):
		with self.con:
			cur = self.con.cursor()
			for edge in edges:
				lemma = edge[0]
				form = edge[1]

				query = cur.execute("SELECT id_lemma_has_form FROM lemma_has_form WHERE id_lemma = %s AND id_form = %s ", [lemma, form])
				datas = cur.fetchall()
				for data in datas:
					id_form_vote = int(data[0])
					query2 = cur.execute("INSERT INTO form_vote (id_lemma_has_form, id_user, value) VALUES ( %s , %s ,  %s )", [id_form_vote, self.pythonUser, 1])

		return True

	def form_vote(self):
		compute = {"lemma" : {}, "form": {}}
		#We build an index
		for edge in self.edges:
			if edge[2] == "lemma-form":
				#Lemma
				lemma = str(edge[0])
				if lemma not in compute["lemma"]:
					compute["lemma"][lemma] = []
				#Form
				form = str(edge[1])
				if form not in compute["form"]:
					compute["form"][form] = []

				compute["lemma"][lemma].append(edge[1])
				compute["form"][form].append(edge[0])

		#We give to our edges the one which are not lemma-form AND the one which have only one possibility
		newcompute = {}
		#Then we need to find a way to compute stuff isn't it ?
		#Basically, we want the one with the biggest compute[lemma] in compute[form]

		for form in compute["form"]:
			f = str(form)
			if len(compute["form"][f]) > 1:
				Max = float(0)
				MaxId = str(0)
				for lemma in compute["form"][f]:
					l = str(lemma)
					computed = float(0)
					for other_form in compute["lemma"][l]:
						of = str(other_form)
						computed += float(1 / float(len(compute["form"][of])))
					if MaxId == 0 or computed > Max:
						MaxId = l
						Max = computed
				newcompute[f] = [MaxId]
			else:
				newcompute[f] = compute["form"][f]

		edges = [[newcompute[edge][0], edge] for edge in newcompute]

		self.form_vote_sql(edges)

		return True
