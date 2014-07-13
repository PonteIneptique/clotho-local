#!/usr/bin/python
# -*- coding: utf-8 -*-

#Python CORE
import os
import sys
import codecs
import hashlib
import json
import re
import string
import operator
from math import log
from pprint import pprint

#Python Libraries
import numpy
import scipy
import nltk
import pylab
import rdflib
import wikipedia
from SPARQLWrapper import SPARQLWrapper, JSON
import requests

#Shared class through Clotho
from classes.SQL import SQL
from dependencies.treetagger import TreeTagger
from classes.cache import Cache

#Specific class

"""
	Order of classes :
		- Corpus (Corpus Generator for R)
		- Export (General Export connector class)
		- D3JS (D3JS Co-occurrence export class)
		- Clotho (Clotho-Web export class)
		- LSA (Latent semantic Analysis class)
		- SMa (Semantic Matrix Class) -> Exempla Clustering
		- TFIDF (Matrix Class) -> Context clustering

	Order of models :
		- Terms
"""
class Corpus(object):
	def __init__(self, data = {}, flexed = False):
		self.folder = "./data/corpus/"
		self.flexed = flexed
		self.data = data

	def w(self, data = False):
		for term in data:
			if isinstance(data[term][0], list):
				replacement = ""
				for sentence in data[term]:
					replacement += " ".join(sentence) + "\n"
				data[term] = replacement
			else:
				data[term] = " ".join(data[term])
			with codecs.open("./data/corpus/" + term + ".txt", "w") as f:
				f.write(data[term])
				f.close()
		return True

	def rawCorpus(self, data = False):
		if not data:
			data = self.data
		outputDictionary = {}
		if self.flexed:
			for term in data:
				outputDictionary[term] = " ".join([word[0] for word in data[term]])
		else:
			for term in data:
				outputDictionary[term] = []
				for word in data[term]:
					for w in word[1]:
						outputDictionary[term].append(w[0])
		self.w(outputDictionary)

	def windowCorpus(self, window = 4, data = False):
		"""
			Return a raw corpus / term where only the n-words left AND right are kept from the sentence.

			Params
			window (Int) - N window
		"""
		if not data:
			data = self.data
		outputDictionary = {}

		#We merge everything in one sentence
		for term in data:
			outputDictionary[term] = []
			sentence = []
			sentence_text = ""
			for word in data[term]:
				lemma = []
				if sentence_text != word[3]:
					#Writing time
					if len(sentence) > 0:
						sentence = self.windowSentence(term, sentence, window)
						outputDictionary[term].append(sentence)
					#Creating the new sentence array
					sentence_text = word[3]
					sentence = []
					print sentence_text

				for w in word[1]:
					lemma.append(w[0])
				if len(lemma) > 0:
					sentence.append(lemma)

		if len(sentence) > 0:
			sentence = self.windowSentence(term, sentence, window)
			outputDictionary[term].append(sentence)

		self.w(outputDictionary)
		return True

	def windowSentence(self, term = "", sentence = [], window = 0):
		if len(sentence) <= 0:
			return sentence


		indexTerm = 0
		min_index = 0
		max_index = len(sentence) - 1
		length = window * 2 + 1

		for i in range(0,  max_index):
			lemma = sentence[i]
			if term in lemma:
				indexTerm = i 

				w = i - window
				if w > min_index:
					min_index = i - window

				w = min_index + length
				if w > max_index:
					max_index = max_index + 1
				else:
					max_index = length + min_index
				break

		sentence = sentence[min_index:max_index]
		s = []
		for lemma in sentence:
			for l in lemma:
				if not term in lemma:	#Remove the term from the sentence 
					s.append(l)
		return s


