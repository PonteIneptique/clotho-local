#!/usr/bin/python
# -*- coding: utf-8 -*-

#Python CORE
import os
import sys
import codecs
import hashlib
import json
import re
import operator
from math import log
from pprint import pprint
import warnings
import tarfile
import wget
import importlib

#Warning
warnings.filterwarnings("ignore", category = RuntimeWarning)

#Python Libraries
from bs4 import BeautifulSoup
import MySQLdb
import numpy
import scipy
import sklearn
import nltk
import pylab
import rdflib
import wikipedia
from SPARQLWrapper import SPARQLWrapper, JSON
import requests

#Shared class through Clotho
#from dependencies.treetagger import TreeTagger
import progressbar

#Warnings
warnings.filterwarnings("ignore", category = MySQLdb.Warning)

clothoFolder = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)))) + "/"
"""
	Order of classes :
	#Initiate Classes
		- SQL
		- Initiate
		- Setup
		- Cache
	#Text Classes
		- Morph
		- Text
	#Export Classes
		- Results
		- Corpus (Corpus Generator for R)
		- Export (General Export connector class)
		- D3JS (D3JS Co-occurrence export class)
		- Clotho (Clotho-Web export class)

		#Algorithm
		- LSA (Latent semantic Analysis class)
		- SMa (Semantic Matrix Class) -> Exempla Clustering
		- TFIDF (Matrix Class) -> Context clustering

	Order of models :
		- Terms

	Query Class
		- Query

	PyLucene
"""

class SQL(object):
	def __init__(self, results = False, cache = False, web = False):
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
			v = cur.fetchone()

		try:
			t = True
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
				v = cur.fetchone()

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

class Initiate(object):
	def __init__(self):
		self.z = True

	def check(self):

		if os.path.exists(clothoFolder + "cache/sentence") == False:
			os.mkdir(clothoFolder + "cache/sentence")

		if os.path.exists(clothoFolder + "cache/search") == False:
			os.mkdir(clothoFolder + "cache/search")

		if os.path.exists(clothoFolder + "cache/form") == False:
			os.mkdir(clothoFolder + "cache/form")

		if os.path.exists(clothoFolder + "cache/download") == False:
			os.mkdir(clothoFolder + "cache/download")

		if os.path.exists(clothoFolder + "cache/dbpedia") == False:
			os.mkdir(clothoFolder + "cache/dbpedia")

		if os.path.exists(clothoFolder + "cache/rdf") == False:
			os.mkdir(clothoFolder + "cache/rdf")

		if os.path.exists(clothoFolder + "cache/mysql") == False:
			os.mkdir(clothoFolder + "cache/mysql")

		if os.path.exists(clothoFolder + "cache/description") == False:
			os.mkdir(clothoFolder + "cache/description")

		if os.path.exists(clothoFolder + "data/gephi") == False:
			os.mkdir(clothoFolder + "data/gephi")

		if os.path.exists(clothoFolder + "data/D3JS") == False:
			os.mkdir(clothoFolder + "data/D3JS")

		if os.path.exists(clothoFolder + "data/MySQL") == False:
			os.mkdir(clothoFolder + "data/MySQL")

		if os.path.exists(clothoFolder + "data/corpus") == False:
			os.mkdir(clothoFolder + "data/corpus")

		M = Morph()
		if M.check() == False:
			M.install()

		return True

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
									tar.extract(member,clothoFolder + "progressbar/") # extract 

		if exit == True:
			print "You need to install and type the given commands before finishing the setup. Come back by typing \n python setup.py"
			sys.exit()

		print "All dependencies are installed like a rolling stone."

	def download(self, mode, url, optionalHeaders = False):
		""" Download an item according to the type given
		"""
		if mode == "mysql":
			path = clothoFolder + "cache/mysql/"
			filename = self.tableName(url) + ".tar.gz"
		elif mode == "morph":
			path = clothoFolder + "morph/"
			filename = "latin.morph.xml"
		elif mode == "progressbar":
			path = clothoFolder 
			filename = "progressbar-2.3.tar.gz"
		elif mode == "texts":
			path = clothoFolder 
			filename = "sgml.xml.texts.tar.gz"

		if os.path.isfile(path + filename) == False:
			filename = wget.download(url)
			os.rename(clothoFolder + filename, path + filename)
		print " Download complete"
		return path + filename



	def connection(self, mode = False):
		"""	Connect to the database using conf
		"""
		if mode == "perseus":
			self.perseus = MySQLdb.connect("localhost", self.conf["MySQL"]["identifiers"]["user"], self.conf["MySQL"]["identifiers"]["password"], self.conf["MySQL"]["database"]["perseus"], charset='utf8')
			self.perseusConnected = True
			return True

		try:
			self.con = MySQLdb.connect('localhost', self.conf["MySQL"]["identifiers"]["user"], self.conf["MySQL"]["identifiers"]["password"], charset='utf8')
			self.connected = True
			return True
		except:
			print "Unable to connect the database. Check the status of the server "
			return False

		return False

	def write(self):
		"""	Overwrite the setup file for the application
		"""
		filename = clothoFolder + "cache/setup.json"
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
			MySQLdb.connect('localhost', data["user"], data["password"], charset='utf8')
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

class Cache(object):
	def __init__(self):
		self.folder = {
			"sentence" : clothoFolder + "cache/sentence/",
			"search" : clothoFolder + "cache/search/",
			"form" : clothoFolder + "cache/form/",
			"dbpedia" : clothoFolder + "cache/dbpedia/",
			"rdf" : clothoFolder + "cache/rdf/",
			"definition" : clothoFolder + "cache/definition/",
			"triples" : clothoFolder + "cache/triples/",
			"nodes" : clothoFolder + "cache/nodes/"
		}
	def tUoB(self, obj, encoding='utf-8'):
		if isinstance(obj, basestring):
			if not isinstance(obj, unicode):
				obj = unicode(obj, encoding)
		return obj

	def hash(self, sentence, mode = "sentence"):
		""" Find the hash for a given query or mode	

		Keyword arguments:
		sentence --- A string by default in mode sentence or a dictionary in mode search
		mode --- Type of hash to retrieve (default = sentence)
		"""
		if mode in ["search", "nodes", "triples"]:
			sentence = " ".join([term for term in sentence["terms"]]) + " " + sentence["name"] + " " + sentence["mode"]

		sentence = hashlib.md5(sentence.encode("utf-8")).hexdigest()
		return sentence

	def filename(self, sentence, mode = "sentence"):
		""" Return the file name given a sentence or a query

		Keyword arguments:
		sentence --- A string by default in mode sentence or a dictionary in mode search
		mode --- Type of hash to retrieve (default = sentence)
		"""
		if mode == "rdf":
			return self.hash(sentence, mode = mode) + ".rdf"
		else:
			return self.hash(sentence, mode = mode) + ".json"


	def cache(self, query, mode, data = False, check = False):
		""" Read, write or check if there is a cache for given identifiers

		query -- filename
		mode -- An element from self.folder
		data -- Either a json convertable object,  an instance of file to be written or an instance of requests lib results
		check -- If set to true, only perform a check if cache is available or not.
		"""
		filename = self.filename(query, mode)
		filename = self.folder[mode] + filename

		if data == False:
			if os.path.isfile(filename):
				if check == True:
					if mode == "rdf":
						return filename
					return True
				else:
					with codecs.open(filename, "r", "utf-8") as f:
						d = json.load(f)
						f.close()
						return d
			return False
		else:
			with codecs.open(filename, "w", "utf-8") as f:
				if hasattr(data , "read"):
					d = f.write(data.read())
				elif hasattr(data , "text"):
					d = f.write(data.text)
				else:
					d = f.write(json.dumps(data))
				f.close()
			return True	

	def triples(self, url, data = False, check = False):
		return self.cache(url, "triples", data, check)

	def nodes(self, query, data = False, check = False):
		return self.cache(query, "nodes", data, check)

	def rdf(self, url, data = False, check = False):
		return self.cache(url, "rdf", data, check)

	def dbpedia(self, url, data = False, check = False):
		return self.cache(url, "dbpedia", data, check)

	def form(self, word, data = False, check = False):
		return self.cache(word, "form", data, check)

	def definition(self, url, data = False, check = False):
		return self.cache(url, "definition", data, check)

	def sentence(self, sentence, data = False, check = False):
		"""	Return a boolean given the functionnality asked: can either check if cache is available, retrieve or write cache

		Keyword arguments:
		sentence --- A string 
		data --- If false, will retrieve or check if cache exists, if set, will write cache
		check --- if data is false and check is true (default), will only check if a cached version of the sentence is available
		"""
		return self.cache(sentence, "sentence", data, check)

	def search(self, query, data = False, check = False):
		"""	Return a boolean given the functionnality asked: can either check if cache is available, retrieve or write cache

		Keyword arguments:
		query --- A query dictionary
		data --- If false, will retrieve or check if cache exists, if set, will write cache
		check --- if data is false and check is true (default), will only check if a cached version of the sentence is available
		"""
		return self.cache(query, "search", data, check)

