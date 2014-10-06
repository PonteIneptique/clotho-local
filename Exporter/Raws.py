#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import time
import sys

sys.path.append("../..")


from Data.Models import *
from Exporter.common import model


class RCorpus(object):
	def __init__(self, OccurenceSetList, folder = "./"):
		self.OccurenceSetList = OccurenceSetList
		self.folder = folder

	def write(self):
		for OccurenceSet in self.OccurenceSetList:
			with codecs.open("{0}data/corpus/{1}-{2}.txt".format(self.folder, self.OccurenceSet.lemma.toString(), time.strftime("%Y-%m-%d.%H-%M")), "w") as f:
				f.write(" ".join([Occurence.lemmatizedToString() for Occurence in OccurenceSet.occurences]))
				f.close()
		return True