class Export(object):
	def __init__(self, q = False):
		self.q = q
		self.c = Cache()
		self.perseus = SQL()
		self.results = SQL(cache = True, web = False)
		self.cache = {"lemma" : {}, "sentence" : {}, "form": {}}

		###Load treetagger if possible
		try:
			self.tt = TreeTagger(encoding='latin-1',language='latin')
			self.ttAvailable = True
		except:
			self.ttAvailable = False

	def nodification(self):
		"""	Using SQL, retrieve the nodes and links so everything works with export
		"""

		if self.q and self.c.nodes(self.q, False, True):
			d = self.c.nodes(self.q)
			self.nodes = d["nodes"]
			self.edges = d["edges"]
			self.triples = d["triples"]
			return True

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

		if self.q:
			self.c.nodes(self.q, data = {"nodes" : nodes, "edges" : edges, "triples" : triples})


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
		"""	Clean the probability
			-> Use self. data
		"""
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
		""" Given a list of terms, transform a graph lemma -> form -> sentence into lemma <-> lemma

		Keyword arguments
		terms --- List of query terms (lemma people are looking form)
		"""


		"""
		if self.q and self.c.triples(self.q, False, True):
			d = self.c.nodes(self.q)
			self.nodes = d["nodes"]
			self.edges = d["edges"]
			return True
		"""
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

		if self.q:
			self.c.triples(self.q, {"nodes" : self.nodes, "edges" : self.edges})


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

	def gephi(self, mode="sentence", nodes = [], edges = [], labels = []):
		separator = "\t"
		if nodes == []:
			nodes = self.nodes
		if edges == []:
			edges = self.edges
		if mode == "lemma":
			nodesColumn = ["id", "label", "weight"]
			edgesColumn = ["target", "source", "sentence"]
			#self.weight()
		elif mode == "semantic":
			nodesColumn = labels
			edgesColumn = ["target", "source", "sentence"]
		else:
			nodesColumn = ["id", "label", "type", "document"]
			edgesColumn = ["target", "source", "type"]

		f = codecs.open("./data/gephi/nodes.csv", "wt")
		f.write(separator.join(nodesColumn)+"\n")
		for node in nodes:
			f.write(separator.join([str(n).replace("\\n", " ").replace("\t", " ") for n in node])+"\n")
		f.close()

		f = codecs.open("./data/gephi/edges.csv", "wt")
		f.write(separator.join(edgesColumn)+"\n")
		for edge in edges:
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
		D3 = D3JS()
		self.edges = self.mergeEdges()

		if cluster == True:
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

		C = Clotho(terms)
		C.save()
		return True

	def semanticMatrix(self, terms = [], query = []):
		""" Semantic matrix """

		sm = SMa(nodes = self.nodes, edges = self.edges, terms = terms)
		sm.dbpedia()
		sm.documents()
		sm.matrixify()
		sm.stats()
		sm.tfidf()

	def tfidfDistance(self, terms = [], query = []):
		""" TF-IDF for all lemma """
		sm = TFIDF(nodes = self.nodes, edges = self.edges, terms = terms)
		sm.matrixify()
		sm.stats()
		sm.tfidf()

	def semanticGephi(self, terms = []):
		sm = SMa(nodes = self.nodes, edges = self.edges, terms = terms)
		sm.dbpedia(definition = False)
		sm.gephi()
		self.gephi(mode = "semantic", nodes = sm.nodes, edges = sm.edges, labels = sm.labels)

	def corpus(self, data = {}):
		""" Generation of plain-text corpus by term """
		C = Corpus(data)
		C.rawCorpus()

	def fourWords(self, data = {}):
		""" Generation of plain-text corpus by term """
		C = Corpus(data)
		C.windowCorpus(4)
		
