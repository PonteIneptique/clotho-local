#!/usr/bin/python
# -*- coding: utf-8 -*-

CONSTANT_DATA_STORAGE = "MySQL"
import sys, os
import xml

sys.path.append("../..")

from Data import Models
from Linguistic.Lemma.form import Finder as FormFinder
from Services.Perseus.Common import Chunk
from Data import Tools

if CONSTANT_DATA_STORAGE == "MySQL":
	from Data import MySQL

	Table = MySQL.Table
	Field = MySQL.Field
	Connection = MySQL.Connection

class Config(object):
	def __init__(self, connection = None, path = None, tables = []):
		if path:
			self.Connection = Connection(path = path)
		else:
			self.Connection = Connection()

		self.dictionnary = Table(Models.storage.Table("hib_lemmas", [
				Models.storage.Field("lemma_id", {"int" : "11"}),
				Models.storage.Field("lemma_text", {"text" : None}),
				Models.storage.Field("lemma_short_def", {"text" : None})
			]), connection = self.Connection)
		#self.dictionnary should be altered to 
		"""
			ALTER TABLE `clotho2_perseus`.`hib_lemmas` 
			CHANGE COLUMN `lemma_id` `lemma_id` INT(11) NOT NULL AUTO_INCREMENT ;
		"""

		self.entities = Table(Models.storage.Table("hib_entities"), connection = self.Connection)

		self.frequencies = Table(Models.storage.Table("hib_frequencies"), connection = self.Connection)

		self.chunks = Table(Models.storage.Table("hib_chunks"), connection = self.Connection)

		self.morph = Table(Models.storage.Table("morph"), connection = self.Connection)

		self.tables = [self.dictionnary, self.entities, self.frequencies, self.chunks, self.morph]
		self.check(tables)

	def check(self, tables = []):
		for table in self.tables:
			if table.name in tables:
				assert table.check(), "No table for {0}".format(table.name)

class LatinFormFinder(FormFinder):
	def __init__(self):
		self.file = Tools.download.File("https://github.com/jfinkels/hopper/raw/master/xml/data/latin.morph.xml", "/morph", "latin.morph.xml")
		self.table = Table(
						table = Models.storage.Table(
							"morph", 
							fields = [
								#Legacy
								Models.storage.Field("id_morph", {"int" : "11"}, "NOT NULL AUTO_INCREMENT"),
								Models.storage.Field("lemma_morph", {"varchar" : "100"}, "CHARACTER SET utf8 DEFAULT NULL"),
								Models.storage.Field("form_morph", {"varchar" :"100"}, "CHARACTER SET utf8 DEFAULT NULL"),
								#New
								Models.storage.Field("pos", {"varchar" :"20"}, "CHARACTER SET utf8 DEFAULT NULL"),
								Models.storage.Field("number", {"varchar" :"20"}, "CHARACTER SET utf8 DEFAULT NULL"),
								Models.storage.Field("gender", {"varchar" :"20"}, "CHARACTER SET utf8 DEFAULT NULL"),
								Models.storage.Field("case", {"varchar" :"20"}, "CHARACTER SET utf8 DEFAULT NULL")

							], 
							keys = ["PRIMARY KEY (`id_morph`)"]
						), 
						connection =Config().Connection
					)

		pass

	def install(self):
		data = {"lemma_morph" : "", "form_morph" : "", "pos" : "", "number" :"", "gender" : "", "case" : ""}
		for event, elem in xml.etree.cElementTree.iterparse(self.file.path):
			if elem.tag == "analysis":
				for child in elem:
					if child.tag == "lemma":
						data["lemma_morph"] = child.text
					elif child.tag == "form":
						data["form_morph"] = child.text
					elif child.tag == "pos":
						data["pos"] = child.text
					elif child.tag == "number":
						data["number"] = child.text
					elif child.tag == "gender":
						data["gender"] = child.text
					elif child.tag == "case":
						data["case"] = child.text
				try:
					self.table.insert(data)
				except Exception as e:
					print e
					continue
		return self.table.length()

	def check(self):
		self.file.check(force = True)
		self.table.check(forceCreate = True)
		self.table.columns()
		if self.table.length() == 0:
			try:
				self.install()
			except Exception as e:
				print e
		return False

	def getForms(self, Lemma):
		lemma_form = self.table.select(
						[ Models.storage.Condition("form_morph", Lemma.text, "=") ], 
						select = ["lemma_morph"], 
						limit = None
					)

		conditions = [Models.storage.Condition("lemma_morph", morph["lemma_morph"], "=", "OR") for morph in lemma_form]
		if len(conditions) > 0:
			conditions[len(conditions) - 1 ].next = ""

		data = self.table.select(conditions, limit = None)
		
		return [Models.lang.Form(uid = f["id_morph"], text = f["form_morph"], lemma = Lemma, pos = f["pos"], number = f["number"], gender = f["gender"], case = f["case"]) for f in data]

