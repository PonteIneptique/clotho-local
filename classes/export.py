#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import codecs
import hashlib
from pprint import pprint	

try:
	import classes.SQL as SQL
except:
	print "Error importing MYSQL tool"
	#sys.exit()
	

class Export(object):
	def __init__(self):
		self.perseus = SQL.SQL()
		self.results = SQL.SQL(cache = True, web = False)
		self.cache = {"lemma" : {}, "sentence" : {}, "form": {}}


		###Load treetagger if possible
		try:
			from dependencies.treetagger import TreeTagger
			self.tt = TreeTagger(encoding='latin-1',language='latin')
			self.ttAvailable = True
		except:
			self.ttAvailable = False

	def nodification(self):
		nodes = [] # [id, label, type, document_id]
		edges = []
		triples = [] # lemma, form, sentence
		orphans = {"edges" : [], "nodes" : []}
		with self.results.con:
			cur = self.results.con.cursor()
			cur.execute("SELECT * FROM lemma_has_form")

			rows = cur.fetchall()
			for row in rows:
				#Lemma, Form, Sentence
				lem = "l"+str(row[0])
				frm = "f"+str(row[1])
				sen = "s"+str(row[2])
				triples.append([lem, frm, sen])
				#Lemma :
				if row[0] not in self.cache["lemma"]:
					cur.execute("SELECT text_lemma FROM lemma WHERE id_lemma = %s LIMIT 1", [row[0]])
					lemma = cur.fetchone()
					if lemma != None:
						self.cache["lemma"][row[0]] = lemma[0]
						nodes.append([lem, self.cache["lemma"][row[0]], "lemma", "Null"])
					else:
						self.cache["lemma"][row[0]] = None

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

				if self.cache["lemma"][row[0]] == None:
					orphans["edges"].append([frm, sen])
					orphans["nodes"].append([frm, self.cache["form"][row[1]]])
				else:
					edges.append([frm, sen, "form-sentence"])
					edges.append([lem, frm, "lemma-form"])

		self.nodes = nodes
		self.edges = edges
		self.triples = triples
		self.orphans = orphans

	def useTT(self):
		""" Use TreeTagger to improve the probability feature, creating a new dictionnary where the key is the sentence and the value is a list of found lemma
		"""

		#First we need to get last lemma id and get id for each lemma
		ret = {}
		sentences = [node for node in self.nodes if node[2] == "sentence"]
		for sentence in sentences:
			results = self.tt.tag(sentence[1][0].encode('latin-1', "ignore"))
			ret[sentence[0]] = []
			for lemma in [r[2].split("|") for r in results]:
				ret[sentence[0]] += lemma
			ret[sentence[0]] = list(set(ret[sentence[0]]))
		return ret

	def cleanLemma(self, lemma):
		"""	Deletes number "#" from lemma in list of lemma
		"""
		ret = []
		for lem in lemma:
			ret.append(lem.split("#")[0])
		return list(set(ret))

	def cleanProbability(self):
		print self.cache["lemma"]
		if self.ttAvailable == True:
			pass
			#computeEdges = self.edges + self.useTT()
		else:
			computeEdges = self.edges
		edges = []
		compute = {}
		#We build an index
		for edge in self.edges:
			if edge[2] == "lemma-form":
				#Lemma
				if edge[0] not in compute:
					compute[edge[0]] = []
				#Form
				if edge[1] not in compute:
					compute[edge[1]] = []

				compute[edge[0]].append(edge[1])
				compute[edge[1]].append(edge[0])

		#We give to our edges the one which are not lemma-form AND the one which have only one possibility
		edges += [edge for edge in self.edges if edge[2] == "form-sentence"]#(edge[2] == "lemma-form" and len(compute[edge[1]]) <= 1) or 
		newcompute = {}
		#Then we need to find a way to compute stuff isn't it ?
		#Basically, we want the one with the biggest compute[lemma] in compute[form]
		for form in compute: 
			if form[0] == "f":
				compute[form] = self.cleanLemma(compute[form])
				if len(compute[form]) > 1:
					Max = float(0)
					MaxId = str(0)
					for lemma in compute[form]:
						computed = float(0)
						for forms in compute[lemma]:
							computed += float(1 / float(len(compute[forms])))

						if MaxId == 0 or computed > Max:
							MaxId = lemma
							Max = computed
					newcompute[form] = [MaxId]
				else:
					newcompute[form] = compute[form]

		edges2 = [[newcompute[edge][0], edge, "lemma-form"] for edge in newcompute if edge[0] == "f"]

		edges += edges2
		self.edges = edges
		return True

	def hash(self, l):
		l = ";".join(l)
		return hashlib.md5(l).hexdigest()

	def lemma(self, terms = []):
		nodes = [node[0:2] for node in self.nodes if node[2] == "lemma"]
		hashes = [self.hash(edge[0:2]) for edge in self.edges if edge[2] == "lemma-form"]
		done = []
		nodesclean = []

		#Update triples according to new edges
		triples = [triple for triple in self.triples if self.hash(triple[0:2]) in hashes]
		edges = []

		i = 0
		while i < len(triples):
			triple = triples[i]
			for tripleBis in triples[i:]:
				if tripleBis[2] == triple[2]:
					edges.append([triple[0], tripleBis[0], triple[2]])
					nodesclean.append(triple[0])
					nodesclean.append(tripleBis[0])
			i += 1

		self.edges = edges
		nodesclean = list(set(nodesclean))
		self.nodes = [node for node in nodes if node[0] in nodesclean]

		self.weight(terms = terms)


	def weight(self, nodes = False, edges = False, terms = []):
		if nodes == False:
			nodes = self.nodes
		if edges == False:
			edges = self.edges

		terms = [node[0] for node in self.nodes if node[1] in terms]

		n = []
		for node in nodes:
			e = [row for row in edges if node[0] in row and (row[0] in terms or row[1] in terms)]
			n.append(node + [len(e)])

		self.nodes = n

	def gephi(self, mode="sentence"):
		separator = "\t"
		if mode == "lemma":
			nodesColumn = ["id", "label", "weight"]
			edgesColumn = ["target", "source", "sentence"]
			#self.weight()
		else:
			nodesColumn = ["id", "label", "type", "document"]
			edgesColumn = ["target", "source", "type"]

		f = codecs.open("./data/gephi/nodes.csv", "wt")
		f.write(separator.join(nodesColumn)+"\n")
		for node in self.nodes:
			f.write(separator.join([str(n).replace("\\n", " ").replace("\t", " ") for n in node])+"\n")
		f.close()

		f = codecs.open("./data/gephi/edges.csv", "wt")
		f.write(separator.join(edgesColumn)+"\n")
		for edge in self.edges:
			f.write(separator.join([str(e) for e in edge])+"\n")
		f.close()

	def clusterNodes(self):
		nodes = self.nodes
		return nodes

	def mergeEdges(self):
		#Merge edges and give them weight
		newEdges = []
		indexEdges = {}

		i = 0
		for edge in self.edges:
			#Edge : source,target,weight
			hash1 = self.hash([edge[0], edge[1]])
			hash2 = self.hash([edge[1], edge[0]])

			if hash1 in indexEdges:
				newEdges[indexEdges[hash1]][2] += 1
			elif hash2 in indexEdges:
				newEdges[indexEdges[hash2]][2] += 1
			else:
				newEdges.append([edge[0], edge[1], 1])
				indexEdges[hash1] = i
				indexEdges[hash2] = i
				i += 1

		return newEdges

	def JSON(self, group = False):
		graph = {"nodes" : [], "links" : []}

		"""
		node : { "name": "Myriel","group": 1 }
		edge : {"source": 42, "target": 41, "value": 2 }
		"""

		NodeIndex = {}

		i = 0
		for node in self.nodes:
			if group:
				graph["nodes"].append({"name" : node[1], "weight" : node[2], "group" : node[3]})
			else:
				graph["nodes"].append({"name" : node[1], "weight" : node[2], "group" : 0})
			NodeIndex[node[0]] = i
			i += 1
		for edge in self.edges:
			graph["links"].append({"source" : NodeIndex[edge[0]], "target": NodeIndex[edge[1]], "value" : edge[2]})

		return graph

	def threshold(self, threshold = 1):
		nodes = []
		deleted = []
		edges = []

		for node in self.nodes:
			if node[2] <= threshold:
				deleted.append(node[0])
			else:
				nodes.append(node)

		for edge in self.edges:
			if edge[0] not in deleted and edge[1] not in deleted:
				edges.append(edge)

		self.nodes = nodes
		self.edges = edges
		return True

	def D3JSMatrix(self, threshold = False, cluster = False):
		import json
		import classes.D3JS as D3JS
		D3 = D3JS.D3JS()
		self.edges = self.mergeEdges()

		if cluster == True:
			try:
				from classes.LSA import LSA
			except:
				print "Unable to load LSA dependency"
				sys.exit()
			self.lsa = LSA(nodes = self.nodes, edges = self.edges)
			self.nodes, self.edges = self.lsa.cluster(building = True)

		if threshold == True:
			self.threshold(1)

		graph = self.JSON(group = cluster)

		with codecs.open("./data/D3JS/data.json", "w") as f:
			f.write(json.dumps(graph))
			f.close()

		with codecs.open("./data/D3JS/index.html", "w") as f:
			f.write(D3.text())
			f.close()


	def ClothoWeb(self, terms = [], query = []):
		try:
			from classes.clotho import Clotho
		except:
			print "Unable to load clotho web dependency"
			sys.exit()

		C = Clotho(terms)
		C.save()
		return True