#!/usr/bin/python
# -*- coding: utf-8 -*-




explanation = """
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
	}
"""


from classes.query import Query
from classes.setup import Setup

q = Query()
s = Setup()

print q.welcome()
print explanation
q.deco()
#Check dependecies
s.dependency()
q.deco()


#Check texts
s.sgml()
q.deco()

#Download dependency files before mysql
s.morph()
q.deco()

#First the database logons
s.conf["MySQL"]["identifiers"] = s.sqlId()
s.write()
q.deco()

#Then the databases' name
s.dbs()
s.write()
q.deco()

#Then the table
q.deco()
s.tables()
q.deco()