class D3JS(object):
	def text(self):
		""" Return a string containing a basic html page.
		"""
		return """
		<!DOCTYPE html>
<html><head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8"><meta charset="utf-8">
<title>Co-occurrence output</title>
<style>
.background {
fill: #eee;
}

line {
stroke: #fff;
}

text.active {
fill: red;
}
svg {
font: 8px sans-serif;
}
</style>

<link rel="stylesheet" href="http://netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css">
<script src="http://d3js.org/d3.v2.min.js?2.8.1"></script>
</head>
<body>
<div class="container" style="margin-top:30px;">

<aside class="col-md-3">
<h1>Co-occurrence</h1>
<p>
Order:
<select id="order">
<option value="name">by Name</option>
<option value="count">by Frequency</option>
<option selected="selected" value="group">by Cluster</option>
</select>
</p>
<p>
Each colored cell represents two terms that appeared in the 
same sentence; darker cells indicate terms that co-occurred more 
frequently.
</p>
<p>
Use the drop-down menu to reorder the matrix and explore the data.
</p>
<p>
Built with <a href="http://d3js.org/">d3.js</a>.
</p>
<p>
Originally done by <a href="http://bost.ocks.org/mike/" rel="author">Mike Bostock</a>
</p>
</aside>
<section id="svg" class="col-md-9">
</section>

<script>

var margin = {top: 80, right: 0, bottom: 10, left: 80},
width = 720,
height = 720;

var x = d3.scale.ordinal().rangeBands([0, width]),
z = d3.scale.linear().domain([0, 4]).clamp(true),
c = d3.scale.category10().domain(d3.range(10));

var svg = d3.select("#svg").append("svg")
.attr("width", width + margin.left + margin.right)
.attr("height", height + margin.top + margin.bottom)
.style("margin-left", margin.left + "px")
.append("g")
.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

d3.json("data.json", function(clotho) {
console.log(clotho)
var matrix = [],
nodes = clotho.nodes,
n = nodes.length;

// Compute index per node.
nodes.forEach(function(node, i) {
node.index = i;
node.count = 0;
matrix[i] = d3.range(n).map(function(j) { return {x: j, y: i, z: 0}; });
});

// Convert links to matrix; count character occurrences.
clotho.links.forEach(function(link) {

matrix[link.source][link.target].z += link.value;
matrix[link.target][link.source].z += link.value;
matrix[link.source][link.source].z += link.value;
matrix[link.target][link.target].z += link.value;
nodes[link.source].count += link.value;
nodes[link.target].count += link.value;
});

// Precompute the orders.
var orders = {
name: d3.range(n).sort(function(a, b) { return d3.ascending(nodes[a].name, nodes[b].name); }),
count: d3.range(n).sort(function(a, b) { return nodes[b].count - nodes[a].count; }),
group: d3.range(n).sort(function(a, b) { return nodes[b].group - nodes[a].group; })
};

// The default sort order.
x.domain(orders.name);

svg.append("rect")
.attr("class", "background")
.attr("width", width)
.attr("height", height);

var row = svg.selectAll(".row")
.data(matrix)
.enter().append("g")
.attr("class", "row")
.attr("transform", function(d, i) { return "translate(0," + x(i) + ")"; })
.each(row);

row.append("line")
.attr("x2", width);

row.append("text")
.attr("x", -6)
.attr("y", x.rangeBand() / 2)
.attr("dy", ".32em")
.attr("text-anchor", "end")
.text(function(d, i) { return nodes[i].name; });

var column = svg.selectAll(".column")
.data(matrix)
.enter().append("g")
.attr("class", "column")
.attr("transform", function(d, i) { return "translate(" + x(i) + ")rotate(-90)"; });

column.append("line")
.attr("x1", -width);

column.append("text")
.attr("x", 6)
.attr("y", x.rangeBand() / 2)
.attr("dy", ".32em")
.attr("text-anchor", "start")
.text(function(d, i) { return nodes[i].name; });

function row(row) {
var cell = d3.select(this).selectAll(".cell")
.data(row.filter(function(d) { return d.z; }))
.enter().append("rect")
.attr("class", "cell")
.attr("x", function(d) { return x(d.x); })
.attr("width", x.rangeBand())
.attr("height", x.rangeBand())
.style("fill-opacity", function(d) { return z(d.z); })
.style("fill", function(d) { return nodes[d.x].group == nodes[d.y].group ? c(nodes[d.x].group) : null; })
.on("mouseover", mouseover)
.on("mouseout", mouseout);
}

function mouseover(p) {
d3.selectAll(".row text").classed("active", function(d, i) { return i == p.y; });
d3.selectAll(".column text").classed("active", function(d, i) { return i == p.x; });
}

function mouseout() {
d3.selectAll("text").classed("active", false);
}

d3.select("#order").on("change", function() {
clearTimeout(timeout);
order(this.value);
});

function order(value) {
x.domain(orders[value]);

var t = svg.transition().duration(2500);

t.selectAll(".row")
.delay(function(d, i) { return x(i) * 4; })
.attr("transform", function(d, i) { return "translate(0," + x(i) + ")"; })
.selectAll(".cell")
.delay(function(d) { return x(d.x) * 4; })
.attr("x", function(d) { return x(d.x); });

t.selectAll(".column")
.delay(function(d, i) { return x(i) * 4; })
.attr("transform", function(d, i) { return "translate(" + x(i) + ")rotate(-90)"; });
}

var timeout = setTimeout(function() {
order("group");
d3.select("#order").property("selectedIndex", 2).node().focus();
}, 5000);
});
</script>

</div>
</body>
</html>

		"""

