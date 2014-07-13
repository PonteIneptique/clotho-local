#!/usr/bin/python
# -*- coding: utf-8 -*-

#Python CORE
import sys
import codecs
import json
import warnings
import re
import os
import tarfile
import wget
import importlib

#Python Libraries
import MySQLdb as mdb

#Python Warning
warnings.filterwarnings("ignore", category = mdb.Warning)

class Setup(object):
	def __init__(self):
		self.connected = False
		self.perseusConnected = False
		#Structure of the config
		self.conf = {
			"MySQL" : {
				"identifiers" : {},
				"database" : {
					"perseus" : "Name of the database for perseus dump",
					"cache" : "Name of the database for cache",
					"web" : "Name of the database for Clotho Web",
					"results" : "Name of the database for the results to be stored"
				}
			}
		}

		#Imports which needs apt-get install
		self.apt = {
			"numpy" : "build-essential python-dev python-numpy python-scipy python-matplotlib libatlas-dev libatlas3-base python-setuptools",
			"scipy" : "build-essential python-dev python-numpy python-scipy python-matplotlib libatlas-dev libatlas3-base python-setuptools",
			"MySQLdb" : "python-mysqldb",
			"pylab" : "python-matplotlib"
		}

		#Imports which needs pip
		self.pip = {
			"sklearn" : "scikit-learn", 
			"bs4" : "beautifulsoup4", 
			"nltk" : "nltk",
			"requests" : "requests",
			"wget" : "wget",
			"rdflib" : "rdflib",
			"wikipedia" : "wikipedia",
			"SPARQLWrapper" : "SPARQLWrapper"
		}

		#Imports  which needs dl and tar gz
		self.dl = {
			"progressbar" : "https://python-progressbar.googlecode.com/files/progressbar-2.3.tar.gz"
		}

		#Needed tables from Perseus :
		self.perseusTables = {
			"Chunks" : "http://www.perseus.tufts.edu/hopper/opensource/downloads/data/hib_chunks.tar.gz",
			"Entities" : "http://www.perseus.tufts.edu/hopper/opensource/downloads/data/hib_entities.tar.gz",
			"Entity Occurencies" : "http://www.perseus.tufts.edu/hopper/opensource/downloads/data/hib_entity_occurrences.tar.gz",
			"Frequencies" : "http://www.perseus.tufts.edu/hopper/opensource/downloads/data/hib_frequencies.tar.gz",
			"Lemmas" : "http://www.perseus.tufts.edu/hopper/opensource/downloads/data/hib_lemmas.tar.gz",
			"Metadata" : "http://www.perseus.tufts.edu/hopper/opensource/downloads/data/metadata.tar.gz"
		}

		#Needed file for morph
		self.morphfile = "https://github.com/jfinkels/hopper/raw/master/xml/data/latin.morph.xml" 

		#Text files
		self.texts = "http://www.perseus.tufts.edu/hopper/opensource/downloads/data/sgml.xml.texts.tar.gz"

	def dependencyType(self, dic):
		cmd = []
		dep = []
		for mod in dic:
			try:
				importlib.import_module(mod)
			except:
				cmd.append(dic[mod])
				dep.append(mod)
		return cmd, dep

	def sgml(self):
		"Print Checking texts"
		filename = self.download("texts", self.texts)
		with tarfile.open(filename) as tar:
			tar.extractall() # extract 
		print "Texts Done"

	def dependency(self):
		exit = False
		apt, dep = self.dependencyType(self.apt)
		if len(apt) > 0:
			print "Some dependencies (" + ", ".join(dep) + ") are not available"
			print "Type in your terminal sudo apt-get install " + " ".join(apt)

		apt, dep = self.dependencyType(self.pip)
		if len(apt) > 0:
			print "Some dependencies (" + ", ".join(dep) + ") are not available"
			print " sudo pip install " + " ".join(apt)

		apt, dep = self.dependencyType(self.dl)
		if len(apt) > 0:
			for app in dep:
				filename = self.download(app, self.dl[app])
				with tarfile.open(filename) as tar:
					if app == "progressbar":
						for member in tar.getmembers():
							if member.isreg():  # skip if the TarInfo is not files
								member.name = os.path.basename(member.name) # remove the path by reset it
								if os.path.splitext(member.name)[1] == ".py":
									tar.extract(member,"./progressbar/") # extract 

		if exit == True:
			print "You need to install and type the given commands before finishing the setup. Come back by typing \n python setup.py"
			sys.exit()

		print "All dependencies are installed like a rolling stone."

	def download(self, mode, url, optionalHeaders = False):
		""" Download an item according to the type given
		"""
		if mode == "mysql":
			path = "./cache/mysql/"
			filename = self.tableName(url) + ".tar.gz"
		elif mode == "morph":
			path = "./morph/"
			filename = "latin.morph.xml"
		elif mode == "progressbar":
			path = "./"
			filename = "progressbar-2.3.tar.gz"
		elif mode == "texts":
			path = "./"
			filename = "sgml.xml.texts.tar.gz"

		if os.path.isfile(path + filename) == False:
			filename = wget.download(url)
			os.rename("./" + filename, path + filename)
		print " Download complete"
		return path + filename



	def connection(self, mode = False):
		"""	Connect to the database using conf
		"""
		if mode == "perseus":
			self.perseus = mdb.connect("localhost", self.conf["MySQL"]["identifiers"]["user"], self.conf["MySQL"]["identifiers"]["password"], self.conf["MySQL"]["database"]["perseus"], charset='utf8')
			self.perseusConnected = True
			return True

		try:
			self.con = mdb.connect('localhost', self.conf["MySQL"]["identifiers"]["user"], self.conf["MySQL"]["identifiers"]["password"], charset='utf8')
			self.connected = True
			return True
		except:
			print "Unable to connect the database. Check the status of the server "
			return False

		return False

	def write(self):
		"""	Overwrite the setup file for the application
		"""
		filename = "./cache/setup.json"
		with codecs.open(filename, "w") as f:
			d = f.write(json.dumps(self.conf))
			f.close()

	def sqlId(self, o = False):
		""" Setup the identifiers
		"""
		data = {}
		if o != False:
			print "The identifiers you gave doesn't seem to work"

		print "We will now setup your connection to MySQL. We need identifiers for an account with Create DB permission"
		data["user"] = raw_input("Enter your username : ").replace(" ", "")
		data["password"] = raw_input("Enter your password : ").replace(" ", "")

		try:
			mdb.connect('localhost', data["user"], data["password"], charset='utf8')
			return data
		except:
			return self.sqlId(data)

	def db(self, db, legend):
		""" Setup the name of databases
		"""
		print "Name of the database `" + db + "` ( " + legend + " ) "
		name = raw_input("For default `clotho_" + db + "`, press enter, otherwise : ").replace(" ", "").replace("\n", "")

		#Using default if needed
		if len(name) == 0:
			name = "clotho2_" + db

		if self.connected == False:
			self.connection()

		with self.con:
			cur = self.con.cursor()
			if cur.execute("CREATE DATABASE IF NOT EXISTS `" + name + "` ") == 1:
				return name


	def dbs(self):
		for db in self.conf["MySQL"]["database"]:
			self.conf["MySQL"]["database"][db] = self.db(db, self.conf["MySQL"]["database"][db])

	def tableName(self, path):
		regexp = re.compile("\/(\w*)\.tar.gz")
		match = regexp.search(path)
		return match.group(1)

	def tableExists(self, con, table):
		with con:
			cursor = con.cursor()
			cursor.execute("SHOW TABLES LIKE %s", table)
			result = cursor.fetchone()
			if result:
				# there is a table named "tableName"
				return True
			else:
				return False
		return False

	def sqlShell(self, db):
		from subprocess import Popen, PIPE
		return Popen('mysql %s -u%s -p%s' % (self.conf["MySQL"]["database"][db], self.conf["MySQL"]["identifiers"]["user"], self.conf["MySQL"]["identifiers"]["password"]), stdout=PIPE, stdin=PIPE, shell=True)

	def tableCreate(self, filename, db = "perseus"):
		with tarfile.open(filename) as tar:
			for element in tar: #There is normaly only one
				tar.extract(element.name, os.path.dirname(filename))
				filename = os.path.dirname(filename) + "/" + element.name

		if db == "perseus":
			"""	Because file are pretty large, we lose connection with MySQLdb so we need subprocess
			"""
			process = self.sqlShell("perseus")
			output = process.communicate('source ' + filename)[0]
			"""
			self.connection("perseus")
			self.perseus.autocommit(True)
			cursor = self.perseus.cursor()
			cursor.execute(content)
			"""

	def tables(self):
		"""	Download tables if necessary
		"""
		#First we need to check if perseus is connected
		if self.perseusConnected == False:
			self.connection("perseus")

		for table in self.perseusTables:
			name = self.tableName(self.perseusTables[table])
			print "Checking table " + name
			if self.tableExists(self.perseus, name) == False:
				print "\t-> Downloading file for " + table
				f = self.download("mysql", self.perseusTables[table])
				print "\t-> Creating table"
				self.tableCreate(f)
				print "\t-> Done"

	def morph(self):
		print "Checking Latin Morph (From Perseus)"
		self.download("morph", self.morphfile)

