#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os


from Data import Models
import Services.Perseus

from Services.Perseus import MySQL as Perseus
from Services.Perseus.MySQL import Lemma
from Linguistic.Contextualiser.syntax import WordWindow as Contextualiser
from Services.Perseus.MySQL import Occurence
from Services.Perseus.MySQL import LatinLemmatizer as FormFinder
from Services.Perseus.MySQL import LatinLemmatizer as Lemmatizer

#Set up with real data
LemmaSearchEngine = Lemma()
SearchEngine = Occurence()
ContextMaker = Contextualiser(FormFinderClass = FormFinder)
LemmatizerEngine = Lemmatizer()

LemmaEntity = LemmaSearchEngine.search("habeo", strict = True)[0]


occurences_raw = SearchEngine.search(LemmaEntity)[0:4]
occurences = []

#Context test
for occurence in occurences_raw:
	occurences += ContextMaker.strip(occurence, LemmaEntity)

#occurences is not a list of List(Occurences) which have been refined
#But we need fo get a lemmatized version of it 

occurences = [LemmatizerEngine.getLemmas(occurence) for occurence in occurences]