class Morph(object):
	def __init__(self):
		self.s = SQL()
		self.widget = ['Words processed: ', progressbar.Counter(), ' ( ', progressbar.Timer() , ' )']
		self.pbar = False
		self.processed = 0
		#
		self.web = True	#If set to true, use perseids database instead, crawling json
		self.cache = Cache()

		#Roman numeral regExp
		romanNumeral = "^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"
		self.num = re.compile(romanNumeral)

		self.r = requests

	def perseid(self, lemma):
		"""	Returns a lemma according to perseid morphology service
		***HIGHLY EXPERIMENTAL, use with care***


		"""
		url = "http://services.perseids.org/bsp/morphologyservice/analysis/word?word=" + lemma +"&lang=lat&engine=morpheuslat"
		headers = {
			'content-type': 'application/json',
			'accept' : 'application/json, text/javascript'
		}
		j = []
		r = self.r.get(url, headers=headers)
		r.raise_for_status()
		try:
			j = json.loads(r.text)
		except:
			print "Perseid returned unreadable json"
			print r.text
			sys.exit()

		if u'Body' in j[u'RDF'][u'Annotation']:
			responseBody = j[u'RDF'][u'Annotation'][u'Body']
			if isinstance(responseBody, list):
				ret = []
				for item in responseBody:
					try:
						ret.append(item[ u'rest'][u'entry'][u'dict'][u'hdwd'][u'$'].translate({ord(c): None for c in string.digits}))
					except:
						print item
						continue
				return ret
			else:
				try:
					return [j[u'RDF'][u'Annotation'][u'Body'][ u'rest'][u'entry'][u'dict'][u'hdwd'][u'$'].translate({ord(c): None for c in string.digits})]
				except:
					return []
		else:
			return []
		#http://services.perseids.org/bsp/morphologyservice/analysis/word?word=vos&lang=lat&engine=morpheuslat

	def check(self):
		with self.s.con:
			cur = self.s.con.cursor()
			query = cur.execute("SELECT COUNT(*) CNT FROM morph LIMIT 10")
			data = cur.fetchone()
			cur.close()

			if int(data[0]) > 0:
				return True
			else:
				return False
		return False

	def install(self):
		data = {"lemma" : "", "form" : ""}
		i = 0
		for event, elem in xml.etree.cElementTree.iterparse(clothoFolder + "morph/latin.morph.xml"):
			if elem.tag == "analysis":
				for child in elem:
					if child.tag == "lemma":
						data["lemma"] = child.text
					elif child.tag == "form":
						data["form"] = child.text
					print child.tag + " = " + child.text
				try:
					self.s.saveMorph(data)
				except:
					continue
		print str(i) + " morph imported in database"

	def all(self,lemma):
		with self.s.con:
			cur = self.s.con.cursor()
			req = cur.execute("SELECT form_morph FROM morph WHERE lemma_morph = '" + lemma + "'")

			rows = cur.fetchall()
			data = []
			for row in rows:
				data.append(row[0])
			return data


	def cleanLemma(self, r):
		if r == None:
			return None
		if r[0]:
			l = r[0].split(u"#")[0]
		else:
			l = None
		if r[1] == None:
			return [l, None]
		else:
			return [l, r[1]]

	def cleanDuplicate(self, data):
		exist = []
		ret = []
		for d in data:
			if d[0] not in exist:
				exist.append(d[0])
				ret.append(d)
		return ret

	def morph(self, form):
		"""Given the form of a word, returns a list of lemma and their type

		Keyword arguments:
		form -- a lemma's form (string)
		"""
		if self.pbar == False:
			self.pbar = progressbar.ProgressBar(widgets=self.widget, maxval=100000).start()

		if(self.num.search(form)):
			return False
		elif len(form) == 1:
			return False
		else:
			if self.web == True:
				#Check if cache exist
				data = self.cache.form(form)
				if data != False:
					return [[d, None] for d in data]

				#if not, check perseid
				data = self.perseid(form)

				#If we got data, cache it and return it
				if len(data) > 0:
					self.cache.form(form, data = data)
					return [[d, None] for d in data]
				else:
					self.cache.form(form, data = [])
			with self.s.con:
				cur = self.s.con.cursor()

				req = cur.execute("SELECT morph.lemma_morph, hib_entities.entity_type FROM morph LEFT JOIN hib_entities ON (hib_entities.display_name = morph.lemma_morph AND hib_entities.entity_type != \"Lemma\") WHERE form_morph= %s ", [form])
				rows = cur.fetchall()
				data = []

				for row in rows:
					r = list(row)
					data.append(self.cleanLemma(r))

				if isinstance(data, list):
					self.cleanDuplicate(data)

				#Update Progress bar
				self.processed += 1
				self.pbar.update(self.processed)

				#Returning data
				return data
	
	def filter(self, sentence, mode = "lemma", safemode="", terms = [], stopwords = []):
		returned = []

		#First filter stop words
		for word in sentence:
			keep = []
			for lemma in word[1]:
				sp = lemma[0].split("#")
				sp = sp[0].replace("-", "").lower()
				if sp not in stopwords:
					keep.append(lemma)
			if len(keep) > 0:
				returned.append([word[0], keep])

		if mode == "lemma":
			return returned

		else:
			sentence = returned
			returned = []
			for word in sentence:
				keep = []
				for lemma in word[1]:
					#if lemma[1] != None:
					#print lemma[0] + " | " + lemma[0][0]
					if lemma[0][0].isupper() == True:
						keep.append(lemma)
					elif lemma[0] in terms:
						keep.append(lemma)

				if len(keep) > 0:
					returned.append([word[0], keep])

			return returned

class Text(object):
	def __init__(self):

		#Instances
		self.sql = SQL()
		self.m = Morph()
		self.r = Results(cache=True)

		self.cache = True


		#Data
		self.learning = {}
		self.dots = "".join([',', '.', '...', '"', "'", ':', ';', '!', '?','-', "(", ")", "[", "]"])
		self.processed = []

		#Processed data
		f = open(clothoFolder + "morph/stopwords.txt")
		self.stopwords = f.read().encode("UTF-8").split(",")
		f.close()

		#Reg Exp
		self.regexp = re.compile("Perseus:text:([0-9]{4}\.[0-9]{2}\.[0-9]{4})")


	def BCEtoInt(self, date):
		""" Convert a string identifying a date using the BCE suffix by an int formatted date 

		Keyword arguments:
		date -- a list of string
		"""
		toReturn = []
		for d in date:
			if "BCE" in d:
				d = -1 * int(d.replace("BCE", ""))
			else:
				d = int(d)
			toReturn.append(d)
		return toReturn

	def inDateRange(self, metadata, dateRange):
		""" Return a bolean given the metadata of a text and a given date range

		Keyword arguments:
		metadata -- a set of metadata (dictionary)
		dateRange -- a given date range (tuple of int)
		"""
		dateRecognition = re.compile("([0-9]+(?:BCE)?)(?:\-([0-9]+(?:BCE)?))?")
		if "dc:Date:Created" in metadata:
			date = dateRecognition.search(metadata["dc:Date:Created"]).groups()
			date = BCEtoInt(date)
			if len(date) == 2: #We have here a range for the date of creation so we check if one of the two dates are in our own range
				if (date[0] >= dateRange[0] and date[0] <= dateRange[1]) or (date[1] >= dateRange[0] and date[1] <= dateRange[1]):
					return True
			elif len(date) == 1: #If we have only one date
				if (date[0] >= dateRange[0] and date[0] <= dateRange[1]):
					return True
		return False	#any other situation, including  not aving the metadata should return False

	def metadata(self, identifier):
		""" Returns the metadata for a given text using the MySQL database instead of the XML metadata

		Keyword arguments:
		identifier -- A list of identifier given by Lucene or MYSQL
		"""
		data , l = self.sql.metadata(identifier[1])
		r = { "identifier" : identifier[1]}

		if l > 0:
			for d in data:
				r[d[0]] = d[1]

		return r

	def path(self, identifier):
		""" Define the path of a file given its identifier

		Keyword arguments:
		identifier -- A list of identifier given by Lucene or MYSQL
		"""
		p = clothoFolder + "texts/"
		identifier = self.regexp.search(identifier).group(1)
		#Typical data : Perseus:text:2008.01.0558
		identifier = identifier.split(".")
		p += ".".join(identifier[:2]) + "/" + ".".join(identifier) + ".xml"

		return p

	def find(self, text, forms):
		""" Return a list of sentence given some forms

		Keyword arguments:
		text -- The text in a string format
		forms -- A list of forms corresponding to the declined query lemma
		"""
		sentences = nltk.tokenize.sent_tokenize(text)
		correct = []
		for form in forms:

			i = 0
			while i < len(sentences):
				#Last condition ensure that sentences has not been processed
				if form in nltk.tokenize.word_tokenize(sentences[i]) and sentences[i] not in self.processed:
					self.processed.append(sentences[i])
					correct.append(sentences.pop(i))
				else:
					i += 1
		return correct

	def chunk(self, identifier, mode = "mysql"):
		""" Return the full text given its identifiers

		Keyword arguments:
		identifier -- A list of identifier given by Lucene or MYSQL
		mode -- A string indicating the mode used, as both identifier have different depth and structure
		"""

		if(mode == "mysql"):
			f = codecs.open(self.path(identifier[1]), "r", "UTF-8")
			text = f.read()
			f.close()

			self.text = text;

			return self.section(identifier)
		elif(mode == "lucene"):
			f = codecs.open(self.path(identifier), "r", "UTF-8")
			text = f.read()
			f.close()

			self.text = text;

			return self.section(identifier, mode = mode)


	def section(self, identifier, mode = "mysql"):
		""" Return the BeautifulSoup section/node of a text where an occurence should be found

		Keyword arguments:
		identifier -- A list of identifier given by Lucene or MYSQL
		mode -- A string indicating the mode used, as both identifier have different depth and structure
		"""
		if mode == "mysql":
			model = BeautifulSoup(identifier[8]+identifier[9])
			tags = model.find_all(True)

			t = BeautifulSoup(self.text)
			div1 = t.find(tags[-1].name, tags[-1].attrs)
			div2 = div1.find(True,{"type" : identifier[3], "n" : identifier[4]})
			if div2:

				return div2.text.encode("UTF-8")
			elif div1:
				return div1.text.encode("UTF-8")

			else:
				return ""
		else:
			t = BeautifulSoup(self.text)
			return t.text

	def lemmatize(self, sentence = "", mode = "Lemma", terms = []):
		"""Given a sentence (string), tokenize it into words 
			and return a list with the following structure 
			[form, [list of corresponding [lemma, type of lemma]]]

		Keyword arguments:
		sentence -- A sentence to lemmatize (string)
		mode -- Either Lemma or Auctoritas, will return all corresponding lemma or only those who are proper nouns (default : "Lemma")
		terms -- A list of terms which are our query terms
		"""
		data = []

		cached = False
		#Caching
		#if self.cache == True:
		#	cached = self.r.sentence(sentence, boolean = True)

		if cached:
			print cached
			#Loading Id of this sentence
			S = self.r.sentence(sentence)
			#Loading data
			tempData = self.r.load(S)
			data = []
			#Caching some of this data
			safe = True
			
			for row in tempData:
				m = row[1]
				self.learning[row[0]] = m
				data.append([row[0], m])
				safe = False
		else:
			#Registering sentence
			S = self.r.sentence(sentence)
			#Cleaning sentence
			sentence = sentence.strip()
			for dot in self.dots:
				sentence = sentence.replace(dot, " ")

			sentence = nltk.tokenize.word_tokenize(sentence)
			safe = True
			for word in sentence:

				lower = word.lower()
				if lower not in self.stopwords:
					if word not in self.learning:
						m = self.m.morph(word)

						if m == False:
							d = False
						else:
							if self.cache == True:
								F = self.r.form(word)

								for Lem in m:
									L = self.r.lemma(Lem)

									#Make Link
									self.r.relationship(S, F, L)

							if "Auctoritas" in mode:
								m = self.m.filter(word, m, safe, terms)

							d = [word, m]
							self.learning[word] = m
					else:
						#print "Using cache for " + word
						F = self.r.form(word)

						for Lem in self.learning[word]:
							L = self.r.lemma(Lem)
							self.r.relationship(S, F, L)

						d = [word, self.learning[word]]

					if d != False:
						data.append(d)
				safe = False
		

		return data

