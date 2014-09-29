#!/usr/bin/python
# -*- coding: utf-8 -*-

CONSTANT_DATA_STORAGE = "MySQL"
import sys

sys.path.append("../..")
from Data import Models
import Linguistic.lang as lang

if CONSTANT_DATA_STORAGE == "MySQL":
	from Data import MySQL

	Table = MySQL.Table
	Field = MySQL.Field
	Connection = MySQL.Connection

class Config(object):
	def __init__(self):
		#"SELECT lemma_id, lemma_text, bare_headword, lemma_short_def FROM hib_lemmas WHERE lemma_text LIKE '" + query + "'"
		self.dictionnary = Table(Models.storage.Table("hib_lemmas", [
				Models.storage.Field("lemma_id", {"int" : "11"}),
				Models.storage.Field("lemma_text", {"text" : None})
			]))
	def check(self):
		self.dictionnary.check()

class Lemma(lang.Lemma):
	def __init__(self):
		self.config = Config()
	def search(self, w):
		pass

l = Lemma()
l.search("w")