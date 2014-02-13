#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
try:
	import classes.SQL as SQL
except:
	print "Error importing MYSQL tool"
	sys.exit()

class Query(object):
	
	def __init__(self):
		self.q = {
			"name" : "",
			"terms" : [],
			"mode" : ""
		}
		self.sql = SQL.SQL()


	def deco(self):
		print "\n*******************************************************\n"

	def config(self):
		self.deco()
		self.q["name"] = raw_input("Name your query : \n - ")
		print "You choosed " + self.q["name"]

		print "Choose your modes :"
		self.q["mode"] = raw_input("Available : Entities | Lemma | Entities,Lemma : \n - ")
		print "You choosed " + self.q["mode"]

	def lemmas(self):

		if len(self.q["terms"]) == 0:
			self.deco()
			print "Define lemma for your query"

		q = raw_input("Type your part of your lemma here (% is a wildcard) : \n - ")

		data, l = self.sql.lemma(q)
		if l == 0:
			print "No result for your query"
		else:
			print "Results : "
			for l in data:
				print "["+str(l)+"] " + data[l][1] + " (Maximum Occurences : "+str(data[l][2])+")"

			id = raw_input("Type the numeric identifier (ex: [1]) for relevant lemma. \n eg. : 1,2 \n e.g. 1 \n - ")

			id = id.split(",")
			for i in id:
				self.q["terms"].append(str(data[int(i)][0]))
		
		q = raw_input("Do you want to add another lemma ? y/n \n - ")
		if q.lower() == "y":
			self.lemmas()
		else:
			return True