class Clotho(object):
	def __init__(self, terms = [], query_terms = []):

		try:
			self.sql = SQL(web=True)
			self.con = self.sql.con
			self.origin = SQL()
		except:
			print "Unable to load SQL dependecy"

		self.terms = terms
		self.query_terms = query_terms
		self.saved = {"lemma" : {}, "sentence" : {}, "form": {}}
		self.url = {"thesaurus" : "http://www.perseus.tufts.edu/hopper/"}
		self.pythonUser = 0
		self.edges = []

		self.annot_index = {"Place" : 2, "Person" : 1, "Date" : 3, "Site" : 5}

	def setup(self):
		annotation_type = "INSERT INTO `annotation_type` VALUES (1,'Type','Type','dc:Type','lemma'),(2,'Polyphony','Polyphony','dc:Polyphony','sentence')"
		annotation_value = "INSERT INTO `annotation_value` VALUES (1,'Person','Person',1,'Person'),(2,'Place','Place',1,'Place'),(3,'Date','Date',1,'Date'),(4,'Irony','Irony',2,'Irony'),(5,'Site','Site',2,'Site')"
		with self.con:
			cur = self.con.cursor()
			cur.execute(annotation_type)
			cur.execute(annotation_value)

	def save(self):
		#We setup annotations
		self.setup()

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
					if lemma[0] in self.query_terms:
						query_lemma = 1
					else:
						query_lemma = 0
					cur.execute("INSERT INTO lemma (text_lemma, query_lemma) VALUES (%s, %s)", [lemma[0], query_lemma])
					r = self.con.insert_id()
					self.saved["lemma"][lemma[0]] = r

					if lemma[1] != None:
						self.annotation(r, lemma[1], vote = True)
					return r

	def annotation(self, id_lemma, value, vote = False):
		with self.con:
			cur = self.con.cursor()
			"""			"""

			cur.execute("INSERT INTO `annotation` (`id_annotation_type`, `id_annotation_value`,`id_user`,`table_target_annotation`,`id_target_annotation`) VALUES ('1' ,%s ,%s ,'lemma',%s); ", [self.annot_index[value], self.pythonUser, id_lemma])
			r = self.con.insert_id()
			if vote == True:
				self.annotation_vote(r)


	def annotation_vote(self, id_annotation):
		with self.con:
			cur = self.con.cursor()
			cur.execute("INSERT INTO annotation_vote (id_annotation, id_user, value) VALUES ( %s , %s , %s ) ", [id_annotation, self.pythonUser, 1])

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
				
				if isinstance(row[2], basestring) != True:
					id_document = row[2][1]
				else:
					id_document = row[2]

				if len(row[1]) == 0:
					s = self.sentence(row[3], id_document)
					l = 0
					f = self.form(row[0])

					self.relationship(s,f,l)
				else:
					for lemma in row[1]:

						s = self.sentence(row[3], id_document)
						l = self.lemma(lemma)
						f = self.form(row[0])

						self.relationship(s,f,l)

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

class LSA(object):
	def __init__(self, nodes, edges):
		self.wdict = {}
		self.wcount = 0
		self.nodes = nodes
		self.edges = edges
		self.matrix = numpy.mat(numpy.zeros([len(self.nodes), len(self.nodes)]), int)

	def build(self):
		""" Build a matrix, needs an instance of self
		"""
		for node in self.nodes:
			self.wdict[node[0]] = self.wcount
			self.wcount += 1

		for edge in self.edges:
			self.matrix[self.wdict[edge[0]], self.wdict[edge[1]]] += 1
			self.matrix[self.wdict[edge[1]], self.wdict[edge[0]]] += 1

		self.matrix = self.matrix * self.matrix

		return self.matrix

	def cluster(self, building = False):
		""" Cluster a matrix

		keywords argument:
		building -- Whether the matrix should be build before or not.
		"""
		if building == True:
			self.build()
			
		clustering = sklearn.cluster.spectral_clustering(self.matrix)

		i = 0
		for id in clustering:
			self.nodes[i].append(int(id + 1))
			i += 1

		return self.nodes, self.edges

	def findzeros(self):
		""" Return the number of 0 in the matrix
		"""
		z =0
		if 0 in self.matrix.flat:
			z += 1
		return z

