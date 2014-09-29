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
	def __init__(self, connection = None, path = None):
		if path:
			self.Connection = Connection(path = path)
		elif 'global_path' in globals():
			self.Connection = Connection(path = global_path)
		else:
			self.Connection = Connection(path ="../../")

		self.dictionnary = Table(Models.storage.Table("hib_lemmas", [
				Models.storage.Field("lemma_id", {"int" : "11"}),
				Models.storage.Field("lemma_text", {"text" : None}),
				Models.storage.Field("lemma_short_def", {"text" : None})
			]), connection = self.Connection)

		self.check()

	def check(self):
		assert self.dictionnary.check(), "No table for dictionnary"

class Lemma(lang.Lemma):
	def __init__(self):
		self.config = Config()

	def search(self, w, uid = False, limit = 30, strict = False):
		if uid:
			conditions = [Models.storage.Condition("lemma_id", w, "=")]
		elif strict:
			conditions = [Models.storage.Condition("lemma_text", w, "=")]
		else:
			conditions = [Models.storage.Condition("lemma_text", "%{0}%".format(w), "LIKE")]

		lemmas = self.config.dictionnary.select(conditions, ["lemma_id", "lemma_text", "lemma_short_def"])

		return [Models.lang.Lemma(uid = lemma["lemma_id"], text = lemma["lemma_text"], definition = lemma["lemma_short_def"]) for lemma in lemmas]


l = Lemma()
lemmas = l.search("habeo")
for lemma in lemmas:
	print lemma.toString()