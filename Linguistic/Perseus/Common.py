#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, re, codecs
from bs4 import BeautifulSoup
sys.path.append("../..")

import Data

class Chunk(Data.Models.documents.Chunk):
	#__init__(self, uid = None, document = None, section = None, xml = None, offset = None)
	def __init__(self, *args, **kw):
		super(self.__class__, self).__init__(*args, **kw)

	def getChunkText(self, text):
		if self.xml:
			model = BeautifulSoup(" ".join([self.xml.opening, self.xml.closing]))
			tags = model.find_all(True)

			t = BeautifulSoup(self.text)
			div1 = t.find(tags[-1].name, tags[-1].attrs)
			div2 = div1.find(True,{"type" : self.section.section, "n" : self.section.identifier})

			if div2:
				return div2.text.encode("UTF-8")
			elif div1:
				return div1.text.encode("UTF-8")
			else:
				raise ValueError("Text not found for given identifier")
		else:
			return text

	def getPath(self):
		"""
			Parse and return a given path
		"""
		_regexp = re.compile("Perseus:text:([0-9]{4}\.[0-9]{2}\.[0-9]{4})")
		p = "../../texts/"
		identifier = _regexp.search(self.document.uid).group(1)
		identifier = identifier.split(".")
		p += ".".join(identifier[:2]) + "/" + ".".join(identifier) + ".xml"

		return p

	def getText(self):
		path = self.getPath()
		
		with codecs.open(path, "r", "UTF-8") as f:
			text = f.read()
			f.close()
			self.text = text
			return self.getChunkText(text);

		raise ValueError("Path to file is incorrect")