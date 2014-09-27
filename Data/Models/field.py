#!/usr/bin/python
# -*- coding: utf-8 -*-
class DataField:
	pass

class Field(DataField):
	def __init__(self, name, parameters = None, options = None):
		print name
		if isinstance(name, basestring) and not isinstance(name, unicode):
			name = unicode(name)
		if isinstance(name, unicode):
			self.name = name
		else:
			raise TypeError("Given name for the Field object is not a string")
		if len(name) == 0:
			raise ValueError("Field name is invalid")

		if options and not isinstance(options, basestring):
			raise TypeError("Options is not a basestring")

		if parameters and not isinstance(parameters, dict):
			raise TypeError("parameter is not a basestring")

		self.options = options
		self.parameters = parameters