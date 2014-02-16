#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys

try:
	import MySQLdb as mdb
except:
	print "MySQLdb not installed. \n apt-get install python-mysqldb"
	sys.exit()

class SQL(object):
	def __init__(self, results = False):
		try:
			self.debug = False
			if results:
				self.con  = mdb.connect('localhost', 'perseus', 'perseus', 'results');

			else:
				self.con = mdb.connect('localhost', 'perseus', 'perseus', 'perseus2');

			if self.debug:
				cur = self.con.cursor()
				cur.execute("SELECT VERSION()")
				ver = cur.fetchone()

		except:
			print "Not connected to DB"
			sys.exit()



	def escape(self, string):
		return mdb.escape_string(string)
		
	def resConnection(self):
		try:
			self.results  = mdb.connect('localhost', 'perseus', 'perseus', 'results');

			if self.debug:
				cur = self.con.cursor()
				cur.execute("SELECT VERSION()")
				ver = cur.fetchone()

		except:
			print "Not connected to DB Results"

		return self.results


	def check(self):
		with self.con:
			cur = self.con.cursor()
			req = "SHOW TABLES LIKE 'python_request' "
			cur.execute(req)
			if len(cur.fetchall()) == 0:
				return False
			else:
				return True

	def saveMorph(self, morph):
		with self.con:
			cur = self.con.cursor()
			req = "INSERT INTO `morph` (`lemma_morph`,`form_morph`) VALUES ('" + morph["lemma"] + "','" + morph["form"] + "');"
			cur.execute(req)
		self.con.commit()

	def create(self):
		with self.con:
			cur = self.con.cursor()
			pRequest = "CREATE TABLE IF NOT EXISTS `python_request` (  `id_request` int(11) NOT NULL AUTO_INCREMENT,  `mode_request` varchar(255) DEFAULT NULL,  `name_request` varchar(45) DEFAULT NULL,  PRIMARY KEY (`id_request`)) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8"
			pRequestTerm = "CREATE TABLE IF NOT EXISTS `python_request_term` (  `id_python_request_term` int(11) NOT NULL AUTO_INCREMENT,  `id_request` int(11) DEFAULT NULL,  `id_entity` int(11) DEFAULT NULL,  PRIMARY KEY (`id_python_request_term`)) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8"
			morph = "CREATE TABLE `morph` (`id_morph` int(11) NOT NULL AUTO_INCREMENT, `lemma_morph` varchar(100) CHARACTER SET utf8 DEFAULT NULL,  `form_morph` varchar(100) CHARACTER SET utf8 DEFAULT NULL,  PRIMARY KEY (`id_morph`),  UNIQUE KEY `index2` (`lemma_morph`,`form_morph`)) ENGINE=InnoDB DEFAULT CHARSET=utf8"
			cur.execute(pRequest)
			cur.execute(pRequestTerm)
			cur.execute(morph)


	def lemma(self, query, numeric = False):
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
		data = []
		cur = self.con.cursor()
		cur.execute("SELECT * FROM perseus.hib_chunks WHERE id='" + query + "'")

		row = list(cur.fetchone())

		return row, len(row)

	def metadata(self, query):
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
		data = []
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
				q["name"] = d[0][1]
				q["mode"] = d[0][2]

				cur.execute("SELECT * FROM `python_request_term` WHERE id_request = ' " + str(identifier) + "' ")
				d = list(cur.fetchall())
				for t in d:
					q["terms"].append(str(t[2]))

			return q


	def save(self, item):
		with self.con:
			cur = self.con.cursor()
			cur.execute("INSERT INTO `python_request` (`mode_request`,`name_request`) VALUES ('" + item["mode"] + "','" + item["name"] + "');")
			
			lastId = self.con.insert_id()

			if lastId:
				for term in item["terms"]:
					cur.execute("INSERT INTO `python_request_term` (`id_request`,`id_entity`) VALUES ('" + str(lastId) + "','" + str(term) + "')")
