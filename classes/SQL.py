#!/usr/bin/python
# -*- coding: utf-8 -*-


#Python CORE
import sys
import warnings

#Python Libraries
import MySQLdb

#Python Warning
warnings.filterwarnings("ignore", category = MySQLdb.Warning)

class SQL(object):
	def __init__(self, results = False, cache = False, web = False):
		try:
			self.debug = False
			if results == True:
				self.con  = MySQLdb.connect('localhost', 'perseus', 'perseus', 'clotho_results', charset='utf8');
			elif cache == True:
				self.con = MySQLdb.connect('localhost', 'perseus', 'perseus', 'clotho_cache', charset='utf8');
			elif web == True:
				self.con = MySQLdb.connect('localhost', 'perseus', 'perseus', 'clotho_web', charset='utf8');
			else:
				self.con = MySQLdb.connect('localhost', 'perseus', 'perseus', 'perseus2', charset='utf8');

			if self.debug:
				cur = self.con.cursor()
				cur.execute("SELECT VERSION()")
				ver = cur.fetchone()

		except:
			print "Not connected to DB"
			sys.exit()



	def escape(self, string):
		""" Return a mysql escaped string

		keywords argument:
		string -- String to be escaped
		"""
		return MySQLdb.escape_string(string)
		
	def resConnection(self):
		""" Test the connection to the MySQL DB "results"
		"""
		try:
			self.results  = MySQLdb.connect('localhost', 'perseus', 'perseus', 'results');

			if self.debug:
				cur = self.con.cursor()
				cur.execute("SELECT VERSION()")
				ver = cur.fetchone()

		except:
			print "Not connected to DB Results"

		return self.results


	def check(self):
		"""	Return a boolean indicating if this programm tables are presents
		"""
		with self.con:
			cur = self.con.cursor()
			req = "SHOW TABLES LIKE 'python_request' "
			cur.execute(req)
			if len(cur.fetchall()) == 0:
				return False
			else:
				return True

	def saveMorph(self, morph):
		""" Save a new morph

		keywords arguments
		morph -- a dictionary with a lemma key and a morph key
		"""
		with self.con:
			cur = self.con.cursor()
			req = "INSERT INTO `morph` (`lemma_morph`,`form_morph`) VALUES ('" + morph["lemma"] + "','" + morph["form"] + "');"
			cur.execute(req)
		self.con.commit()

	def create(self):
		""" Creates this software's MySQL tables
		"""
		with self.con:
			cur = self.con.cursor()
			pRequest = "CREATE TABLE IF NOT EXISTS `python_request` (  `id_request` int(11) NOT NULL AUTO_INCREMENT,  `mode_request` varchar(255) DEFAULT NULL,  `name_request` varchar(45) DEFAULT NULL,  PRIMARY KEY (`id_request`)) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8"
			pRequestTerm = "CREATE TABLE IF NOT EXISTS `python_request_term` (  `id_python_request_term` int(11) NOT NULL AUTO_INCREMENT,  `id_request` int(11) DEFAULT NULL,  `id_entity` int(11) DEFAULT NULL,  PRIMARY KEY (`id_python_request_term`)) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8"
			morph = "CREATE TABLE `morph` (`id_morph` int(11) NOT NULL AUTO_INCREMENT, `lemma_morph` varchar(100) CHARACTER SET utf8 DEFAULT NULL,  `form_morph` varchar(100) CHARACTER SET utf8 DEFAULT NULL,  PRIMARY KEY (`id_morph`),  UNIQUE KEY `index2` (`lemma_morph`,`form_morph`)) ENGINE=InnoDB DEFAULT CHARSET=utf8"
			cur.execute(pRequest)
			cur.execute(pRequestTerm)
			cur.execute(morph)


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

	def load(self, identifier = False):
		""" Returns a list of saved Clotho request or returns one and set it as the actual request

		keywords arguments
		identifier -- (Default false) When set, returns the parameters of a given query
		"""
		cur = self.con.cursor()

		if identifier == False:
			cur.execute("SELECT * FROM `python_request`")
			rows = cur.fetchall()
			return list(rows), len(rows)
		else:
			q = {
				"name" : "",
				"terms" : [],
				"mode" : ""
			}
			cur.execute("SELECT * FROM `python_request` WHERE id_request = ' " + str(identifier) + "' ")
			d = list(cur.fetchall())
			if len(d) == 1:
				q["name"] = d[0][2]
				q["mode"] = d[0][1].lower()

				cur.execute("SELECT * FROM `python_request_term` WHERE id_request = ' " + str(identifier) + "' ")
				d = list(cur.fetchall())
				for t in d:
					q["terms"].append(str(t[2]))

			return q


	def save(self, item):
		""" Save a clotho request

		keywords arguments
		item -- A dictionary with three parameters : a list of terms, a mode and a name
		"""
		with self.con:
			cur = self.con.cursor()
			cur.execute("INSERT INTO `python_request` (`mode_request`,`name_request`) VALUES ('" + item["mode"] + "','" + item["name"] + "');")
			
			lastId = self.con.insert_id()

			if lastId:
				for term in item["terms"]:
					cur.execute("INSERT INTO `python_request_term` (`id_request`,`lemma_request`) VALUES ('" + str(lastId) + "','" + str(term) + "')")
