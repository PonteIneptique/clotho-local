#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from pprint import pprint

class Term(object):
	def __init__(self, json):
		self.json = json

		self.graph = {}

		self.avoid = [u'rdf-schema#comment', u'wikiPageExternalLink', u'hasPhotoCollection', u'isPrimaryTopicOf', u'id', u'viaf', u'influenced',  u'influencedBy',  u'influences', u"owl#sameAs", u'abstract', u'wikiArticles', u'wikiPageDisambiguates', u'wikiPageExternalLink', u'wikiPageID', u'wikiPageInLinkCount', u'wikiPageOutLinkCount', u'wikiPageRedirects',u'thumbnail', u'wikiPageRevisionID', u'rdf-schema#comment', u'site', u'rdf-schema#label',u'prov#wasDerivedFrom']

		if json:
			for p in json:
				pp = self.toString(p)
				if pp not in self.avoid:
					self.graph[pp] = []
					for o in json[p]:
						oo = self.toString(o)
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
