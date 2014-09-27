#!/usr/bin/python
# -*- coding: utf-8 -*-

from field import *

class DataTable:
	pass

class Table(DataTable):
	def __init__(self, name, sql_conn = None, fields = [], keys = [], engine  = False, charset = False):

		self.fields = []
		self.name = ""
		self.keys = []
		self.engine = "InnoDB"
		self.charset = "utf8"

		if isinstance(name, basestring) and not isinstance(name, unicode):
			name = unicode(name)
		if isinstance(name, unicode):
			self.name = name
		else:
			raise TypeError("Given name for the Table object is not a string")

		if sql_conn:
			try:
				self.setCon()
			except e:
				print e

		if isinstance(engine, basestring):
			self.engine = engine
		if isinstance(charset, basestring):
			self.charset = charset

		if not isinstance(fields, list):
			raise TypeError("Given fields is not a list")
		if len(fields) > 0:
			self.setFields(fields)

	def setCon(self, con):
		if not isinstance(con, MySQLdb.connections.Connection):
			raise TypeError("SQL Object is not a correct MySQLdb.connections.Connection instance")
		else:
			self.sql = con

	def setFields(self, fields = []):
		if not isinstance(fields, list):
			raise TypeError("Given fields is not a list")
		if len(fields) == 0:
			raise ValueError("Given list of fields is empty")

		for field in fields:
			self.addField(field)

	def addField(self,field):
		if field.name in [f.name for f in self.fields]:
			raise ValueError("A field with the name " + field.name + " already exists")
		self.fields.append(field)

