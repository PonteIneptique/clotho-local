#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import time
import os
import sys

sys.path.append("../..")


from Data.Models import *
from Exporter.common import Model as ExporterModel


class RCorpus(ExporterModel):
	def __init__(self, OccurenceSetList, folder = "./data/corpus/"):
		self.OccurenceSetList = OccurenceSetList
		self.folder = folder
		if not os.path.exists(folder):
			os.makedirs(folder)


	def write(self):
		for OccurenceSet in self.OccurenceSetList:
			with codecs.open("{0}{1}-{2}.txt".format(self.folder, OccurenceSet.lemma.toString(), time.strftime("%Y-%m-%d.%H-%M")), "w") as f:
				f.write("\n".join([Occurence.lemmatizedToString() for Occurence in OccurenceSet.occurences]))
				f.close()
		return True