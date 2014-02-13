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

	def lemma(self, query):
		data = {}
		cur = self.con.cursor()
		cur.execute("SELECT id, display_name, max_occ FROM hib_entities WHERE entity_type = 'Lemma' AND display_name LIKE '" + query + "'")

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