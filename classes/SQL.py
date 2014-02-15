#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys

try:
	import MySQLdb as mdb
except:
	print "MySQLdb not installed. \n apt-get install python-mysqldb"
	sys.exit()

class SQL(object):
	def __init__(self):
		try:
			self.debug = True
			self.con = mdb.connect('localhost', 'perseus', 'perseus', 'perseus');

			if self.debug:
				cur = self.con.cursor()
				cur.execute("SELECT VERSION()")
				ver = cur.fetchone()
				print "Database version : %s " % ver

		except:
			print "Not connected to DB"

	def lemma(self, query, numeric = False):
		data = {}
		cur = self.con.cursor()
		if numeric == False:
			cur.execute("SELECT id, display_name, max_occ FROM hib_entities WHERE entity_type = 'Lemma' AND display_name LIKE '" + query + "'")
		else:
			cur.execute("SELECT id, display_name, max_occ FROM hib_entities WHERE entity_type = 'Lemma' AND id = '" + str(query) + "'")

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

		rows = cur.fetchall()

		rows = list(rows[0])

		return rows, len(rows)

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
		cur.execute("SELECT chunk_id FROM hib_frequencies WHERE entity_id = '" + query + "' AND chunk_id != ''")

		rows = cur.fetchall()

		for row in rows:
			data.append(str(list(row)[0]))

		return data, len(rows)

	def load(self, identifier = False):
		data = []
		cur = self.con.cursor()

		if identifier == False:
			cur.execute("SELECT * FROM `perseus`.`python_request`")
			rows = cur.fetchall()
			return list(rows), len(rows)
		else:
			q = {
				"name" : "",
				"terms" : [],
				"mode" : ""
			}
			cur.execute("SELECT * FROM `perseus`.`python_request` WHERE id_request = ' " + str(identifier) + "' ")
			d = list(cur.fetchall())
			if len(d) == 1:
				q["name"] = d[0][1]
				q["mode"] = d[0][2]

				cur.execute("SELECT * FROM `perseus`.`python_request_term` WHERE id_request = ' " + str(identifier) + "' ")
				d = list(cur.fetchall())
				for t in d:
					q["terms"].append(str(t[2]))

			return q




	def save(self, item):
		with self.con:
			cur = self.con.cursor()
			cur.execute("INSERT INTO `perseus`.`python_request` (`mode_request`,`name_request`) VALUES ('" + item["mode"] + "','" + item["name"] + "');")
			
			lastId = self.con.insert_id()

			if lastId:
				for term in item["terms"]:
					cur.execute("INSERT INTO `perseus`.`python_request_term` (`id_request`,`id_entity`) VALUES ('" + str(lastId) + "','" + str(term) + "')")