class Results(object):
	def __init__(self, cache = False, web = False):
		self.s = SQL(cache = cache, web = web)
		self.con = self.s.con
		self.saved = {"lemma" : {}, "sentence" : {}, "form": {}}

	def db(self):
		with self.con:
			cur = self.con.cursor()
			cur.execute("SELECT DATABASE()")
			return cur.fetchall()

	def lemma(self, lemma):
		if lemma[0] in self.saved["lemma"]:
			return self.saved["lemma"][lemma[0]]
		else:
			with self.con:
				cur = self.con.cursor()
				cur.execute("SELECT id_lemma FROM lemma WHERE text_lemma = %s LIMIT 1", [lemma[0]])
				d = cur.fetchone()

				if d != None:
					if len(d) == 1:
						return d[0]
				else:
					cur.execute("INSERT INTO lemma (text_lemma, type_lemma) VALUES (%s, %s)", [lemma[0],lemma[1]])
					r = self.con.insert_id()
					self.saved["lemma"][lemma[0]] = r
					return r

	def form(self, form):
		if form in self.saved["form"]:
			return self.saved["form"][form]
		else:
			with self.con:
				cur = self.con.cursor()
				cur.execute("SELECT id_form  FROM form WHERE text_form = %s",[form])
				d = cur.fetchone()

				if d != None:
					if len(d) == 1:
						return d[0]
				else:
					cur.execute("INSERT INTO form (text_form) VALUES (%s)", [form])
					r = self.con.insert_id()
					self.saved["form"][form] = r
					return r

	def sentence(self, sentence, text = False, boolean = False):
		if sentence in self.saved["sentence"]:
			if boolean:
				return True
			else:
				return self.saved["sentence"][sentence]
		else:
			with self.con:
				cur = self.con.cursor()
				if text:
					cur.execute("SELECT id_sentence FROM sentence WHERE text_sentence = %s AND id_document = %s LIMIT 1", [sentence, text])
				else:
					cur.execute("SELECT id_sentence FROM sentence WHERE text_sentence = %s LIMIT 1", [sentence])

				d = cur.fetchone()

				if d != None:
					if len(d) == 1:
						if boolean:
							return True
						else:
							return d[0]
				else:
					if boolean:
						return False
					else:
						if text:
							cur.execute("INSERT INTO sentence (text_sentence, id_document) VALUES ( %s, %s )", [sentence, text])
						else:
							cur.execute("INSERT INTO sentence (text_sentence) VALUES ( %s )", [sentence])

						r = self.con.insert_id()

						self.saved["sentence"][sentence] = r
						return r

	def load(self, sentence):
		with self.con:
			d = {}
			cur = self.con.cursor()
			cur.execute("SELECT f.text_form, l.text_lemma, l.type_lemma FROM lemma_has_form lf, form f, lemma l WHERE l.id_lemma = lf.id_lemma AND f.id_form = lf.id_form AND lf.id_sentence = %s", [sentence])
			rows = cur.fetchall()

			for row in rows:
				if row[0] not in d:
					d[row[0]] = []
				d[row[0]].append([row[1], row[2]])

			return [[form, d[form]] for form in d]

	def clean(self):
		"""
			Clean the table or create them

		"""
		operations = [
			'CREATE TABLE IF NOT EXISTS form (    id_form int(11) NOT NULL AUTO_INCREMENT,    text_form varchar(255) DEFAULT NULL,    PRIMARY KEY (id_form))  ENGINE=InnoDB DEFAULT CHARSET=utf8;'
			'CREATE TABLE IF NOT EXISTS lemma (    id_lemma int(11) NOT NULL AUTO_INCREMENT,    text_lemma varchar(255) DEFAULT NULL,    type_lemma varchar(45) DEFAULT NULL,    PRIMARY KEY (id_lemma))  ENGINE=InnoDB DEFAULT CHARSET=utf8;',
			'CREATE TABLE IF NOT EXISTS lemma_has_form (    id_lemma int(11) NOT NULL,    id_form int(11) NOT NULL,    id_sentence int(11) DEFAULT NULL,    KEY lhf_lemma (id_lemma),    KEY lhf_form (id_form),    KEY lhf_sentence (id_sentence))  ENGINE=InnoDB DEFAULT CHARSET=utf8;',
			'CREATE TABLE IF NOT EXISTS sentence (    id_sentence int(11) NOT NULL AUTO_INCREMENT,    text_sentence text,    id_document varchar(255) DEFAULT NULL,    PRIMARY KEY (id_sentence))  ENGINE=InnoDB DEFAULT CHARSET=utf8;',
			'TRUNCATE TABLE form;',
			'TRUNCATE TABLE lemma;',
			'TRUNCATE TABLE sentence;',
			'TRUNCATE TABLE lemma_has_form;'
		]
		with self.con:
			for op in operations:
				try:
					cur = self.con.cursor()
					cur.execute(op)
					cur.close()
				except:
					log = op

	def relationship(self, sentence, form, lemma):
		with self.con:
			cur = self.con.cursor()
			cur.execute("INSERT INTO `lemma_has_form` (`id_lemma`,`id_form`,`id_sentence`)VALUES(%s, %s, %s)", [lemma,form,sentence])
			return True

	def save(self, rows):
		#
		#	rows = [
		#		[form, lemma, text, sentence]
		#	]
		#
		for row in rows:
			if row[1] != False:
				if isinstance(row[2], basestring) != True:
					id_document = row[2][1]
				else:
					id_document = row[2]

				if len(row[1]) == 0:
					s = self.sentence(row[3], text = id_document)
					l = 0
					f = self.form(row[0])

					self.relationship(s,f,l)
				else:
					for lemma in row[1]:

						s = self.sentence(row[3], text = id_document)
						l = self.lemma(lemma)
						f = self.form(row[0])

						self.relationship(s,f,l)

class Corpus(object):
	def __init__(self, data = {}, flexed = False):
		self.folder = clothoFolder + "data/corpus/"
		self.flexed = flexed
		self.data = data

	def w(self, data = False):
		for term in data:
			if isinstance(data[term][0], list):
				replacement = ""
				for sentence in data[term]:
					replacement += " ".join(sentence) + "\n"
				data[term] = replacement
			else:
				data[term] = " ".join(data[term])
			with codecs.open(clothoFolder + "data/corpus/" + term + ".txt", "w") as f:
				f.write(data[term])
				f.close()
		return True

	def rawCorpus(self, data = False):
		if not data:
			data = self.data
		outputDictionary = {}
		if self.flexed:
			for term in data:
				outputDictionary[term] = " ".join([word[0] for word in data[term]])
		else:
			for term in data:
				outputDictionary[term] = []
				for word in data[term]:
					for w in word[1]:
						outputDictionary[term].append(w[0])
		self.w(outputDictionary)

	def windowCorpus(self, window = 4, data = False):
		"""
			Return a raw corpus / term where only the n-words left AND right are kept from the sentence.

			Params
			window (Int) - N window
		"""
		if not data:
			data = self.data
		outputDictionary = {}

		#We merge everything in one sentence
		for term in data:
			outputDictionary[term] = []
			sentence = []
			sentence_text = ""
			for word in data[term]:
				lemma = []
				if sentence_text != word[3]:
					#Writing time
					if len(sentence) > 0:
						sentence = self.windowSentence(term, sentence, window)
						outputDictionary[term].append(sentence)
					#Creating the new sentence array
					sentence_text = word[3]
					sentence = []
					print sentence_text

				for w in word[1]:
					lemma.append(w[0])
				if len(lemma) > 0:
					sentence.append(lemma)

		if len(sentence) > 0:
			sentence = self.windowSentence(term, sentence, window)
			outputDictionary[term].append(sentence)

		self.w(outputDictionary)
		return True

	def LDA(self, data = False):
		"""
			Return a raw corpus / term where only the n-words left AND right are kept from the sentence.

			Params
			window (Int) - N window
		"""
		if not data:
			data = self.data
		outputDictionary = {}

		#We merge everything in one sentence
		for term in data:
			outputDictionary[term] = []
			sentence = []
			sentence_text = ""
			for word in data[term]:
				lemma = []
				if sentence_text != word[3]:
					#Writing time
					if len(sentence) > 0:
						sentence = self.LDASequence(sentence, word[2])
						outputDictionary[term].append(sentence)
					#Creating the new sentence array
					sentence_text = word[3]
					sentence = []

				for w in word[1]:
					lemma.append(w[0])
				if len(lemma) > 0:
					sentence.append(lemma)

		if len(sentence) > 0:
			sentence = self.LDASequence(sentence, word[2])
			print sentence
			outputDictionary[term].append(sentence)

		self.w(outputDictionary)
		return True

	def urlify(self, s):
		# Remove all non-word characters (everything except numbers and letters)
		s = re.sub(r"[^\w\s]", '', s)
		# Replace all runs of whitespace with a single dash
		s = re.sub(r"\s+", '-', s)

		return s

	def LDASequence(self, sentence, author):
		author = self.urlify(author)
		s = [[author + "\t"], [author + "\t"]]
		s = s + sentence
		q = []
		for l in s:
			for i in l:
				q.append(i)

		return q


	def windowSentence(self, term = "", sentence = [], window = 0):
		if len(sentence) <= 0:
			return sentence
		min_index = 0
		max_index = len(sentence) - 1
		length = window * 2 + 1

		for i in range(0,  max_index):
			lemma = sentence[i]
			if term in lemma:
				w = i - window
				if w > min_index:
					min_index = i - window

				w = min_index + length
				if w > max_index:
					max_index = max_index + 1
				else:
					max_index = length + min_index
				break

		sentence = sentence[min_index:max_index]
		s = []
		for lemma in sentence:
			for l in lemma:
				if not term in lemma:	#Remove the term from the sentence 
					s.append(l)
		return s

