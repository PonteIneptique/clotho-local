#!/usr/bin/python
# -*- coding: utf-8 -*-

from pprint import pprint
import re

class DataTerm:
	pass

class Term(DataTerm):
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
