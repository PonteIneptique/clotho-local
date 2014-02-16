#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys

try:
	import classes.SQL as SQL
except:
	print "Error importing MYSQL tool"
	sys.exit()

import hashlib

class Export(object):
	def __init__(self):
		self.perseus = SQL.SQL()
		self.results = SQL.SQL(True)
		self.cache = {"lemma" : {}, "sentence" : {}, "form": {}}

	def nodification(self):
		nodes = [] # [id, label, type, document_id]
		edges = []
		with self.results.con:
			cur = self.results.con.cursor()
			cur.execute("SELECT * FROM lemma_has_form")

			rows = cur.fetchall()
			for row in rows:
				#Lemma, Form, Sentence
				lem = "l"+str(row[0])
				frm = "f"+str(row[1])
				sen = "s"+str(row[2])
				#Lemma :
				if row[0] not in self.cache["lemma"]:
					cur.execute("SELECT text_lemma FROM lemma WHERE id_lemma = %s LIMIT 1", [row[0]])
					lemma = cur.fetchone()[0]
					self.cache["lemma"][row[0]] = lemma
					nodes.append([lem, self.cache["lemma"][row[0]], "lemma", "Null"])

				#Sentence :
				if row[2] not in self.cache["sentence"]:
					cur.execute("SELECT text_sentence, id_document FROM sentence WHERE id_sentence = %s LIMIT 1", [row[2]])
					sentence = cur.fetchone()
					self.cache["sentence"][row[2]] = sentence
					nodes.append([sen, self.cache["sentence"][row[2]], "sentence", sentence[1]])

				#Form :
				if row[1] not in self.cache["form"]:
					cur.execute("SELECT text_form FROM form WHERE id_form = %s LIMIT 1", [row[1]])
					form = cur.fetchone()[0]
					self.cache["form"][row[1]] = form
					nodes.append([frm, self.cache["form"][row[1]], "form", "Null"])

				#We add two edges : lemma -> sentence; lemma -> form
				#We presume that a vote has been made and only form = 1 lemma
				edges.append([lem, sen, "lemma-sentence"])
				edges.append([lem, frm, "lemma-form"])

		self.nodes = nodes
		self.edges = edges

	def lemma(self):
		nodes = [node[0:2] for node in self.nodes if node[2] == "lemma"]
		ed = [edge for edge in self.edges if edge[2] == "lemma-sentence"]
		edges = []
		existing = []

		for e in ed:
			same = [row for row in ed if row[0] != e[0] and row[1] == e[1]]
			for edge in same:
				edg = [e[0], edge[0]]
				h1 = hashlib.md5("".join([e[0], edge[0], edge[1]])).hexdigest()
				h2 = hashlib.md5("".join([e[0], edge[0], edge[1]])).hexdigest()
				if h1 not in existing and h2 not in existing:
					edges.append(edg)
					existing.append(h1)

		self.nodes = nodes
		self.edges = edges




	def gephi(self, mode="sentence"):
		separator = "\t"
		if mode == "lemma":
			nodesColumn = ["id", "label"]
			edgesColumn = ["target", "source"]
		else:
			nodesColumn = ["id", "label", "type", "document"]
			edgesColumn = ["target", "source", "type"]

		f = open("./data/nodes.csv", "wt")
		f.write(separator.join(nodesColumn)+"\n")
		for node in self.nodes:
			f.write(separator.join([str(n).encode("UTF-8").replace("\\n", " ").replace("\t", " ") for n in node])+"\n")
		f.close()

		f = open("./data/edges.csv", "wt")
		f.write(separator.join(edgesColumn)+"\n")
		for edge in self.edges:
			f.write(separator.join([str(e).encode("UTF-8") for e in edge])+"\n")
		f.close()



e = Export()
e.nodification()
e.lemma()
e.gephi("lemma")