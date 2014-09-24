#!/usr/bin/python
# -*- coding: utf-8 -*-

from classes import Query, Setup

q = Query()
s = Setup()

q.welcome()
q.setupExplanation()
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
