#!/usr/bin/python
# -*- coding: utf-8 -*-

#Python CORE
import sys
import re

#Shared class through Clotho
from classes.SQL import SQL

class Query(object):
	
	def __init__(self):
		self.q = {
			"name" : "",
			"terms" : [],
			"mode" : ""
		}
		self.dateRegexp = re.compile("(-?[0-9]+|\?)\;(-?[0-9]+|\?)")
		self.sql =SQL()
		self.exportLemma = ["semantic-matrix", "tfidf-distance", "semantic-gephi"]


	def deco(self):
		print "\n*******************************************************\n"

	def yn(self, question):
		""" Return a raw input and check it

		Keywords Arguments
		question --- Question to be printed
		"""
		answer = raw_input(question + "\n y/n ->\t").lower()
		if answer in ["y", "n"]:
			return answer
		else:
			return self.yn("Input not recognized")

	def options(self, question, options = False, intOnly = False):
		answer = raw_input(question)
		if intOnly:
			if answer.isdigit():
				if options:
					if int(answer) in options:
						return int(answer)
					else:
						return self.options(question, options, intOnly)
				return int(answer)
			else:
				return self.options(question, options, intOnly)
		else:
			if answer.isdigit() and options:
				if int(answer) in options:
					return int(answer)
				else:
					return self.options(question, options, intOnly)
			elif options:
				if answer in options:
					return answer
				else:
					return self.options(question, options, intOnly)
			else:
				return answer

		return True

	def welcome(self):
		self.deco()
		print "\t\tWelcome to Clotho"
		print "\t\tDeveloped by Thibault Clerice (KCL-ENC)"
		self.deco()

	def threshold(self, error = False):
		if error == True:
			print "Unrecognized input"
		else:
			print "Choose your threshold"
		self.q["threshold"] = self.yn("Format your threshold like beginning-end  : \n y/n - ")
		#Checking

	def config(self):
		self.deco()
		self.q["name"] = raw_input("Name your query : \n - ")
		print "You choosed " + self.q["name"]

		print "Choose your modes :"
		self.q["mode"] = raw_input("Available : Entities | Lemma | Entities,Lemma : \n - ")
		print "You choosed " + self.q["mode"]

		self.q["threshold"] = self.yn("Do you want to apply a date threshold ?")

		print "You choosed " + self.q["threshold"]

	def lemmas(self):

		if len(self.q["terms"]) == 0:
			self.deco()
			print "Define lemma for your query"

		q = raw_input("Type your part of your lemma here (% is a wildcard) : \n - ")

		data, l = self.sql.lemma(q)
		if l == 0:
			print "No result for your query"
			return self.addLemma()
		else:
			print "Results : "
			for l in data:
				print "["+str(l)+"] " + data[l][2] + " (Definition : "+str(data[l][3])+")"

			id = raw_input("Type the numeric identifier (ex: [1]) for relevant lemma. \n eg. : 1,2 \n e.g. 1 \n - ")

			id = id.split(",")
			for i in id:
				self.q["terms"].append(str(data[int(i)][1]))
		
		return self.addLemma()

	def addLemma(self):
		q = self.yn("Do you want to add another lemma ?")
		if q == "y":
			return self.lemmas()
		elif q == "n":
			return True


	def load(self):
		self.deco()
		print "Available queries"
		available, l = self.sql.load()
		correctAnswers = []
		if l == 0:
			print "No saved request"
			return False
		else:
			for item in available:
				correctAnswers.append(item[0])
				print "[" + str(item[0]) + "]\t " + item[2] + " (Mode : " + item[1] + ")"
		
		q = raw_input( "Which one do you want to load ? (Type the number) \n - ")
		if int(q) in correctAnswers:
			self.q = self.sql.load(q)
			return self.q
		else:
			print "Incorrect answer"
			return self.load()

	def inputError(self, s):
		print "Error ----> We didn't understand your input ( "+str(s)+" ) "

	def save(self, deco = True):
		if deco:
			self.deco()
		s = self.yn("Do you want to save your request ?")
		if s == "y":
			if(self.sql.save(self.q)):
				print "Request saved"
			else:
				print "Error during save"
		else:
			print "Request won't be saved"

	def saveResults(self, deco = True):
		if deco:
			self.deco()
		s = self.yn("Do you want to save your results ?")
		if s == "y":
			return True
		else:
			return False

	def exportResults(self):
		self.deco()

		s = self.yn("Do you want to export your query ?")
		if s == "y":
			return True
		else:
			return False

	def process(self, deco = True):
		if deco:
			self.deco()

		s = self.yn("Do you want to process this query ?")
		if s == "y":
			return True
		else:
			return False

	def alreadySaved(self, deco = True):
		if deco:
			self.deco()

		s = self.yn("Is this query the last one you launched and saved ?")
		if s == "y":
			return True
		else:
			return False

	def exportLinkType(self, deco = True):
		if deco:
			self.deco()

		s = self.yn("Do you want to replace lemma/form/Sentence links to lemma/lemma links ?")
		if s == "y":
			return "lemma"
		else:
			return "sentence"


	def exportMean(self, deco = True):
		availableMeans = ["gephi", "d3js-matrix", "mysql", "semantic-matrix", "tfidf-distance", "semantic-gephi", "corpus"]
		if deco:
			self.deco()

		means = []
		i = 0
		for mean in availableMeans:
			means.append( mean + " (" + str( i ) + ") " )
			i += 1

		s = raw_input("Which mean of export do you want to use ? " + " / ".join(means) + " \n - ").lower()
		if s in availableMeans:
			return s
		elif  s.isdigit() and int(s) < len(availableMeans):
			return availableMeans[int(s)]
		else:
			self.inputError(s)
			return self.modeGephi(deco = False)

	def cleanProbability(self, deco = True):
		if deco:
			self.deco()

		s = self.yn("Clean based on probability ?")
		if s == "y":
			return "lemma"
		else:
			return "sentence"


	def thresholdOne(self, deco = True):
		if deco:
			self.deco()

		s = self.yn("Do you want to clean item with a frequency of 1 ?")
		if s == "y":
			return True
		else:
			return False

	def clustering(self, deco = True):
		if deco:
			self.deco()

		s = self.yn("Do you want to cluster items ?")
		if s == "y":
			return True
		else:
			return False

	def databaseMode(self, modes, deco = True):
		if len(modes) == 1:
			return modes[0]

		if deco:
			self.deco()

		means = []
		i = 0
		for mean in modes:
			means.append( mean + " (" + str( i ) + ") " )
			i += 1

		s = raw_input("Which occurrences finding mode do you want to use ? " + " / ".join(means) + " \n - ").lower()
		
		if s in modes:
			return s
		elif s.isdigit() and int(s) < len(modes):
			return modes[int(s)]
		else:
			self.inputError(s)
			return self.databaseMode(modes, deco = False)