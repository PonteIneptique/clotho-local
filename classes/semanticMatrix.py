#!/usr/bin/python
# -*- coding: utf-8 -*-

import pylab
import rdflib
import wikipedia
from pprint import pprint
from classes.cache import Cache
from models.Term import Term
from SPARQLWrapper import SPARQLWrapper, JSON
from math import log
import numpy
import nltk
import scipy.cluster.hierarchy as hier
import scipy.spatial.distance as dist

from  nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string


class SMa(object):
	def __init__(self, nodes = [], edges = [], terms = [], prevent = False):
		"""	Initialize

		Keyword arguments
		nodes -- List of nodes using list -> [[idNode, textNode, whatever...], etc.]
		edges -- List of edges [[idNode1, idNode2, idSentence], etc.]
		terms -- Query terms
		prevent -- Prevent autocompute for debugging
		"""
		try:
			import requests
			self.r = requests
		except:
			print "Unable to load Request. http://docs.python-requests.org/en/latest/user/install/#install"

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
		stopword = stopwords.words("english")

		if len(results["head"]["vars"]) > 0:
			var = results["head"]["vars"][0]
			if len(results["results"]["bindings"]) == 1:
				return [w for w in word_tokenize(results["results"]["bindings"][0][var]["value"]) if w not in stopword and w not in punctuation]
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
			     foaf:name '""" + name + """'@en .
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
			#Checking rediret
			"""
			redirect = self.rdf.triples( (url, "http://dbpedia.org/ontology/wikiPageRedirects", None) ).toPython()
			if len(redirect) > 0:
				print redirect
			"""

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

	def dbpedia(self):
		for lem in self.lemma:
			l = self.lemma[lem]
			c = False
			print "Looking for " + l
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
					t += self.document[self.lemma[otherEdge]]
			#Just a temp check
			#t = [self.reversedProperties[prop] for prop in t]
			#End temp check
			if len(t) > 0:
				m.append(t)
			else:
				self.terms[term] = False

		#Now we have a matrix with ids of item, now let make a real matrix
		matrix = []
		for mm in m:
			t = [0]*len(self.properties) #We fill the matrix
			for e in mm:
				t[e] += 1
			matrix.append(t)

		self.matrix = matrix
		return self.matrix


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

		# print "First 50 words are", unique_terms[:20]
		for fileindex in U:
			print "First 10 stats for this document are:", fileindex[0:10]

		clusterer = nltk.cluster.GAAClusterer(num_clusters=3)
		clusters = clusterer.cluster(self.vectors, True)

		print "clusterer: ", clusterer
		print "clustered: ", self.vectors
		print "As: ", clusters
		# print "Means: ", clusterer.means()
		labels = [self.terms[t] for t in self.terms if self.terms[t] != False]
		clusterer.dendrogram().show(leaf_labels = labels )


		#Using a distance matrix
		distMatrix = dist.pdist(self.tfidf_matrix)
		distSquareMatrix = dist.squareform(distMatrix)
		print '\ndistance matrix:'
		print distSquareMatrix

		#calculate the linkage matrix
		fig = pylab.figure(figsize=(10,10))
		linkageMatrix = hier.linkage(distSquareMatrix, method = 'ward')
		dendro = hier.dendrogram(linkageMatrix,orientation='left', labels=labels)
		fig.savefig('dendrogram.png')
		print dendro

		#Using KMEANS
		clusterer = nltk.cluster.KMeansClusterer(3, nltk.cluster.euclidean_distance, repeats=10, avoid_empty_clusters=True)
		print '\nK-means results using NLTK:'
		answer = clusterer.cluster(self.vectors, True)
		
		print('Clustered:', self.vectors)
		print('As:', answer)
		print('Means:', clusterer.means())

	def pprint(self):
		print self.semes