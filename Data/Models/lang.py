#!/usr/bin/python
# -*- coding: utf-8 -*-

class Form(object):
	def __init__(self, uid = None, text = None, lemma = None):
		if isinstance(uid, basestring):
			self.uid = uid
		if isinstance(uid, int):
			self.uid = str(uid)
		if isinstance(text, basestring):
			self.text = text
		if isinstance(lemma, list):
			self.lemma = [l for l in lemma if isinstance(l, Lemma)]

	def toString(self):
		return self.text

	def length(self):
		return len([l for l in self.lemma if isinstance(l, Lemma)])

class Lemma(object):
	def __init__(self, uid = None, text = None, definition = None):
		self.uid = None
		self.text = None
		self.definition = None
		if isinstance(uid, basestring):
			self.uid = uid
		elif isinstance(uid, int):
			self.uid = str(uid)
		if isinstance(text, basestring):
			self.text = text
		if isinstance(definition, basestring):
			self.definition = definition

	def toString(self):
		return self.text