#!/usr/bin/python
# -*- coding: utf-8 -*-

import Models
import MySQLdb
import MySQLdb.cursors 
import pickle
SQL_DATA_TYPE = ["int", "varchar", "text"]

class Connection(object):
	def __init__(self, alias = "perseus", path = None):
		clothoFolder = "../../../"
		if isinstance(path, basestring):
			clothoFolder = path
		self.debug = False

		"""
		We need to load values from our config
		"""
		try:
			#Config filename
			filename = clothoFolder + "cache/setup.pickle"
			with open(filename, "rb") as f:
				self.conf = pickle.load(f)
				f.close()
		except:
			print "No configuration for SQL"

		try:
			self.con  = MySQLdb.connect(
				'localhost', 
				self.conf["MySQL"]["identifiers"]["user"], 
				self.conf["MySQL"]["identifiers"]["password"], 
				self.conf["MySQL"]['database'][alias], 
				charset='utf8');
		except:
			self.con = False

	def escape(self, string):
		""" Return a mysql escaped string

		keywords argument:
		string -- String to be escaped
		"""
		return MySQLdb.escape_string(string)

import copy

class Field(Models.storage.Field):
	def __init__(self, field = None):
		if isinstance(field, Models.storage.Field):
			self.name = field.name
			self.options = field.options
			self.parameters = field.parameters

	def toString(self):
		""" Transform a field into a CREATE readable string
		"""
		s = u"`" + self.name + u"` "

		if self.parameters:
			for p in self.parameters:
				if p in SQL_DATA_TYPE:
					if self.parameters[p]:
						s += u"".join([" ", p, "(", self.parameters[p], ") "])
					else:
						s += u"".join([" ", p, " "])

		if self.options:
			s += u" " + self.options

		return s