class SMa(object):
	def __init__(self, nodes = [], edges = [], terms = [], prevent = False):
		"""	Initialize

		Keyword arguments
		nodes -- List of nodes using list -> [[idNode, textNode, whatever...], etc.]
		edges -- List of edges [[idNode1, idNode2, idSentence], etc.]
		terms -- Query terms
		prevent -- Prevent autocompute for debugging
		"""
		self.r = requests

		self.rdf = rdflib.Graph()
		self.cache = Cache()
		self.semes= {}
		self.dbpedia_url = "http://dbpedia.org/resource/"

		if prevent == False:
			temp_nodes = nodes
			self.edges = edges

			self.matrix = []
			self.lemma = {}
			self.terms = {}

			#We split nodes informations between terms and lemma, eg : latest being example found 
			for node in temp_nodes:
				if node[1] not in terms:
					self.lemma[node[0]] = node[1]
				else:
					self.terms[node[0]] = node[1]
	def addslashes(self, s):
		l = ["\\", '"', "'", "\0", ]
		for i in l:
			if i in s:
				s = s.replace(i, '\\'+i)
		return s
	def definition(self, url):
		sparql = SPARQLWrapper("http://dbpedia.org/sparql")

		punctuation = (';', ':', ',', '.', '!', '?', '(', ')', '-', "'", '"')
		sparql.setQuery("""SELECT str(?desc) 
					where {
					  <"""+url+"""> <http://www.w3.org/2000/01/rdf-schema#comment> ?desc
					  FILTER (langMatches(lang(?desc),"en"))
					} LIMIT 1""")
		sparql.setReturnFormat(JSON)
		results = sparql.query().convert()
		stopword = nltk.corpus.stopwords.words("english")

		if len(results["head"]["vars"]) > 0:
			var = results["head"]["vars"][0]
			if len(results["results"]["bindings"]) == 1:
				return [w for w in nltk.tokenize.word_tokenize(results["results"]["bindings"][0][var]["value"]) if w not in stopword and w not in punctuation]
			else:
				return []
		else:
			return []

	def sparql(self, name):

		sparql = SPARQLWrapper("http://dbpedia.org/sparql")
		sparql.setQuery("""
			PREFIX foaf: <http://xmlns.com/foaf/0.1/>
			SELECT ?url WHERE {
			  ?url a ?type;
			     foaf:name '""" + self.addslashes(name) + """'@en .
			} LIMIT 1
			""")
		sparql.setReturnFormat(JSON)
		results = sparql.query().convert()

		if len(results["results"]["bindings"]) == 1:
			return results["results"]["bindings"][0]["url"]["value"]
		else:
			return False

	def load(self, url):
		f = self.cache.rdf(url, check = True)
		if f == False:
			statusCode = 0
			tentative = 0
			while statusCode != self.r.codes.ok and tentative <= 5:
				try:
					r = self.r.get(url, headers = {
						"accept" : 'application/rdf+xml,text/rdf+n3;q=0.9,application/xhtml+xml'
					}, timeout = 5)
					statusCode = r.status_code
				except:
					statusCode = 0
					tentative += 1

				self.cache.rdf(url, data = r)
				self.rdf.load(self.cache.rdf(url, check = True))
		else:
			self.rdf.load(f)

	def lookup(self, url):
		""" 
		Inspired by https://github.com/abgoldberg/tv-guests/blob/master/dbpedia.py

		"""
		l = {}

		self.rdf = rdflib.Graph()
		self.currentUrl = url
		self.load(url)
		if len(self.rdf) == 0:
			results = wikipedia.search(url.split("/")[-1])
			if len(results) > 0:
				input = results[0] # -> Page Name
				url = self.sparql(input)
				if url == False:
					return {}
				self.currentUrl = url
				l = self.lookup(url)
				return l
		else:

			for s,p,o in self.rdf:
				"""We construct a json whith the following structure :
				# Name : md5(url).json
				# {
					p : [o]
				}
				"""
				pp = unicode(p.toPython()).encode("utf-8")
				oo = unicode(o.toPython()).encode("utf-8")
				if pp not in l:
					l[pp] = []
				if pp == "http://dbpedia.org/ontology/wikiPageRedirects" and oo != url:
					self.currentUrl = oo
					return self.lookup(oo)
				l[pp].append(oo)
			return l

	def dbpedia(self, definition = True):
		for lem in self.lemma:
			l = self.lemma[lem]
			c = False
			#print "Looking for " + l
			url = self.dbpedia_url + l
			self.currentUrl = url
			#Checking if exist
			c = self.cache.dbpedia(url)
			if c == False:
				l = self.lookup(url)
				self.cache.dbpedia(url, l)
			else:
				l = c

			d = self.cache.definition(self.currentUrl)
			if d == False:
				d = self.definition(self.currentUrl)
				self.cache.definition(self.currentUrl, d)
			else:
				d = d

			self.semes[self.lemma[lem]] = Term(l)

			if definition == True:
				self.semes[self.lemma[lem]].definition(d)

	def documents(self):
		"""	Returns a list of document given nodes and edges so we can perform tf-idf 

		Keyword arguments :
		"""
		properties = {}
		reversedProperties = {}
		document = {}

		for exempla in self.semes:
			seme = self.semes[exempla]
			if exempla not in document:
				document[exempla] = []
			for propertyItem in seme.graph:
				for prop in seme.graph[propertyItem]:
					pprop = propertyItem + ":" + prop
					if pprop not in properties:
						l = len(properties)
						properties[pprop] = l
						reversedProperties[l] = pprop
					document[exempla].append(properties[pprop])


		self.document = document
		self.properties = properties
		self.reversedProperties = reversedProperties
		return True

	def cleanProperty(self, prop):
		r = re.compile("([A-Za-z]+)[0-9]+")
		p = r.match(prop)
		if p:
			return p.group(1)
		else:
			return prop

	def gephi(self, liste = True):
		""" Get the gephi representation of the matrix
		"""
		self.nodes = {}
		self.csvIndex = {"id": 0, "label" : 1, "type" : 2}
		indexes = ["id", "label", "type"]


		for term in self.terms:
			self.nodes[term] = {"label" : self.terms[term], "id" : term, "type" : "term"}
		edges = self.edges
		self.edges = [edge for edge in self.edges if edge[0] != edge[1] and edge[0] in self.nodes]
		for e in [edge for edge in edges if edge[0] != edge[1] and edge[1] in self.nodes]:
			self.edges += [e[1], e[0]]

		for lemma in self.lemma:

			self.nodes[lemma] = self.semes[self.lemma[lemma]].graph
			self.nodes[lemma]["label"] = self.lemma[lemma]
			self.nodes[lemma]["id"] = lemma
			self.nodes[lemma]["type"] = "entity"

		#Now we have the whole set of nodes
		#We need to extract all information so it would feet into a CSV...
		i = 3
		if liste:
			for node in self.nodes:
				for prop in self.nodes[node]:
					if prop not in indexes:
						if prop not in self.csvIndex:
							self.csvIndex[prop] = i
							i += 1

			nodes = []
			for node in self.nodes:
				n = [0] * len(self.csvIndex)
				for prop in self.nodes[node]:
					if isinstance(self.nodes[node][prop], list):

						n[self.csvIndex[prop]] = ",".join([self.cleanProperty(elem) for elem in self.nodes[node][prop]])
					else:
						n[self.csvIndex[prop]] = self.nodes[node][prop]
				nodes.append(n)

			labels = sorted(self.csvIndex.iteritems(), key=operator.itemgetter(1))
			self.labels = [label[0] for label in labels]
		else: #Returns properties as nodes
			for node in self.nodes:
				for prop in self.nodes[node]:
					if prop not in indexes:
						for elem in self.nodes[node][prop]:
							el = self.cleanProperty(elem)
							if el not in self.csvIndex:
								self.csvIndex[el] = i
								i += 1

			nodes = []
			for node in self.nodes:
				n = [0] * len(indexes)
				for prop in self.nodes[node]:
					if isinstance(self.nodes[node][prop], list):
						for elem in self.nodes[node][prop]:
							el = self.cleanProperty(elem)
							self.edges.append([node, self.csvIndex[el], 1])
					else:
						n[self.csvIndex[prop]] = self.nodes[node][prop]
				nodes.append(n)


			for element in self.csvIndex:
				if element not in indexes:
					el = self.cleanProperty(elem)
					nodes.append([self.csvIndex[el], el, "property"])

			self.labels = indexes
		self.nodes = nodes

	def matrixify(self):
		m = []
		ms = []
		#We get all terms
		for term in self.terms:
			t = []
			ts = []
			#We get all linked lemma
			for edge in [e for e in self.edges if term in e]:
				if edge[0] == term:
					otherEdge = edge[1]
				else:
					otherEdge = edge[0]
				if otherEdge not in self.terms:
					#Now we get the document informations
					t += self.document[self.lemma[otherEdge]]
					ts += [1]
			#Just a temp check
			#t = [self.reversedProperties[prop] for prop in t]
			#End temp check
			if len(t) > 0:
				m.append(t)
				ms.append(ts)
			else:
				self.terms[term] = False

		#Now we have a matrix with ids of item, now let make a real matrix
		matrix = []
		self.prematrix = ms
		for mm in m:
			t = [0]*len(self.properties) #We fill the matrix
			for e in mm:
				t[e] += 1
			matrix.append(t)

		self.matrix = matrix
		return self.matrix


	def stats(self):
		labels = [self.terms[t] for t in self.terms if self.terms[t] != False]
		sums = [sum([1 for p in m if p > 1]) for m in self.prematrix]
		for i, s in enumerate(sums):
			print labels[i] + "\t" + str(s)

	def tfidf(self):
		tfidf_matrix = []
		#TF = frequency in first list / max frequency available in document
		for term_matrix in self.matrix:
			term_tfidf_matrix = [0]*len(term_matrix)
			maxTF = float(max(term_matrix))
			i = 0
			for term in term_matrix:
				tf = float(term) / maxTF
				idf = float(len(term_matrix)) / (1.0 + float(len([1 for other_matrix in self.matrix if other_matrix[i] != 0])))
				term_tfidf_matrix[i] = tf * log(idf)
				i += 1
			tfidf_matrix.append(term_tfidf_matrix)

		self.tfidf_matrix = tfidf_matrix

		self.vectors = [numpy.array(f) for f in tfidf_matrix]

		U,s,V = numpy.linalg.svd(self.vectors) # svd decomposition of A
		print "Vectors created", len(self.vectors[0]), "after SVD decomposition", len(U)

		#clusterer = nltk.cluster.GAAClusterer(num_clusters=3)
		#clusters = clusterer.cluster(self.vectors, True)

		# print "Means: ", clusterer.means()
		labels = [self.terms[t] for t in self.terms if self.terms[t] != False]
		#clusterer.dendrogram().show(leaf_labels = labels )


		#Using a distance matrix
		distMatrix = scipy.spatial.distance.pdist(self.tfidf_matrix)
		distSquareMatrix = scipy.spatial.distance.squareform(distMatrix)

		#calculate the linkage matrix
		fig = pylab.figure(figsize=(10,10))
		linkageMatrix = scipy.cluster.hierarchy.linkage(distSquareMatrix, method = 'ward')
		dendro = scipy.cluster.hierarchy.dendrogram(linkageMatrix,orientation='left', labels=labels)
		fig.savefig('dendrogram.png')

		#Using KMEANS
		clusterer = nltk.cluster.KMeansClusterer(3, nltk.cluster.euclidean_distance, repeats=10, avoid_empty_clusters=True)
		answer = clusterer.cluster(self.vectors, True)

	def pprint(self):
		print self.semes