class Export(object):
	def __init__(self, q = False, QueryObject = False):
		self.q = q
		self.c = Cache()
		self.perseus = SQL()
		self.results = SQL(cache = True, web = False)
		self.cache = {"lemma" : {}, "sentence" : {}, "form": {}}
		self.mode = "lemma"

		availableMeans = ["gephi", "d3js-matrix", "mysql", "semantic-matrix", "tfidf-distance", "semantic-gephi", "corpus"]
		if not QueryObject:
			QueryObject = Query()
		self.query = QueryObject
		self.options = {
			"gephi" : {
				"probability" : 0, # = Ask Question // -1 Never 1// Always
				"nodification" : 1,
				"nodificationMode" : True, #Or Sentence or Lemma
				"function" : self.gephi
			},
			"clotho-web": {
				"probability": 0,
				"nodification": 1,
				"nodificationMode" : True,
				"function" : self.ClothoWeb
			},
			"d3js-matrix" : {
				"probability": 0,
				"nodification": 1,
				"nodificationMode" : True,
				"function" : self.D3JSMatrix
			},
			"corpus" : {
				"probability": 0,
				"nodification": 1,
				"nodificationMode" : False,
				"function" : self.corpus
			},
			"jsLDA" : {
				"probability": 0,
				"nodification": 1,
				"nodificationMode" : False,
				"function" : self.jsLDA
			}
		}
		###Load treetagger if possible
		try:
			self.tt = TreeTagger(encoding='latin-1',language='latin')
			self.ttAvailable = True
		except:
			self.ttAvailable = False

	def nodification(self):
		"""	Using SQL, retrieve the nodes and links so everything works with export
		"""

		if self.q and self.c.nodes(self.q, False, True):
			d = self.c.nodes(self.q)
			self.nodes = d["nodes"]
			self.edges = d["edges"]
			self.triples = d["triples"]
			return True

		nodes = [] # [id, label, type, document_id]
		edges = []
		triples = [] # lemma, form, sentence
		orphans = {"edges" : [], "nodes" : []}
		with self.results.con:
			cur = self.results.con.cursor()
			cur.execute("SELECT * FROM lemma_has_form")

			rows = cur.fetchall()
			for row in rows:
				#Lemma, Form, Sentence
				lem = "l"+str(row[0])
				frm = "f"+str(row[1])
				sen = "s"+str(row[2])
				triples.append([lem, frm, sen])
				#Lemma :
				if row[0] not in self.cache["lemma"]:
					cur.execute("SELECT text_lemma FROM lemma WHERE id_lemma = %s LIMIT 1", [row[0]])
					lemma = cur.fetchone()
					if lemma != None:
						self.cache["lemma"][row[0]] = lemma[0]
						nodes.append([lem, self.cache["lemma"][row[0]], "lemma", "Null"])
					else:
						self.cache["lemma"][row[0]] = None

				#Sentence :
				if row[2] not in self.cache["sentence"]:
					cur.execute("SELECT text_sentence, id_document FROM sentence WHERE id_sentence = %s LIMIT 1", [row[2]])
					sentence = cur.fetchone()
					self.cache["sentence"][row[2]] = sentence
					nodes.append([sen, self.cache["sentence"][row[2]], "sentence", sentence[1]])

				#Form :
				if row[1] not in self.cache["form"]:
					cur.execute("SELECT text_form FROM form WHERE id_form = %s LIMIT 1", [row[1]])
					form = cur.fetchone()[0]
					self.cache["form"][row[1]] = form
					nodes.append([frm, self.cache["form"][row[1]], "form", "Null"])

				#We add two edges : lemma -> sentence; lemma -> form
				#We presume that a vote has been made and only form = 1 lemma

				if self.cache["lemma"][row[0]] == None:
					orphans["edges"].append([frm, sen])
					orphans["nodes"].append([frm, self.cache["form"][row[1]]])
				else:
					edges.append([frm, sen, "form-sentence"])
					edges.append([lem, frm, "lemma-form"])

		self.nodes = nodes
		self.edges = edges
		self.triples = triples
		self.orphans = orphans

		if self.q:
			self.c.nodes(self.q, data = {"nodes" : nodes, "edges" : edges, "triples" : triples})


	def useTT(self):
		""" Use TreeTagger to improve the probability feature, creating a new dictionnary where the key is the sentence and the value is a list of found lemma
		"""

		#First we need to get last lemma id and get id for each lemma
		ret = {}
		sentences = [node for node in self.nodes if node[2] == "sentence"]
		for sentence in sentences:
			results = self.tt.tag(sentence[1][0].encode('latin-1', "ignore"))
			ret[sentence[0]] = []
			for lemma in [r[2].split("|") for r in results]:
				ret[sentence[0]] += lemma
			ret[sentence[0]] = list(set(ret[sentence[0]]))
		return ret

	def cleanLemma(self, lemma):
		"""	Deletes number "#" from lemma in list of lemma
		"""
		ret = []
		for lem in lemma:
			ret.append(lem.split("#")[0])
		return list(set(ret))

	def cleanProbability(self):
		"""	Clean the probability
			-> Use self. data
		"""
		edges = []
		compute = {}
		#We build an index
		for edge in self.edges:
			if edge[2] == "lemma-form":
				#Lemma
				if edge[0] not in compute:
					compute[edge[0]] = []
				#Form
				if edge[1] not in compute:
					compute[edge[1]] = []

				compute[edge[0]].append(edge[1])
				compute[edge[1]].append(edge[0])

		#We give to our edges the one which are not lemma-form AND the one which have only one possibility
		edges += [edge for edge in self.edges if edge[2] == "form-sentence"]#(edge[2] == "lemma-form" and len(compute[edge[1]]) <= 1) or 
		newcompute = {}
		#Then we need to find a way to compute stuff isn't it ?
		#Basically, we want the one with the biggest compute[lemma] in compute[form]
		for form in compute: 
			if form[0] == "f":
				compute[form] = self.cleanLemma(compute[form])
				if len(compute[form]) > 1:
					Max = float(0)
					MaxId = str(0)
					for lemma in compute[form]:
						computed = float(0)
						for forms in compute[lemma]:
							computed += float(1 / float(len(compute[forms])))

						if MaxId == 0 or computed > Max:
							MaxId = lemma
							Max = computed
					newcompute[form] = [MaxId]
				else:
					newcompute[form] = compute[form]

		edges2 = [[newcompute[edge][0], edge, "lemma-form"] for edge in newcompute if edge[0] == "f"]

		edges += edges2
		self.edges = edges
		return True

	def hash(self, l):
		l = ";".join(l)
		return hashlib.md5(l).hexdigest()

	def lemma(self, terms = []):
		""" Given a list of terms, transform a graph lemma -> form -> sentence into lemma <-> lemma

		Keyword arguments
		terms --- List of query terms (lemma people are looking form)
		"""


		"""
		if self.q and self.c.triples(self.q, False, True):
			d = self.c.nodes(self.q)
			self.nodes = d["nodes"]
			self.edges = d["edges"]
			return True
		"""
		nodes = [node[0:2] for node in self.nodes if node[2] == "lemma"]
		hashes = [self.hash(edge[0:2]) for edge in self.edges if edge[2] == "lemma-form"]
		nodesclean = []

		#Update triples according to new edges
		triples = [triple for triple in self.triples if self.hash(triple[0:2]) in hashes]
		edges = []

		i = 0
		while i < len(triples):
			triple = triples[i]
			for tripleBis in triples[i:]:
				if tripleBis[2] == triple[2]:
					edges.append([triple[0], tripleBis[0], triple[2]])
					nodesclean.append(triple[0])
					nodesclean.append(tripleBis[0])
			i += 1

		self.edges = edges
		nodesclean = list(set(nodesclean))
		self.nodes = [node for node in nodes if node[0] in nodesclean]

		self.weight(terms = terms)

		if self.q:
			self.c.triples(self.q, {"nodes" : self.nodes, "edges" : self.edges})


	def weight(self, nodes = False, edges = False, terms = []):
		if nodes == False:
			nodes = self.nodes
		if edges == False:
			edges = self.edges

		terms = [node[0] for node in self.nodes if node[1] in terms]

		n = []
		for node in nodes:
			e = [row for row in edges if node[0] in row and (row[0] in terms or row[1] in terms)]
			n.append(node + [len(e)])

		self.nodes = n

	def gephi(self, mode="sentence", nodes = [], edges = [], labels = []):
		separator = "\t"
		if nodes == []:
			nodes = self.nodes
		if edges == []:
			edges = self.edges
		if mode == "lemma":
			nodesColumn = ["id", "label", "weight"]
			edgesColumn = ["target", "source", "sentence"]
			#self.weight()
		elif mode == "semantic":
			nodesColumn = labels
			edgesColumn = ["target", "source", "sentence"]
		else:
			nodesColumn = ["id", "label", "type", "document"]
			edgesColumn = ["target", "source", "type"]

		f = codecs.open(clothoFolder + "data/gephi/nodes.csv", "wt")
		f.write(separator.join(nodesColumn)+"\n")
		for node in nodes:
			f.write(separator.join([str(n).replace("\\n", " ").replace("\t", " ") for n in node])+"\n")
		f.close()

		f = codecs.open(clothoFolder + "data/gephi/edges.csv", "wt")
		f.write(separator.join(edgesColumn)+"\n")
		for edge in edges:
			f.write(separator.join([str(e) for e in edge])+"\n")
		f.close()

	def clusterNodes(self):
		nodes = self.nodes
		return nodes

	def mergeEdges(self):
		#Merge edges and give them weight
		newEdges = []
		indexEdges = {}

		i = 0
		for edge in self.edges:
			#Edge : source,target,weight
			hash1 = self.hash([edge[0], edge[1]])
			hash2 = self.hash([edge[1], edge[0]])

			if hash1 in indexEdges:
				newEdges[indexEdges[hash1]][2] += 1
			elif hash2 in indexEdges:
				newEdges[indexEdges[hash2]][2] += 1
			else:
				newEdges.append([edge[0], edge[1], 1])
				indexEdges[hash1] = i
				indexEdges[hash2] = i
				i += 1

		return newEdges

	def JSON(self, group = False):
		graph = {"nodes" : [], "links" : []}

		"""
		node : { "name": "Myriel","group": 1 }
		edge : {"source": 42, "target": 41, "value": 2 }
		"""

		NodeIndex = {}

		i = 0
		for node in self.nodes:
			if group:
				graph["nodes"].append({"name" : node[1], "weight" : node[2], "group" : node[3]})
			else:
				graph["nodes"].append({"name" : node[1], "weight" : node[2], "group" : 0})
			NodeIndex[node[0]] = i
			i += 1
		for edge in self.edges:
			graph["links"].append({"source" : NodeIndex[edge[0]], "target": NodeIndex[edge[1]], "value" : edge[2]})

		return graph

	def threshold(self, threshold = 1):
		nodes = []
		deleted = []
		edges = []

		for node in self.nodes:
			if node[2] <= threshold:
				deleted.append(node[0])
			else:
				nodes.append(node)

		for edge in self.edges:
			if edge[0] not in deleted and edge[1] not in deleted:
				edges.append(edge)

		self.nodes = nodes
		self.edges = edges
		return True

	def D3JSMatrix(self, threshold = False, cluster = False):
		D3 = D3JS()
		self.edges = self.mergeEdges()

		if cluster == True:
			self.lsa = LSA(nodes = self.nodes, edges = self.edges)
			self.nodes, self.edges = self.lsa.cluster(building = True)

		if threshold == True:
			self.threshold(1)

		graph = self.JSON(group = cluster)

		with codecs.open(clothoFolder + "data/D3JS/data.json", "w") as f:
			f.write(json.dumps(graph))
			f.close()

		with codecs.open(clothoFolder + "data/D3JS/index.html", "w") as f:
			f.write(D3.text())
			f.close()


	def ClothoWeb(self, terms = [], query = []):
		if len(terms) == 0:
			terms = self.terms
		if len(query) == 0:
			terms = self.query.q["terms"]
		C = Clotho(terms)
		C.save()
		return True

	def semanticMatrix(self, terms = [], query = []):
		""" Semantic matrix """

		sm = SMa(nodes = self.nodes, edges = self.edges, terms = terms)
		sm.dbpedia()
		sm.documents()
		sm.matrixify()
		sm.stats()
		sm.tfidf()

	def tfidfDistance(self, terms = [], query = []):
		""" TF-IDF for all lemma """
		sm = TFIDF(nodes = self.nodes, edges = self.edges, terms = terms)
		sm.matrixify()
		sm.stats()
		sm.tfidf()

	def semanticGephi(self, terms = []):
		sm = SMa(nodes = self.nodes, edges = self.edges, terms = terms)
		sm.dbpedia(definition = False)
		sm.gephi()
		self.gephi(mode = "semantic", nodes = sm.nodes, edges = sm.edges, labels = sm.labels)

	def corpus(self, data = {}):
		""" Generation of plain-text corpus by term """
		if len(data) == 0:
			data = self.terms
		C = Corpus(data)
		C.rawCorpus()

	def jsLDA(self, data = {}):
		""" Generation of plain-text corpus by term """
		if len(data) == 0:
			data = self.terms
		C = Corpus(data)
		C.LDA()

	def fourWords(self, data = {}):
		""" Generation of plain-text corpus by term """
		C = Corpus(data)
		C.windowCorpus(4)
		
