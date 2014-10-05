#!/usr/bin/python
# -*- coding: utf-8 -*-

class Form(object):
	def __init__(self, uid = None, text = None, lemma = None, pos = None, number = None, gender = None, case = None):
		self.uid = None
		self.text = None
		self.lemma = []
		self.pos = None
		self.number = None
		self.gender = None
		self.case = None

		if isinstance(uid, basestring):
			self.uid = uid
		if isinstance(uid, int):
			self.uid = str(uid)
		if isinstance(text, basestring):
			self.text = text
		if isinstance(lemma, list):
			self.lemma = [l for l in lemma if isinstance(l, Lemma)]
		if isinstance(pos, basestring):
			self.pos = pos
		if isinstance(number, basestring):
			self.number = number
		if isinstance(gender, basestring):
			self.gender = gender
		if isinstance(case, basestring):
			self.case = case


	def toString(self):
		return self.text

	def length(self):
		return len([l for l in self.lemma if isinstance(l, Lemma)])

class Lemma(object):
	def __init__(self, uid = None, text = None, definition = None, forms = None):
		self.uid = None
		self.text = None
		self.definition = None
		self.forms = None
		self.formStringList = None
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

	def getFormStringList(self):
		if not self.formStringList:
			self.formStringList = [form.toString() for form in self.forms]
		return self.formStringList