class TFIDF(object):
	def __init__(self, nodes = [], edges = [], terms = [], prevent = False):
		"""	Initialize

		Keyword arguments
		nodes -- List of nodes using list -> [[idNode, textNode, whatever...], etc.]
		edges -- List of edges [[idNode1, idNode2, idSentence], etc.]
		terms -- Query terms
		prevent -- Prevent autocompute for debugging
		"""
		self.semes = {}

		#Need a dictionary and reversed dictionary
		temp_nodes = nodes
		self.edges = edges
		self.nodes = nodes

		self.matrix = []
		self.lemma = {}
		self.terms = {}
		self.total = {}
		self.reversed = []

		#We split nodes informations between terms and lemma, eg : latest being example found 
		for node in temp_nodes:
			if node[1] not in terms:
				i = len(self.reversed)
				self.lemma[node[0]] = i
				self.reversed.append(node[0])
			else:
				self.terms[node[0]] = node[1]
				self.total[node[0]] = 0

		print self.lemma

	def matrixify(self):
		m = []
		#We get all terms
		for term in self.terms:
			t = []
			#We get all linked lemma
			for edge in [e for e in self.edges if term in e]:
				if edge[0] == term:
					otherEdge = edge[1]
				else:
					otherEdge = edge[0]
				if otherEdge not in self.terms:
					#Now we get the document informations
					idLemma = self.lemma[otherEdge]
					t += [idLemma]
					self.total[term] += 1

			if len(t) > 0:
				m.append(t)
			else:
				self.terms[term] = False

		#Now we have a matrix with ids of item, now let make a real matrix
		matrix = []
		for mm in m:
			t = [0]*len(self.lemma) #We fill the matrix
			for e in mm:
				t[e] += 1
			matrix.append(t)

		self.matrix = matrix
		return self.matrix

	def stats(self):
		labels = [self.terms[t] for t in self.terms if self.terms[t] != False]
		print self.matrix
		print self.terms
		sums = [sum(m) for m in self.matrix]
		for i, s in enumerate(sums):
			print labels[i] + "\t" + str(s)


	def tfidf(self):
		tfidf_matrix = []
		#TF = frequency in first list / max frequency available in document
		for term_matrix in self.matrix:
			term_tfidf_matrix = [0]*len(term_matrix)
			maxTF = float(max(term_matrix))
			i = 0
			for term in term_matrix:
				tf = float(term) / maxTF
				idf = float(len(term_matrix)) / (1.0 + float(len([1 for other_matrix in self.matrix if other_matrix[i] != 0])))
				term_tfidf_matrix[i] = tf * log(idf)
				i += 1
			tfidf_matrix.append(term_tfidf_matrix)

		self.tfidf_matrix = tfidf_matrix

		self.vectors = [numpy.array(f) for f in tfidf_matrix]

		U,s,V = numpy.linalg.svd(self.vectors) # svd decomposition of A
		print "Vectors created", len(self.vectors[0]), "after SVD decomposition", len(U)

		#clusterer = nltk.cluster.GAAClusterer(num_clusters=3)
		#clusters = clusterer.cluster(self.vectors, True)

		# print "Means: ", clusterer.means()
		labels = [self.terms[t] for t in self.terms if self.terms[t] != False]
		#clusterer.dendrogram().show(leaf_labels = labels )


		#Using a distance matrix
		distMatrix = scipy.spatial.distance.pdist(self.tfidf_matrix)
		distSquareMatrix = scipy.spatial.distance.squareform(distMatrix)

		#calculate the linkage matrix
		fig = pylab.figure(figsize=(10,10))
		linkageMatrix = scipy.cluster.hierarchy.linkage(distSquareMatrix, method = 'ward')
		dendro = scipy.cluster.hierarchy.dendrogram(linkageMatrix,orientation='left', labels=labels)
		fig.savefig('dendrogram.png')

		#Using KMEANS
		"""
		clusterer = nltk.cluster.KMeansClusterer(3, nltk.cluster.euclidean_distance, repeats=10, avoid_empty_clusters=True)
		answer = clusterer.cluster(self.vectors, True)
"""
	def pprint(self):
		print self.semes


