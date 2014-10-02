#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, libxml2, sys, codecs
sys.path.append("../..")

import Data

class Chunk(Data.Models.documents.Chunk):
	#__init__(self, uid = None, document = None, section = None, xml = None, offset = None)
	def __init__(self, *args, **kw):
		super(self.__class__, self).__init__(*args, **kw)

	def getChunkText(self, text):
		if self.xml:
			tags = re.compile("(<([^>]*)>)")
			tags = [tag[1] for tag in tags.findall(self.xml.opening)] # We have here a list of xml tags with n="X" if there is one
			attr = re.compile('([a-zA-Z0-9.]+)((:\=")+([a-zA-Z1-9])(:+")+)*')

			string = []
			for tag in tags[-2:]:
				t = attr.findall(tag)
				if len(t) == 1:
					string.append(tag)
				else:
					xpath = t[0][0]
					t = [a[0] for a in t[1:]]
					t = zip(t[0::2], t[1::2])
					t = ['[@{0}="{1}"]'.format(a[0], a[1]) for a in t]
					z = t
					xpath += "".join(z)
					string.append(xpath)


			xpath = "//" + "/".join(string) + '/*[@unit="{0}"][@n="{1}"]/following-sibling::node()'.format(self.section.section, self.section.identifier)

			doc = libxml2.parseDoc(self.text.encode("utf-8"))
			ctxt = doc.xpathNewContext()
			div1 = ctxt.xpathEval(xpath)

			results = []
			for e in div1:
				if e.prop("unit") and e.prop("unit") == self.section.section:
					break
				results.append(e.getContent().replace("\t", ""))
			results = " ".join(results)
			return results
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