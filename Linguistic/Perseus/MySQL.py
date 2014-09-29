#!/usr/bin/python
# -*- coding: utf-8 -*-

CONSTANT_DATA_STORAGE = "MySQL"
import sys

sys.path.append("../..")
from Data import Models
import Linguistic.lang as lang

if CONSTANT_DATA_STORAGE == "MySQL":
	from Data import MySQL

	Table = MySQL.Table
	Field = MySQL.Field
	Connection = MySQL.Connection

class Config(object):
	def __init__(self):
		pass

class Lemma(lang.Lemma):
	def search(self, w):
		pass

l = Lemma()
l.search("w")