class D3JS(object):
	def text(self):
		""" Return a string containing a basic html page.
		"""
		return """<!DOCTYPE html>
<html><head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8"><meta charset="utf-8">
<title>Co-occurrence output</title>
<style>
.background {
fill: #eee;
}

line {
stroke: #fff;
}

text.active {
fill: red;
}
svg {
font: 8px sans-serif;
}
</style>

<link rel="stylesheet" href="http://netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css">
<script src="http://d3js.org/d3.v2.min.js?2.8.1"></script>
</head>
<body>
<div class="container" style="margin-top:30px;">

<aside class="col-md-3">
<h1>Co-occurrence</h1>
<p>
Order:
<select id="order">
<option value="name">by Name</option>
<option value="count">by Frequency</option>
<option selected="selected" value="group">by Cluster</option>
</select>
</p>
<p>
Each colored cell represents two terms that appeared in the 
same sentence; darker cells indicate terms that co-occurred more 
frequently.
</p>
<p>
Use the drop-down menu to reorder the matrix and explore the data.
</p>
<p>
Built with <a href="http://d3js.org/">d3.js</a>.
</p>
<p>
Originally done by <a href="http://bost.ocks.org/mike/" rel="author">Mike Bostock</a>
</p>
</aside>
<section id="svg" class="col-md-9">
</section>

<script>

var margin = {top: 80, right: 0, bottom: 10, left: 80},
width = 720,
height = 720;

var x = d3.scale.ordinal().rangeBands([0, width]),
z = d3.scale.linear().domain([0, 4]).clamp(true),
c = d3.scale.category10().domain(d3.range(10));

var svg = d3.select("#svg").append("svg")
.attr("width", width + margin.left + margin.right)
.attr("height", height + margin.top + margin.bottom)
.style("margin-left", margin.left + "px")
.append("g")
.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

d3.json("data.json", function(clotho) {
console.log(clotho)
var matrix = [],
nodes = clotho.nodes,
n = nodes.length;

// Compute index per node.
nodes.forEach(function(node, i) {
node.index = i;
node.count = 0;
matrix[i] = d3.range(n).map(function(j) { return {x: j, y: i, z: 0}; });
});

// Convert links to matrix; count character occurrences.
clotho.links.forEach(function(link) {

matrix[link.source][link.target].z += link.value;
matrix[link.target][link.source].z += link.value;
matrix[link.source][link.source].z += link.value;
matrix[link.target][link.target].z += link.value;
nodes[link.source].count += link.value;
nodes[link.target].count += link.value;
});

// Precompute the orders.
var orders = {
name: d3.range(n).sort(function(a, b) { return d3.ascending(nodes[a].name, nodes[b].name); }),
count: d3.range(n).sort(function(a, b) { return nodes[b].count - nodes[a].count; }),
group: d3.range(n).sort(function(a, b) { return nodes[b].group - nodes[a].group; })
};

// The default sort order.
x.domain(orders.name);

svg.append("rect")
.attr("class", "background")
.attr("width", width)
.attr("height", height);

var row = svg.selectAll(".row")
.data(matrix)
.enter().append("g")
.attr("class", "row")
.attr("transform", function(d, i) { return "translate(0," + x(i) + ")"; })
.each(row);

row.append("line")
.attr("x2", width);

row.append("text")
.attr("x", -6)
.attr("y", x.rangeBand() / 2)
.attr("dy", ".32em")
.attr("text-anchor", "end")
.text(function(d, i) { return nodes[i].name; });

var column = svg.selectAll(".column")
.data(matrix)
.enter().append("g")
.attr("class", "column")
.attr("transform", function(d, i) { return "translate(" + x(i) + ")rotate(-90)"; });

column.append("line")
.attr("x1", -width);

column.append("text")
.attr("x", 6)
.attr("y", x.rangeBand() / 2)
.attr("dy", ".32em")
.attr("text-anchor", "start")
.text(function(d, i) { return nodes[i].name; });

function row(row) {
var cell = d3.select(this).selectAll(".cell")
.data(row.filter(function(d) { return d.z; }))
.enter().append("rect")
.attr("class", "cell")
.attr("x", function(d) { return x(d.x); })
.attr("width", x.rangeBand())
.attr("height", x.rangeBand())
.style("fill-opacity", function(d) { return z(d.z); })
.style("fill", function(d) { return nodes[d.x].group == nodes[d.y].group ? c(nodes[d.x].group) : null; })
.on("mouseover", mouseover)
.on("mouseout", mouseout);
}

function mouseover(p) {
d3.selectAll(".row text").classed("active", function(d, i) { return i == p.y; });
d3.selectAll(".column text").classed("active", function(d, i) { return i == p.x; });
}

function mouseout() {
d3.selectAll("text").classed("active", false);
}

d3.select("#order").on("change", function() {
clearTimeout(timeout);
order(this.value);
});

function order(value) {
x.domain(orders[value]);

var t = svg.transition().duration(2500);

t.selectAll(".row")
.delay(function(d, i) { return x(i) * 4; })
.attr("transform", function(d, i) { return "translate(0," + x(i) + ")"; })
.selectAll(".cell")
.delay(function(d) { return x(d.x) * 4; })
.attr("x", function(d) { return x(d.x); });

t.selectAll(".column")
.delay(function(d, i) { return x(i) * 4; })
.attr("transform", function(d, i) { return "translate(" + x(i) + ")rotate(-90)"; });
}

var timeout = setTimeout(function() {
order("group");
d3.select("#order").property("selectedIndex", 2).node().focus();
}, 5000);
});
</script>

</div>
</body>
</html>"""