class Lemma(Models.lang.Lemma):
	def __init__(self):
		self.config = Config(tables = ["hib_lemmas", "morphs"])

	def flection(self):
		self.config = Config(tables = ["hib_morph"])

	def search(self, w, uid = False, limit = 30, strict = False):
		if uid:
			conditions = [Models.storage.Condition("lemma_id", w, "=")]
		elif strict:
			conditions = [Models.storage.Condition("lemma_text", w, "=")]
		else:
			conditions = [Models.storage.Condition("lemma_text", "%{0}%".format(w), "LIKE")]

		lemmas = self.config.dictionnary.select(conditions, ["lemma_id", "lemma_text", "lemma_short_def"])

		return [Models.lang.Lemma(uid = lemma["lemma_id"], text = lemma["lemma_text"], definition = lemma["lemma_short_def"]) for lemma in lemmas]

	def new(self, lemma):
		if not(isinstance(lemma, Models.lang.Lemma)):
			raise TypeError("Lemma is not an instance of Models.lang.Lemma")
		data = {
			"lemma_text" : lemma.toString(),
			"lemma_short_def" : lemma.definition
		}
		if lemma.uid:
			data["lemma_id"] = lemma.uid
		return self.config.dictionnary.insert(data)

	def remove(self, lemma):
		if not(isinstance(lemma, Models.lang.Lemma)):
			raise TypeError("Lemma is not an instance of Models.lang.Lemma")
		conditions = []
		if lemma.uid:
			conditions.append(Models.storage.Condition("lemma_id", lemma.uid, "=", "AND"))
		if lemma.text:
			conditions.append(Models.storage.Condition("lemma_text", lemma.text, "=", "AND"))
		if lemma.definition:
			conditions.append(Models.storage.Condition("lemma_short_def", lemma.definition, "="))

		return self.config.dictionnary.delete(conditions, limit = 100)

class Occurence(object):
	def __init__(self):
		self.config = Config(tables = ["hib_entities", "hib_frequencies"])

	def search(self, lemma):
		if not(isinstance(lemma, Models.lang.Lemma)):
			raise TypeError("Lemma is not an instance of Models.lang.Lemma")
		
		condition = [
			Models.storage.Condition("entity_type", "lemma", "=", "AND"),
			Models.storage.Condition("display_name", lemma.toString(), "=")
		]

		results = self.config.entities.select(where = condition, select = ["id"], limit = 1)
		if len(results) == 0:
			return []

		condition = [
			Models.storage.Condition("entity_id", results[0]["id"], "=", "AND"),
			Models.storage.Condition("chunk_id", "", "!=")
		]

		results = self.config.frequencies.select(where = condition, select = ["chunk_id"])#DEBUG, limit = 10)

		chunks = []
		for result in results:
			c = self.config.chunks.select([Models.storage.Condition("id", result["chunk_id"], "=")], select = ["id", "document_id", "type", "value", "position", "abs_position", "open_tags", "close_tags", "start_offset", "end_offset"])
			if len(c) == 0:
				raise ValueError("A chunk is missing in the database")
			c = c[0]
			chunks.append(
				Models.documents.Occurence(
					#uid = c["id"], 
					#document = Models.documents.Text(uid = c["document_id"]), 
					lemma = lemma,
					chunk = Chunk(
						uid = c["id"], 
						document = Models.documents.Text(uid = c["document_id"]),
						section = Models.documents.Section(
							section = c["type"], 
							identifier = c["value"], 
							position = c["position"], 
							absolute_position = c["abs_position"]
						), 
						xml = Models.documents.XmlChunk(
							opening = c["open_tags"], 
							closing = c["close_tags"]
						),
						offset = Models.documents.Offset(
							start = c["start_offset"],
							end = c["end_offset"]
						)
					)
				)
			)
		return chunks
