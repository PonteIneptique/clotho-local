#!/usr/bin/python
# -*- coding: utf-8 -*-
from classes.semanticMatrix import SMa

sma = SMa(prevent = True)
sma.lemma = {"125" : "Cicero", "984" : "Vergilius"}
sma.dbpedia()