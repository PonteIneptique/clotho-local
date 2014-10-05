#!/usr/bin/python
# -*- coding: utf-8 -*-

import Linguistic
import Data
import Services

Config = {
	"Linguistic" : {
		"Contextualiser" : {
			"use" : Linguistic.Contextualiser.Sentence,
			"Sentence" : {
				"FormFinder" : Services.Perseus.MySQL.LatinFormFinder
			}
		}
	}
}