class Term(object):
	def __init__(self, json):
		self.json = json

		self.graph = {}

		self.yago = re.compile("(\w*)[0-9]*")
		self.category = re.compile("Category:(\w*)")
		self.avoid = [u'rdf-schema#comment', u'wikiPageExternalLink', u'hasPhotoCollection', u'isPrimaryTopicOf', u'id', u'viaf', u'influenced',  u'influencedBy',  u'influences', u"owl#sameAs", u'abstract', u'wikiArticles', u'wikiPageDisambiguates', u'wikiPageExternalLink', u'wikiPageID', u'wikiPageInLinkCount', u'wikiPageOutLinkCount', u'wikiPageRedirects',u'thumbnail', u'wikiPageRevisionID', u'rdf-schema#comment', u'site', u'rdf-schema#label',u'prov#wasDerivedFrom']
		self.keep = [u"subject", u"22-rdf-syntax-ns#type", u"placeOfDeath", u"placeOfBirth", u"country", ]
		if json:
			for p in json:
				pp = self.toString(p)
				if pp in self.keep:
					self.graph[pp] = []
					for o in json[p]:
						oo = self.toString(o)
						if self.yago.match(oo):
							oo = self.yago.search(oo).group(1)
						elif self.category.match(oo):
							oo = self.category.search(oo).group(1)
						if oo not in self.graph[pp]:
							self.graph[pp].append(oo)

	def toString(self, url):
		if url[0:7] == "http://":
			value = url.split("/")
			return value[-1]
		else:
			return url

	def pprint(self):
		pprint(self.graph)

	def definition(self, d):
		self.graph["DBPediaDEF"] = d