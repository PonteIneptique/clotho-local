#!/usr/bin/python
# -*- coding: utf-8 -*-

import pylab
import rdflib
from pprint import pprint
from math import log
import numpy
import nltk
import scipy.cluster.hierarchy as hier
import scipy.spatial.distance as dist


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
		distMatrix = dist.pdist(self.tfidf_matrix)
		distSquareMatrix = dist.squareform(distMatrix)

		#calculate the linkage matrix
		fig = pylab.figure(figsize=(10,10))
		linkageMatrix = hier.linkage(distSquareMatrix, method = 'ward')
		dendro = hier.dendrogram(linkageMatrix,orientation='left', labels=labels)
		fig.savefig('dendrogram.png')

		#Using KMEANS
		"""
		clusterer = nltk.cluster.KMeansClusterer(3, nltk.cluster.euclidean_distance, repeats=10, avoid_empty_clusters=True)
		answer = clusterer.cluster(self.vectors, True)
"""
	def pprint(self):
		print self.semes