class Clotho(object):
	def __init__(self, terms = [], query_terms = []):

		try:
			self.sql = SQL(web=True)
			self.con = self.sql.con
			self.origin = SQL()
		except:
			print "Unable to load SQL dependecy"

		self.terms = terms
		self.query_terms = query_terms
		self.saved = {"lemma" : {}, "sentence" : {}, "form": {}}
		self.url = {"thesaurus" : "http://www.perseus.tufts.edu/hopper/"}
		self.pythonUser = 0
		self.edges = []

		self.annot_index = {"Place" : 2, "Person" : 1, "Date" : 3, "Site" : 5}

	def setup(self):
		annotation_type = "INSERT INTO `annotation_type` VALUES (1,'Type','Type','dc:Type','lemma'),(2,'Polyphony','Polyphony','dc:Polyphony','sentence')"
		annotation_value = "INSERT INTO `annotation_value` VALUES (1,'Person','Person',1,'Person'),(2,'Place','Place',1,'Place'),(3,'Date','Date',1,'Date'),(4,'Irony','Irony',2,'Irony'),(5,'Site','Site',2,'Site')"
		with self.con:
			cur = self.con.cursor()
			cur.execute(annotation_type)
			cur.execute(annotation_value)

	def save(self):
		#We setup annotations
		self.setup()

		#First save every form , sentence, lemma
		#Then save their relationships
		#In the same time, we do some kind of nice thesaurus config
		for term in self.terms:
			self.query(self.terms[term])

		#So now, we kind of need the vote for lemma isn't it ?
		#Then save their vote	def lemma(self, lemma):
		self.form_vote()

		#Then we save the metadata:
		self.metadata()

	def metadata(self):
		with self.con:
			cur = self.con.cursor()
			cur.execute("SELECT id_document FROM sentence GROUP BY id_document")
			documents = [str(row[0]) for row in cur.fetchall()]
			documents = list(set(documents))
		with self.origin.con:
			cur2 = self.origin.con.cursor()
			for document in documents:
				cur2.execute("SELECT * FROM metadata WHERE document_id = %s ", [document])
				meta = cur2.fetchall()
				for data in meta:
					cur.execute("INSERT INTO metadata VALUES ( %s , %s , %s , %s , %s , %s , %s )", list(data))



	def lemma(self, lemma):
		if lemma[0] in self.saved["lemma"]:
			return self.saved["lemma"][lemma[0]]
		else:
			with self.con:
				cur = self.con.cursor()
				cur.execute("SELECT id_lemma FROM lemma WHERE text_lemma = %s LIMIT 1", [lemma[0]])
				d = cur.fetchone()

				if d != None:
					if len(d) == 1:
						return d[0]
				else:
					if lemma[0] in self.query_terms:
						query_lemma = 1
					else:
						query_lemma = 0
					cur.execute("INSERT INTO lemma (text_lemma, query_lemma) VALUES (%s, %s)", [lemma[0], query_lemma])
					r = self.con.insert_id()
					self.saved["lemma"][lemma[0]] = r

					if lemma[1] != None:
						self.annotation(r, lemma[1], vote = True)
					return r

	def annotation(self, id_lemma, value, vote = False):
		with self.con:
			cur = self.con.cursor()
			"""			"""

			cur.execute("INSERT INTO `annotation` (`id_annotation_type`, `id_annotation_value`,`id_user`,`table_target_annotation`,`id_target_annotation`) VALUES ('1' ,%s ,%s ,'lemma',%s); ", [self.annot_index[value], self.pythonUser, id_lemma])
			r = self.con.insert_id()
			if vote == True:
				self.annotation_vote(r)


	def annotation_vote(self, id_annotation):
		with self.con:
			cur = self.con.cursor()
			cur.execute("INSERT INTO annotation_vote (id_annotation, id_user, value) VALUES ( %s , %s , %s ) ", [id_annotation, self.pythonUser, 1])

	def form(self, form):
		if form in self.saved["form"]:
			return self.saved["form"][form]
		else:
			with self.con:
				cur = self.con.cursor()
				cur.execute("SELECT id_form  FROM form WHERE text_form = '" + form + "'")
				d = cur.fetchone()

				if d != None:
					if len(d) == 1:
						return d[0]
				else:
					cur.execute("INSERT INTO form (text_form) VALUES ('" + form + "')")
					r = self.con.insert_id()
					self.saved["form"][form] = r
					return r

	def sentence(self, sentence, text = False, boolean = False):
		if sentence in self.saved["sentence"]:
			if boolean:
				return True
			else:
				return self.saved["sentence"][sentence]
		else:
			with self.con:
				cur = self.con.cursor()
				if text:
					cur.execute("SELECT id_sentence FROM sentence WHERE text_sentence = %s AND id_document = %s LIMIT 1", [sentence, text])
				else:
					cur.execute("SELECT id_sentence FROM sentence WHERE text_sentence = %s LIMIT 1", [sentence])

				d = cur.fetchone()

				if d != None:
					if len(d) == 1:
						if boolean:
							return True
						else:
							return d[0]
				else:
					if boolean:
						return False
					else:
						if text:
							cur.execute("INSERT INTO sentence (text_sentence, id_document) VALUES ( %s, %s )", [sentence, text])
						else:
							cur.execute("INSERT INTO sentence (text_sentence) VALUES ( %s )", [sentence])
						r = self.con.insert_id()
						self.saved["sentence"][sentence] = r
						return r
		
	def relationship(self, sentence, form, lemma):
		with self.con:
			cur = self.con.cursor()
			cur.execute("INSERT INTO `lemma_has_form` (`id_lemma`,`id_form`,`id_sentence`)VALUES(%s, %s, %s)", [lemma,form,sentence])
			#edg = self.con.insert_id()


			self.edges.append([form, sentence, "form-sentence"])
			self.edges.append([lemma, form, "lemma-form"])

			return True

	def query(self, rows):
		#
		#	rows = [
		#		[form, lemma, text, sentence]
		#	]
		#
		for row in rows:
			if row[1] != False:
				
				if isinstance(row[2], basestring) != True:
					id_document = row[2][1]
				else:
					id_document = row[2]

				if len(row[1]) == 0:
					s = self.sentence(row[3], id_document)
					l = 0
					f = self.form(row[0])

					self.relationship(s,f,l)
				else:
					for lemma in row[1]:

						s = self.sentence(row[3], id_document)
						l = self.lemma(lemma)
						f = self.form(row[0])

						self.relationship(s,f,l)

	def form_vote_sql(self, edges):
		with self.con:
			cur = self.con.cursor()
			for edge in edges:
				lemma = edge[0]
				form = edge[1]

				query = cur.execute("SELECT id_lemma_has_form FROM lemma_has_form WHERE id_lemma = %s AND id_form = %s ", [lemma, form])
				datas = cur.fetchall()
				for data in datas:
					id_form_vote = int(data[0])
					query2 = cur.execute("INSERT INTO form_vote (id_lemma_has_form, id_user, value) VALUES ( %s , %s ,  %s )", [id_form_vote, self.pythonUser, 1])

		return True

	def form_vote(self):
		compute = {"lemma" : {}, "form": {}}
		#We build an index
		for edge in self.edges:
			if edge[2] == "lemma-form":
				#Lemma
				lemma = str(edge[0])
				if lemma not in compute["lemma"]:
					compute["lemma"][lemma] = []
				#Form
				form = str(edge[1])
				if form not in compute["form"]:
					compute["form"][form] = []

				compute["lemma"][lemma].append(edge[1])
				compute["form"][form].append(edge[0])

		#We give to our edges the one which are not lemma-form AND the one which have only one possibility
		newcompute = {}
		#Then we need to find a way to compute stuff isn't it ?
		#Basically, we want the one with the biggest compute[lemma] in compute[form]

		for form in compute["form"]:
			f = str(form)
			if len(compute["form"][f]) > 1:
				Max = float(0)
				MaxId = str(0)
				for lemma in compute["form"][f]:
					l = str(lemma)
					computed = float(0)
					for other_form in compute["lemma"][l]:
						of = str(other_form)
						computed += float(1 / float(len(compute["form"][of])))
					if MaxId == 0 or computed > Max:
						MaxId = l
						Max = computed
				newcompute[f] = [MaxId]
			else:
				newcompute[f] = compute["form"][f]

		edges = [[newcompute[edge][0], edge] for edge in newcompute]

		self.form_vote_sql(edges)

		return True

class LSA(object):
	def __init__(self, nodes, edges):
		self.wdict = {}
		self.wcount = 0
		self.nodes = nodes
		self.edges = edges
		self.matrix = numpy.mat(numpy.zeros([len(self.nodes), len(self.nodes)]), int)

	def build(self):
		""" Build a matrix, needs an instance of self
		"""
		for node in self.nodes:
			self.wdict[node[0]] = self.wcount
			self.wcount += 1

		for edge in self.edges:
			self.matrix[self.wdict[edge[0]], self.wdict[edge[1]]] += 1
			self.matrix[self.wdict[edge[1]], self.wdict[edge[0]]] += 1

		self.matrix = self.matrix * self.matrix

		return self.matrix

	def cluster(self, building = False):
		""" Cluster a matrix

		keywords argument:
		building -- Whether the matrix should be build before or not.
		"""
		if building == True:
			self.build()
			
		clustering = sklearn.cluster.spectral_clustering(self.matrix)

		i = 0
		for id in clustering:
			self.nodes[i].append(int(id + 1))
			i += 1

		return self.nodes, self.edges

	def findzeros(self):
		""" Return the number of 0 in the matrix
		"""
		z =0
		if 0 in self.matrix.flat:
			z += 1
		return z

