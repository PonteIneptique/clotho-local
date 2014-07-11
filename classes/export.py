#!/usr/bin/python
# -*- coding: utf-8 -*-

#Python CORE
import os
import sys
import codecs
import hashlib
import json
from pprint import pprint

#Python Libraries

#Shared class through Clotho
from classes.SQL import SQL
from dependencies.treetagger import TreeTagger
from classes.cache import Cache

#Specific class
from classes.LSA import LSA
from classes.D3JS import D3JS
from classes.clotho import Clotho
from classes.semanticMatrix import SMa
from classes.tfidf import TFIDF

"""
	Order of classes :
		- Corpus (Corpus Generator for R)
		- Export (General Export connector class)
		- D3JS
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
		if not self.data:
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