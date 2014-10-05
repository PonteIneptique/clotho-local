#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys 
sys.path.append("../..")

import Linguistic.Contextualiser.common
import Data.Models

class WordWindow(Linguistic.Contextualiser.common.Model):

	def __init__(self):
		self.mode = "Sentence"

	def strip(self, occurence, lemma):
		pass