#!/usr/bin/python
# -*- coding: utf-8 -*-

#Python CORE
import sys

#Python Libraries
from numpy import zeros, mat, linalg
import scipy as sp
from sklearn.cluster import spectral_clustering

#Shared class through Clotho

#Specific class

#Python Warning


class LSA(object):
	
	def __init__(self, nodes, edges):
		self.wdict = {}
		self.wcount = 0
		self.nodes = nodes
		self.edges = edges
		self.matrix = mat(zeros([len(self.nodes), len(self.nodes)]), int)

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
			
		clustering = spectral_clustering(self.matrix)

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