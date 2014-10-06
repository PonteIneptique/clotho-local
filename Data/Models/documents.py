#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys 
sys.path.append("../..")

from Data.Models import lang

class Text(object):
	def __init__(self, uid = None, metadata = None):
		if isinstance(uid, basestring):
			self.uid = uid
		if isinstance(metadata, dict):
			self.metadata = metadata

	def property(self, key = None, value = None, metadata = None):
		if isinstance(metadata, dict):
			for key in metadata:
				self.metadata[key] = metadata[key]
		if key and isinstance(key, basestring) and value:
			self.metadata[key] = value

class XmlChunk(object):
	def __init__(self, opening = None, closing = None):
		self.opening = None
		self.closing = None

		if isinstance(opening, basestring):
			self.opening = opening
		else:
			raise TypeError("Opening is not a string")

		if isinstance(closing, basestring):
			self.closing = closing
		else:
			raise TypeError("Closing is not a string")

	def wrapper(self):
		return self.opening + self.closing

class Section(object):
	def __init__(self, section, identifier, position = None, absolute_position = None):
		self.section = section
		self.identifier = identifier

		if isinstance(position, basestring) or isinstance(position, long):
			self.position = position

		if isinstance(absolute_position, basestring) or isinstance(absolute_position, long):
			self.absolute_position = absolute_position

	def toString(self):
		return self.section + " " + self.identifier

	def toXml(self):
		return '<{0} id="{1}" />'.format(self.section, self.identifier)

class Offset(object):
	def __init__(self, start, end):
		self.start = start
		self.end = end

class Chunk(object):
	def __init__(self, uid = None, document = None, section = None, xml = None, offset = None):
		self.uid = None
		self.document = None
		self.xml = None
		self.section = None
		self.offset = None

		if uid:
			self.uid = uid

		if isinstance(document, Text):
			self.document = document
		else:
			raise TypeError("Document is not a Models.documents.Text")

		if isinstance(section, Section):
			self.section = section
		elif section:
			raise TypeError("Section is not a Models.documents.Section")

		if isinstance(xml, XmlChunk):
			self.xml = xml
		elif xml:
			raise TypeError("Xml is not a Models.documents.XmlChunk")

		if isinstance(offset, Offset):
			self.offset = offset
		elif offset:
			raise TypeError("Offset is not a Models.documents.Offset")

	def getText(self):
		#Should return a String
		raise NotImplementedError()


class Occurence(object):
	def __init__(self, text = None, lemma = None, form = None, chunk = None, augmented = None, lemmatized = []):
		self.text = None
		self.lemma = None
		self.form = None
		self.chunk = None
		self.augmented = None #The text but in augmented form like XML or so
		self.lemmatized = [] #A list of forms with Lemma in there

		if isinstance(chunk, Chunk) and not isinstance(text, basestring):
			self.text = chunk.getText()
			self.chunk = text
		elif isinstance(text, basestring):
			self.text = text
			self.chunk = None
		else:
			raise ValueError("There is not text or chunk available for this occurence")

		if isinstance(lemma, lang.Lemma):
			self.lemma = lemma
		else:
			raise TypeError("Lemma is not a Models.lang.Lemma")

		if isinstance(form, lang.Form):
			self.form = form
		elif not form:
			self.form = None
		else:
			raise TypeError("Form is not a Models.lang.Form")

	def toString(self):
		return self.text

	def lemmatizedToString(self):
		forms = []
		for word in self.lemmatized: #Getting a list of form for each word
			f = []
			for form in word:
				f += [lemma.text for lemma in form.lemma]
			forms += list(set([lemma for lemma in f]))
		return " ".join(forms)