#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys 
sys.path.append("../..")

from common import Model
import Data.Models

class WordWindow(Model):

	def __init__(self):
		self.mode = "Sentence"

	def strip(self, occurence, lemma):
		pass