#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import time
import sys

sys.path.append("../..")

class Model(object):
	def __init__(self, OccurenceSetList, folder = "./"):
		self.OccurenceSetList = OccurenceSetList
		self.folder = folder

	def write(self):
		raise NotImplementedError("Write is not implemented")