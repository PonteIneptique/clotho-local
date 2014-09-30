#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys 
sys.path.append("../..")
import Data.Models.lang

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
	def __init__(self, uid = None, opening = None, closing = None):
		self.uid = None
		self.opening = None
		self.closing = None

		if isinstance(uid, basestring) or isinstance(uid, int):
			self.uid = str(uid)
		else:
			raise TypeError("Uid is not a string or an int")

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
	def __init__(self, uid = None, document = None, xml = None):
		self.uid = None

		self.document = None
		self.section = None
		self.offset = None

	def getText(self):
		#Should return a String
		raise NotImplementedError()


class Occurence(object):
	def __init__(self, text = None, lemma = None, form = None, chunk = None):
		self.text = None
		self.lemma = None
		self.form = None
		self.chunk = None

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

		if isinstance(form, lang.form):
			self.form = form
		else:
			raise TypeError("Form is not a Models.lang.Form")

		pass
