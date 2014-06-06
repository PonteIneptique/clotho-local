#!/usr/bin/python
# -*- coding: utf-8 -*-
from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
name = "Lucius Fundanius Lamia Aelianus"
sparql.setQuery("""
	PREFIX foaf: <http://xmlns.com/foaf/0.1/>
	SELECT ?url WHERE {
	  ?url a ?type;
	     foaf:name '""" + name + """'@en .
	} LIMIT 1
	""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

if len(results["results"]["bindings"]) == 1:
	print results["results"]["bindings"][0]["url"]["value"]
else:
	print false