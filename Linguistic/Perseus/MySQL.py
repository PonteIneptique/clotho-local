#!/usr/bin/python
# -*- coding: utf-8 -*-

CONSTANT_DATA_STORAGE = "MySQL"
import sys, os

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
		else:
			self.Connection = Connection()

		self.dictionnary = Table(Models.storage.Table("hib_lemmas", [
				Models.storage.Field("lemma_id", {"int" : "11"}),
				Models.storage.Field("lemma_text", {"text" : None}),
				Models.storage.Field("lemma_short_def", {"text" : None})
			]), connection = self.Connection)

		self.entities = Table(Models.storage.Table("hib_entities"), connection = self.Connection)
		#self.dictionnary should be altered to 
		"""
			ALTER TABLE `clotho2_perseus`.`hib_lemmas` 
			CHANGE COLUMN `lemma_id` `lemma_id` INT(11) NOT NULL AUTO_INCREMENT ;
		"""
		self.check()

	def check(self):
		assert self.dictionnary.check(), "No table for hib_dictionnary"
		assert self.entities.check(), "No table hib_entities"

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
		pass

	def search(self, lemma):
		if not(isinstance(lemma, Models.lang.Lemma)):
			raise TypeError("Lemma is not an instance of Models.lang.Lemma")
		raise NotImplementedError()
		
		condition = [
			Models.storage.Condition("entity_type", "lemma", "=", "AND"),
			Models.storage.Condition("display_name", lemma.toString(), "=")
		]
		"""

		| id            | int(11)      | NO   | PRI | NULL    | auto_increment |

		| document_id   | varchar(50)  | YES  | MUL | NULL    |                |

		| type          | varchar(30)  | YES  |     | NULL    |                |
		| value         | varchar(250) | YES  |     | NULL    |                |
		| position      | int(11)      | YES  |     | NULL    |                |
		| abs_position  | int(11)      | YES  |     | NULL    |                |

		| open_tags     | text         | YES  |     | NULL    |                |
		| close_tags    | text         | YES  |     | NULL    |                |

		| start_offset  | int(11)      | YES  |     | NULL    |                |
		| end_offset    | int(11)      | YES  |     | NULL    |                |

		| head          | text         | YES  |     | NULL    |                |
		"""
		data = []
		cur = self.con.cursor()

		#We retrieve the entity_id before going further
		cur.execute("SELECT id FROM hib_entities WHERE entity_type = 'Lemma' and display_name='"+query+"'")
		i = cur.fetchone()
		i = i[0]


		cur.execute("SELECT chunk_id FROM hib_frequencies WHERE entity_id = '" + str(i) + "' AND chunk_id != ''")

		rows = cur.fetchall()

		for row in rows:
			data.append(str(list(row)[0]))

		return data, len(rows)