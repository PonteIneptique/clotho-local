#!/usr/bin/python
# -*- coding: utf-8 -*-

import rdflib
import wikipedia
from classes.cache import Cache
from models.Term import Term

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

	def load(self, url):
		print "HELLOOO"
		f = self.cache.rdf(url, check = True)
		if f == False:
			statusCode = 0
			while statusCode != self.r.codes.ok:
				print statusCode
				print url
				try:
					r = self.r.get(url, headers = {
						"accept" : 'application/rdf+xml,text/rdf+n3;q=0.9,application/xhtml+xml'
					}, timeout = 1)
					statusCode = r.status_code
				except:
					statusCode = 0
			self.cache.rdf(url, data = r)
		else:
			self.rdf.load(f)

	def lookup(self, url):
		""" 
		Inspired by https://github.com/abgoldberg/tv-guests/blob/master/dbpedia.py

		"""
		l = {}

		self.load(url)
		if len(self.rdf) == 0:
			results = wikipedia.search(url.split("/")[-1])
			if len(results) > 0:
				input = results[0]
				print input
				l = lookup(input)
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
					return self.lookup(oo)
				l[pp].append(oo)
			return l

	def dbpedia(self):
		for lem in self.lemma:
			l = self.lemma[lem]
			c = False
			print "Looking for " + l
			url = "http://dbpedia.org/resource/" + l
			#Checking if exist
			c = self.cache.dbpedia(url)
			if c == False:
				l = self.lookup(url)
				self.cache.dbpedia(url, l)
			else:
				l = c

			self.semes[self.lemma[lem]] = Term(l)


			


	def documents(self):
		"""	Returns a list of document given nodes and edges so we can perform tf-idf 

		Keyword arguments :
		"""
		return True

	def pprint(self):
		print self.semes