"""
"""
from Models import *

class SQL(object):
	def __init__(self, alias = "perseus"):
		clothoFolder = "../../../"
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
			self.con  = MySQLdb.connect('localhost', self.conf["MySQL"]["identifiers"]["user"], self.conf["MySQL"]["identifiers"]["password"], self.conf["MySQL"]['database'][alias], charset='utf8');
			print "Connected"
		except:
			print "Not connected"
			self.con = False

	def escape(self, string):
		""" Return a mysql escaped string

		keywords argument:
		string -- String to be escaped
		"""
		return MySQLdb.escape_string(string)

import copy

class SQLField(Field):
    def __new__(cls, F):
        return F

	def __init__(self, field):
		self = copy.deepcopy(field)
		print self

	def toSql(self):
		""" Transform a field into a CREATE readable string
		"""
		s = u"`" + self.name + u"` " + self.sqltype

		if self.parameter:
			s += u"(" + self.parameter + u")"

		if self.options:
			s += u" " + self.options

		return s

class SQLTable(Table):

	def check(self, forceCreate = False):
		with self.sql:
			cur = self.sql.cursor()
			cur.execute("SHOW TABLES LIKE \"%s\" ", [self.name])
			if len(cur.fetchall()) == 0:
				if forceCreate:
					return self.create()
				return False
			else:
				return True

	def create(self):
		with self.sql:
			cur = sql.sql.cursor()
			fields = [f.toSql for f in self.fields]
			fields += self.keys
			cur.execute("CREATE TABLE `%s` (%s) ENGINE=%s DEFAULT CHARSET=%s", [self.name, ", ".join(fields), self.engine, self.charset])

	def insert(self, data):
		""" Save a new morph

		keywords arguments
		data -- a dictionary with given fields name
		"""
		fieldName = ", ".join([field for field in data])
		fieldData = ", ".join([ '"' + data[field] + '"' for field in data])
		with self.sql:
			cur = self.sql.cursor()
			cur.execute("INSERT INTO `%s` (%s) VALUES (%s)", [self.name, fieldName, fieldData])
		self.con.commit()


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