class Table(Models.storage.Table):
	def __init__(self, table = None, connection = None):
		self.Table(table)
		self.Connection(connection)

	def Table(self, table):
		if isinstance(table, Models.storage.Table):
			self.fields = [Field(f) for f in table.fields]
			self.name = table.name
			self.keys = table.keys
			self.engine = table.engine
			self.charset = table.charset

	def Connection(self, connection):
		if not isinstance(connection, Connection):
			raise TypeError("SQL Object is not a correct MySQL.Connection instance")
		else:
			self.instance = connection
			self.connection = self.instance.con

	def ConditionsToWhere(self, req, where = []):
		if len(where) > 0:
			req_where = ""
			for w in where:
				if not isinstance(w, Models.storage.Condition):
					raise TypeError("One of the condition is not a Models.storage.Condition instance")
				req_where += " `{0}` {1} %s {2}".format(w.field, w.condition, w.next)
			req += " WHERE " + req_where

			return req
		else:
			return ""

	def check(self, forceCreate = False):
		with self.connection:
			cur = self.connection.cursor()
			cur.execute("SHOW TABLES LIKE %s ", [self.name])
			if len(cur.fetchall()) == 0:
				if forceCreate:
					return self.create()
				return False
			else:
				return True
		return False

	def create(self):
		with self.connection:
			cur = self.connection.cursor()
			fields = [f.toString() for f in self.fields]
			fields += self.keys
			try:
				cur.execute("CREATE TABLE `"+ self.name +"` ( " + ", ".join(fields) + ") ENGINE="+self.engine+" DEFAULT CHARSET=" + self.charset)
				return True
			except:
				return False
		return False

	def length(self):
		#SELECT COUNT(*) as count FROM clotho2_perseus.morph;
		with self.connection:
			cur = self.connection.cursor()
			try:
				cur.execute("SELECT COUNT(*) FROM {0}".format(self.name))
			except:
				return 0
			try:
				return cur.fetchone()[0]
			except:
				return 0
		return 0

	def insert(self, data):
		""" Do a insert query

		keywords arguments
		data -- a dictionary with given fields name
		"""
		fieldName = ", ".join(["`%s`" % field for field in data])
		fieldData = ", ".join([ '"' + data[field] + '"' for field in data])
		with self.connection:
			cur = self.connection.cursor()
			req = "INSERT INTO `{0}` ({1}) ".format(self.name, fieldName)
			try:
				cur.execute(req + " VALUES ({0})".format(" ,".join([" %s " for field in data])), [data[field] for field in data])
				try:
					return self.connection.insert_id()
				except:
					return True
			except:
				return False
		self.connection.commit()

	def drop(self):
		with self.connection:
			cur = self.connection.cursor()
			req = "DROP TABLE %s" % self.name
			try:
				cur.execute(req)
				return True
			except:
				return False

		return False

	def select(self, where = [], select = []):
		"""	Where as to be designed this way :
			[{
				"field" : "",
				"equality" : None or something in WHERE_ACCEPTED,
				"value" : "",
				"next" : None
			}]
		"""
		if len(select) > 0:
			req = "SELECT {0} FROM `{1}` ".format(",".join([str(s) for s in select]), self.name)
		else:
			req = "SELECT * FROM `{0}` ".format(self.name)

		if len(where) > 0:
			with self.connection:
				cur = MySQLdb.cursors.DictCursor(self.connection)
				cur.execute(self.ConditionsToWhere(req, where), [w.value for w in where])
		else:
			with self.connection:
				cur = MySQLdb.cursors.DictCursor(self.connection)
				cur.execute(req)

		return list(cur.fetchall())

	def select(self, where = [], select = [], limit = 30):
		"""	WHERE -> Models.storage.Condition
		"""
		if len(select) > 0:
			req = "SELECT {0} FROM `{1}` ".format(",".join([str(s) for s in select]), self.name)
		else:
			req = "SELECT * FROM `{0}` ".format(self.name)

		if len(where) > 0:
			with self.connection:
				cur = MySQLdb.cursors.DictCursor(self.connection)
				cur.execute(self.ConditionsToWhere(req, where) + " LIMIT {0}".format(limit), [w.value for w in where])
		else:
			with self.connection:
				cur = MySQLdb.cursors.DictCursor(self.connection)
				cur.execute(req + " LIMIT {0}".format(limit))

		return list(cur.fetchall())

	def delete(self, where = [], limit = 1):
		"""	WHERE -> Models.storage.Condition
		"""
		req = "DELETE FROM `{0}` ".format(self.name)

		if len(where) > 0:
			with self.connection:
				cur = MySQLdb.cursors.DictCursor(self.connection)
				try:
					cur.execute(self.ConditionsToWhere(req, where) + " LIMIT {0}".format(limit), [w.value for w in where])
					return True
				except:
					return False
		else:
			with self.connection:
				cur = MySQLdb.cursors.DictCursor(self.connection)
				try:
					cur.execute(req + " LIMIT {0}".format(limit))
					return True
				except:
					return False

		return False


	"""
	Has to be turned to something else
	"""
	def lemma(self, query, numeric = False):
		""" Return a dictionary where the key is a numeric identifier and the value is a list
		where the data are the lemma unique identifier, lemma's text, the bare headword and the lemma short definition

		key arguments
		query -- A string or an int refering to the lemma identifier or spelling
		numeric -- a boolean indicating if the query is a numeric identifier

		"""
		data = {}
		cur = self.con.cursor()
		if numeric == False:
			cur.execute("SELECT lemma_id, lemma_text, bare_headword, lemma_short_def FROM hib_lemmas WHERE lemma_text LIKE '" + query + "'")
		else:
			cur.execute("SELECT lemma_id, lemma_text, bare_headword, lemma_short_def FROM hib_lemmas WHERE lemma_id = '" + str(query) + "'")

		rows = cur.fetchall()

		i = 0
		for row in rows:
			data[i] = list(row)
			i += 1

		return data, len(rows)

	def chunk(self, query):
		""" Return MySQL data about a chunk

		keywords arguments
		query --- The id of an element
		"""
		cur = self.con.cursor()
		cur.execute("SELECT * FROM perseus.hib_chunks WHERE id='" + query + "'")

		row = list(cur.fetchone())

		return row, len(row)

	def metadata(self, query):
		""" Return a 2-tuple where the first element is a list of metadata and the second the number of different metadata crawled

		keywords arguments
		query -- The Perseus document string identifier 
		"""
		data = []
		cur = self.con.cursor()
		cur.execute("SELECT key_name, value FROM perseus.metadata WHERE document_id='" + query + "'")

		rows = cur.fetchall()

		i = 0
		for row in rows:
			data.append(list(row))
			i += 1

		return data, len(rows)

	def occurencies(self, query):
		""" For a given word, returns a list of occurences and its number

		keywords arguments
		query -- A lemma
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