class SMa(object):
	def __init__(self, nodes = [], edges = [], terms = [], prevent = False):
		"""	Initialize

		Keyword arguments
		nodes -- List of nodes using list -> [[idNode, textNode, whatever...], etc.]
		edges -- List of edges [[idNode1, idNode2, idSentence], etc.]
		terms -- Query terms
		prevent -- Prevent autocompute for debugging
		"""
		self.r = requests

		self.rdf = rdflib.Graph()
		self.cache = Cache()
		self.semes= {}
		self.dbpedia_url = "http://dbpedia.org/resource/"

		if prevent == False:
			temp_nodes = nodes
			self.edges = edges

			self.matrix = []
			self.lemma = {}
			self.terms = {}

			#We split nodes informations between terms and lemma, eg : latest being example found 
			for node in temp_nodes:
				if node[1] not in terms:
					self.lemma[node[0]] = node[1]
				else:
					self.terms[node[0]] = node[1]
	def addslashes(self, s):
		l = ["\\", '"', "'", "\0", ]
		for i in l:
			if i in s:
				s = s.replace(i, '\\'+i)
		return s
	def definition(self, url):
		sparql = SPARQLWrapper("http://dbpedia.org/sparql")

		punctuation = (';', ':', ',', '.', '!', '?', '(', ')', '-', "'", '"')
		sparql.setQuery("""SELECT str(?desc) 
					where {
					  <"""+url+"""> <http://www.w3.org/2000/01/rdf-schema#comment> ?desc
					  FILTER (langMatches(lang(?desc),"en"))
					} LIMIT 1""")
		sparql.setReturnFormat(JSON)
		results = sparql.query().convert()
		stopword = nltk.corpus.stopwords.words("english")

		if len(results["head"]["vars"]) > 0:
			var = results["head"]["vars"][0]
			if len(results["results"]["bindings"]) == 1:
				return [w for w in nltk.tokenize.word_tokenize(results["results"]["bindings"][0][var]["value"]) if w not in stopword and w not in punctuation]
			else:
				return []
		else:
			return []

	def sparql(self, name):

		sparql = SPARQLWrapper("http://dbpedia.org/sparql")
		sparql.setQuery("""
			PREFIX foaf: <http://xmlns.com/foaf/0.1/>
			SELECT ?url WHERE {
			  ?url a ?type;
			     foaf:name '""" + self.addslashes(name)  + """@en .
			} LIMIT 1
			""")
		sparql.setReturnFormat(JSON)
		results = sparql.query().convert()

		if len(results["results"]["bindings"]) == 1:
			return results["results"]["bindings"][0]["url"]["value"]
		else:
			return False

	def load(self, url):
		f = self.cache.rdf(url, check = True)
		if f == False:
			statusCode = 0
			tentative = 0
			while statusCode != self.r.codes.ok and tentative <= 5:
				try:
					r = self.r.get(url, headers = {
						"accept" : 'application/rdf+xml,text/rdf+n3;q=0.9,application/xhtml+xml'
					}, timeout = 5)
					statusCode = r.status_code
				except:
					statusCode = 0
					tentative += 1

				self.cache.rdf(url, data = r)
				self.rdf.load(self.cache.rdf(url, check = True))
		else:
			self.rdf.load(f)

	def lookup(self, url):
		""" 
		Inspired by https://github.com/abgoldberg/tv-guests/blob/master/dbpedia.py

		"""
		l = {}

		self.rdf = rdflib.Graph()
		self.currentUrl = url
		self.load(url)
		if len(self.rdf) == 0:
			results = wikipedia.search(url.split("/")[-1])
			if len(results) > 0:
				input = results[0] # -> Page Name
				url = self.sparql(input)
				if url == False:
					return {}
				self.currentUrl = url
				l = self.lookup(url)
				return l
		else:

			for s,p,o in self.rdf:
				"""We construct a json whith the following structure :
				# Name : md5(url).json
				# {
					p : [o]
				}
				"""
				pp = unicode(p.toPython()).encode("utf-8")
				oo = unicode(o.toPython()).encode("utf-8")
				if pp not in l:
					l[pp] = []
				if pp == "http://dbpedia.org/ontology/wikiPageRedirects" and oo != url:
					self.currentUrl = oo
					return self.lookup(oo)
				l[pp].append(oo)
			return l

	def dbpedia(self, definition = True):
		for lem in self.lemma:
			l = self.lemma[lem]
			c = False
			#print "Looking for " + l
			url = self.dbpedia_url + l
			self.currentUrl = url
			#Checking if exist
			c = self.cache.dbpedia(url)
			if c == False:
				l = self.lookup(url)
				self.cache.dbpedia(url, l)
			else:
				l = c

			d = self.cache.definition(self.currentUrl)
			if d == False:
				d = self.definition(self.currentUrl)
				self.cache.definition(self.currentUrl, d)
			else:
				d = d

			self.semes[self.lemma[lem]] = Term(l)

			if definition == True:
				self.semes[self.lemma[lem]].definition(d)

	def documents(self):
		"""	Returns a list of document given nodes and edges so we can perform tf-idf 

		Keyword arguments :
		"""
		properties = {}
		reversedProperties = {}
		document = {}

		for exempla in self.semes:
			seme = self.semes[exempla]
			if exempla not in document:
				document[exempla] = []
			for propertyItem in seme.graph:
				for prop in seme.graph[propertyItem]:
					pprop = propertyItem + ":" + prop
					if pprop not in properties:
						l = len(properties)
						properties[pprop] = l
						reversedProperties[l] = pprop
					document[exempla].append(properties[pprop])


		self.document = document
		self.properties = properties
		self.reversedProperties = reversedProperties
		return True

	def cleanProperty(self, prop):
		r = re.compile("([A-Za-z]+)[0-9]+")
		p = r.match(prop)
		if p:
			return p.group(1)
		else:
			return prop

	def gephi(self, liste = True):
		""" Get the gephi representation of the matrix
		"""
		self.nodes = {}
		self.csvIndex = {"id": 0, "label" : 1, "type" : 2}
		indexes = ["id", "label", "type"]


		for term in self.terms:
			self.nodes[term] = {"label" : self.terms[term], "id" : term, "type" : "term"}
		edges = self.edges
		self.edges = [edge for edge in self.edges if edge[0] != edge[1] and edge[0] in self.nodes]
		for e in [edge for edge in edges if edge[0] != edge[1] and edge[1] in self.nodes]:
			self.edges += [e[1], e[0]]

		for lemma in self.lemma:

			self.nodes[lemma] = self.semes[self.lemma[lemma]].graph
			self.nodes[lemma]["label"] = self.lemma[lemma]
			self.nodes[lemma]["id"] = lemma
			self.nodes[lemma]["type"] = "entity"

		#Now we have the whole set of nodes
		#We need to extract all information so it would feet into a CSV...
		i = 3
		if liste:
			for node in self.nodes:
				for prop in self.nodes[node]:
					if prop not in indexes:
						if prop not in self.csvIndex:
							self.csvIndex[prop] = i
							i += 1

			nodes = []
			for node in self.nodes:
				n = [0] * len(self.csvIndex)
				for prop in self.nodes[node]:
					if isinstance(self.nodes[node][prop], list):

						n[self.csvIndex[prop]] = ",".join([self.cleanProperty(elem) for elem in self.nodes[node][prop]])
					else:
						n[self.csvIndex[prop]] = self.nodes[node][prop]
				nodes.append(n)

			labels = sorted(self.csvIndex.iteritems(), key=operator.itemgetter(1))
			self.labels = [label[0] for label in labels]
		else: #Returns properties as nodes
			for node in self.nodes:
				for prop in self.nodes[node]:
					if prop not in indexes:
						for elem in self.nodes[node][prop]:
							el = self.cleanProperty(elem)
							if el not in self.csvIndex:
								self.csvIndex[el] = i
								i += 1

			nodes = []
			for node in self.nodes:
				n = [0] * len(indexes)
				for prop in self.nodes[node]:
					if isinstance(self.nodes[node][prop], list):
						for elem in self.nodes[node][prop]:
							el = self.cleanProperty(elem)
							self.edges.append([node, self.csvIndex[el], 1])
					else:
						n[self.csvIndex[prop]] = self.nodes[node][prop]
				nodes.append(n)


			for element in self.csvIndex:
				if element not in indexes:
					el = self.cleanProperty(elem)
					nodes.append([self.csvIndex[el], el, "property"])

			self.labels = indexes
		self.nodes = nodes

	def matrixify(self):
		m = []
		ms = []
		#We get all terms
		for term in self.terms:
			t = []
			ts = []
			#We get all linked lemma
			for edge in [e for e in self.edges if term in e]:
				if edge[0] == term:
					otherEdge = edge[1]
				else:
					otherEdge = edge[0]
				if otherEdge not in self.terms:
					#Now we get the document informations
					t += self.document[self.lemma[otherEdge]]
					ts += [1]
			#Just a temp check
			#t = [self.reversedProperties[prop] for prop in t]
			#End temp check
			if len(t) > 0:
				m.append(t)
				ms.append(ts)
			else:
				self.terms[term] = False

		#Now we have a matrix with ids of item, now let make a real matrix
		matrix = []
		self.prematrix = ms
		for mm in m:
			t = [0]*len(self.properties) #We fill the matrix
			for e in mm:
				t[e] += 1
			matrix.append(t)

		self.matrix = matrix
		return self.matrix


	def stats(self):
		labels = [self.terms[t] for t in self.terms if self.terms[t] != False]
		sums = [sum([1 for p in m if p > 1]) for m in self.prematrix]
		for i, s in enumerate(sums):
			print labels[i] + "\t" + str(s)

	def tfidf(self):
		tfidf_matrix = []
		#TF = frequency in first list / max frequency available in document
		for term_matrix in self.matrix:
			term_tfidf_matrix = [0]*len(term_matrix)
			maxTF = float(max(term_matrix))
			i = 0
			for term in term_matrix:
				tf = float(term) / maxTF
				idf = float(len(term_matrix)) / (1.0 + float(len([1 for other_matrix in self.matrix if other_matrix[i] != 0])))
				term_tfidf_matrix[i] = tf * log(idf)
				i += 1
			tfidf_matrix.append(term_tfidf_matrix)

		self.tfidf_matrix = tfidf_matrix

		self.vectors = [numpy.array(f) for f in tfidf_matrix]

		U,s,V = numpy.linalg.svd(self.vectors) # svd decomposition of A
		print "Vectors created", len(self.vectors[0]), "after SVD decomposition", len(U)

		#clusterer = nltk.cluster.GAAClusterer(num_clusters=3)
		#clusters = clusterer.cluster(self.vectors, True)

		# print "Means: ", clusterer.means()
		labels = [self.terms[t] for t in self.terms if self.terms[t] != False]
		#clusterer.dendrogram().show(leaf_labels = labels )


		#Using a distance matrix
		distMatrix = scipy.spatial.distance.pdist(self.tfidf_matrix)
		distSquareMatrix = scipy.spatial.distance.squareform(distMatrix)

		#calculate the linkage matrix
		fig = pylab.figure(figsize=(10,10))
		linkageMatrix = scipy.cluster.hierarchy.linkage(distSquareMatrix, method = 'ward')
		dendro = scipy.cluster.hierarchy.dendrogram(linkageMatrix,orientation='left', labels=labels)
		fig.savefig('dendrogram.png')

		#Using KMEANS
		clusterer = nltk.cluster.KMeansClusterer(3, nltk.cluster.euclidean_distance, repeats=10, avoid_empty_clusters=True)
		answer = clusterer.cluster(self.vectors, True)

	def pprint(self):
		print self.semes

class TFIDF(object):
	def __init__(self, nodes = [], edges = [], terms = [], prevent = False):
		"""	Initialize

		Keyword arguments
		nodes -- List of nodes using list -> [[idNode, textNode, whatever...], etc.]
		edges -- List of edges [[idNode1, idNode2, idSentence], etc.]
		terms -- Query terms
		prevent -- Prevent autocompute for debugging
		"""
		self.semes = {}

		#Need a dictionary and reversed dictionary
		temp_nodes = nodes
		self.edges = edges
		self.nodes = nodes

		self.matrix = []
		self.lemma = {}
		self.terms = {}
		self.total = {}
		self.reversed = []

		#We split nodes informations between terms and lemma, eg : latest being example found 
		for node in temp_nodes:
			if node[1] not in terms:
				i = len(self.reversed)
				self.lemma[node[0]] = i
				self.reversed.append(node[0])
			else:
				self.terms[node[0]] = node[1]
				self.total[node[0]] = 0

		print self.lemma

	def matrixify(self):
		m = []
		#We get all terms
		for term in self.terms:
			t = []
			#We get all linked lemma
			for edge in [e for e in self.edges if term in e]:
				if edge[0] == term:
					otherEdge = edge[1]
				else:
					otherEdge = edge[0]
				if otherEdge not in self.terms:
					#Now we get the document informations
					idLemma = self.lemma[otherEdge]
					t += [idLemma]
					self.total[term] += 1

			if len(t) > 0:
				m.append(t)
			else:
				self.terms[term] = False

		#Now we have a matrix with ids of item, now let make a real matrix
		matrix = []
		for mm in m:
			t = [0]*len(self.lemma) #We fill the matrix
			for e in mm:
				t[e] += 1
			matrix.append(t)

		self.matrix = matrix
		return self.matrix

	def stats(self):
		labels = [self.terms[t] for t in self.terms if self.terms[t] != False]
		print self.matrix
		print self.terms
		sums = [sum(m) for m in self.matrix]
		for i, s in enumerate(sums):
			print labels[i] + "\t" + str(s)


	def tfidf(self):
		tfidf_matrix = []
		#TF = frequency in first list / max frequency available in document
		for term_matrix in self.matrix:
			term_tfidf_matrix = [0]*len(term_matrix)
			maxTF = float(max(term_matrix))
			i = 0
			for term in term_matrix:
				tf = float(term) / maxTF
				idf = float(len(term_matrix)) / (1.0 + float(len([1 for other_matrix in self.matrix if other_matrix[i] != 0])))
				term_tfidf_matrix[i] = tf * log(idf)
				i += 1
			tfidf_matrix.append(term_tfidf_matrix)

		self.tfidf_matrix = tfidf_matrix

		self.vectors = [numpy.array(f) for f in tfidf_matrix]

		U,s,V = numpy.linalg.svd(self.vectors) # svd decomposition of A
		print "Vectors created", len(self.vectors[0]), "after SVD decomposition", len(U)

		#clusterer = nltk.cluster.GAAClusterer(num_clusters=3)
		#clusters = clusterer.cluster(self.vectors, True)

		# print "Means: ", clusterer.means()
		labels = [self.terms[t] for t in self.terms if self.terms[t] != False]
		#clusterer.dendrogram().show(leaf_labels = labels )


		#Using a distance matrix
		distMatrix = scipy.spatial.distance.pdist(self.tfidf_matrix)
		distSquareMatrix = scipy.spatial.distance.squareform(distMatrix)

		#calculate the linkage matrix
		fig = pylab.figure(figsize=(10,10))
		linkageMatrix = scipy.cluster.hierarchy.linkage(distSquareMatrix, method = 'ward')
		dendro = scipy.cluster.hierarchy.dendrogram(linkageMatrix,orientation='left', labels=labels)
		fig.savefig('dendrogram.png')

		#Using KMEANS
		"""
		clusterer = nltk.cluster.KMeansClusterer(3, nltk.cluster.euclidean_distance, repeats=10, avoid_empty_clusters=True)
		answer = clusterer.cluster(self.vectors, True)
"""
	def pprint(self):
		print self.semes


class Term(object):
	def __init__(self, json):
		self.json = json

		self.graph = {}

		self.yago = re.compile("(\w*)[0-9]*")
		self.category = re.compile("Category:(\w*)")
		self.avoid = [u'rdf-schema#comment', u'wikiPageExternalLink', u'hasPhotoCollection', u'isPrimaryTopicOf', u'id', u'viaf', u'influenced',  u'influencedBy',  u'influences', u"owl#sameAs", u'abstract', u'wikiArticles', u'wikiPageDisambiguates', u'wikiPageExternalLink', u'wikiPageID', u'wikiPageInLinkCount', u'wikiPageOutLinkCount', u'wikiPageRedirects',u'thumbnail', u'wikiPageRevisionID', u'rdf-schema#comment', u'site', u'rdf-schema#label',u'prov#wasDerivedFrom']
		self.keep = [u"subject", u"22-rdf-syntax-ns#type", u"placeOfDeath", u"placeOfBirth", u"country", ]
		if json:
			for p in json:
				pp = self.toString(p)
				if pp in self.keep:
					self.graph[pp] = []
					for o in json[p]:
						oo = self.toString(o)
						if self.yago.match(oo):
							oo = self.yago.search(oo).group(1)
						elif self.category.match(oo):
							oo = self.category.search(oo).group(1)
						if oo not in self.graph[pp]:
							self.graph[pp].append(oo)

	def toString(self, url):
		if url[0:7] == "http://":
			value = url.split("/")
			return value[-1]
		else:
			return url

	def pprint(self):
		pprint(self.graph)

	def definition(self, d):
		self.graph["DBPediaDEF"] = d

class Query(object):
	
	def __init__(self, e = False):
		self.q = {
			"name" : "",
			"terms" : [],
			"mode" : ""
		}
		self.dateRegexp = re.compile("(-?[0-9]+|\?)\;(-?[0-9]+|\?)")
		self.sql =SQL()
		self.exportLemma = ["semantic-matrix", "tfidf-distance", "semantic-gephi"]

	def defineExport(self, e):
		self.export = e
		self.means = self.export.options

	def setupExplanation(self):
		print """
	This file is here to provide a setup functionnality
	It will setup the environment so we have :
		- an identifier for MySQL
		- created database
		- download necessary items from the web

	In cache there should be a json file with everything related to the configuration
	{
		"MySQL" : {
			"identifiers" : {
				"user" : $username,
				"password" : $password
			},
			"database" : {
				"perseus" : Name of the database for perseus dump,
				"cache" : Name of the database for cache,
				"web" : Name of the database for Clotho Web,
				"results" : Name of the database for the results to be stored
			}
		}
	}"""

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
		if options:
			s = ""
			for i in range(0, len(options)):
				s += " \n\t[ " + str( i ) + " ] " + options[i]
			answer = raw_input(question + s + "\n")
		else:
			answer = raw_input(question + "\n")

		if answer.isdigit():
			if options:
				if int(answer) in range(0, len(options)):
					return options[int(answer)]
				else:
					return self.options(question, options)
			return int(answer)
		else:
			if options and answer in options:
				return answer
			return self.options(question, options)

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

	def mode(self):
		return self.options("Mode :", ["Lemma", "Exempla"])

	def config(self):
		self.deco()
		self.q["name"] = raw_input("Name your query : \n - ")
		print "You choosed " + self.q["name"]

		print "Choose your modes :"
		self.q["mode"] = self.mode()
		print "You choosed " + self.q["mode"]

		"""	To be included later
		self.q["threshold"] = self.yn("Do you want to apply a date threshold ?")
		print "You choosed " + self.q["threshold"]
		"""

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
		if q.isdigit() and int(q) in correctAnswers:
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


	def exportMean(self, e = False, deco = False):
		if e:
			self.export = e
			availableMeans = self.export.options
		if deco:
			self.deco()

		means = []
		i = 0
		for mean in availableMeans:
			means.append(mean)
			i += 1

		s = self.options("Which mean of export do you want to use ? ", means)
		print s
		if s in availableMeans:
			return s
		elif  s.isdigit() and int(s) < len(availableMeans):
			return availableMeans[int(s)]
		else:
			self.inputError(s)
			return self.exportMean(e, deco)

	def cleanProbability(self, deco = True):
		if deco:
			self.deco()

		s = self.yn("Clean based on probability ?")
		if s == "y":
			return True
		else:
			return False


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

	def D3JS(self, q, e):
		cluster = q.clustering()
		threshold =q.thresholdOne()
		e.D3JSMatrix(threshold = threshold, cluster = cluster)
		filepath = os.path.dirname(os.path.abspath(__file__)) + "/data/D3JS/index.html"
		try:
			import webbrowser
			webbrowser.open("file://"+filepath,new=2)
		except:
			print "File available at " + filepath


class PyLucene(object):
	def __init__(self):
		try:
			import lucene
			#Java imports
			from java.io import File
			from org.apache.lucene.store import MMapDirectory
			from org.apache.lucene.analysis.standard import StandardAnalyzer
			from org.apache.lucene.search import IndexSearcher
			from org.apache.lucene.util import Version
			from org.apache.lucene.queryparser.classic import QueryParser
			from org.apache.lucene.index import DirectoryReader
			self.lucene = True
			lucene.initVM()
			indexDir = "texts/index"
			directory = MMapDirectory(File(indexDir))
			directory = DirectoryReader.open(directory)
			self.analyzer = StandardAnalyzer(Version.LUCENE_30)
			self.searcher = IndexSearcher(directory)
			self.regexp = re.compile("(Perseus:text:[0-9]{4}\.[0-9]{2}\.[0-9]{4})")
		except:
			self.lucene = False

	def query(self, terms = []):
		import lucene
		#Java imports
		from java.io import File
		from org.apache.lucene.store import MMapDirectory
		from org.apache.lucene.analysis.standard import StandardAnalyzer
		from org.apache.lucene.search import IndexSearcher
		from org.apache.lucene.util import Version
		from org.apache.lucene.queryparser.classic import QueryParser
		from org.apache.lucene.index import DirectoryReader
		query = QueryParser(Version.LUCENE_30, "text", self.analyzer).parse(" OR ".join(terms))
		MAX = 1000
		hits = self.searcher.search(query, MAX)

		resTemp = []
		results = []
		done = {}
		for hit in hits.scoreDocs:
			doc = self.searcher.doc(hit.doc)
			resTemp.append([self.regexp.search(doc.get("doc_id").encode("utf-8")).group(1), doc.get("head").encode("utf-8")])#, doc.get("doc_id").encode("utf-8")])

		#print results
		for res in resTemp:
			if res[0] not in done:
				done[res[0]] = [res[1]]
				results.append(res)
			elif res[1] not in done[res[0]]:
				done[res[0]].append(res[1])
				results.append(res)
		return results

	def occurencies(self, term, morphs):
		query = []
		already = []

		for morph in morphs:
			query.append(morph)
			#Sometime, when there is doubt about a term, because of xml hashing in Lucene, you would find twice a lemma like wordword
			query.append(morph+morph)

		results = self.query(query)

		resultsReturned = []
		for result in results:
			if result[0] not in already:
				resultsReturned.append(result)
				already.append(result[0])

		return resultsReturned, len(resultsReturned)

	def chunk(self, occurency):
		#Could be updated using the section information but could be only milesone

		return occurency#, len(occurency)