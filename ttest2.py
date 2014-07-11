#!/usr/bin/python
# -*- coding: utf-8 -*-

#Python CORE
import os
import sys
import codecs
import hashlib
import json
from pprint import pprint

"""
	Order of classes :
		- Corpus (Corpus Generator for R)
		- Export (General Export connector class)
		- D3JS
"""
class Corpus(object):
	def __init__(self, data = {}, flexed = False):
		self.folder = "./data/corpus/"
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
			with codecs.open("./data/corpus/" + term + ".txt", "w") as f:
				f.write(data[term])
				f.close()
		return True

	def rawCorpus(self, data = False):
		if not self.data:
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

	def windowSentence(self, term = "", sentence = [], window = 0):
		if len(sentence) <= 0:
			return sentence


		indexTerm = 0
		min_index = 0
		max_index = len(sentence) - 1
		length = window * 2 + 1

		for i in range(0,  max_index):
			lemma = sentence[i]
			if term in lemma:
				indexTerm = i 

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


testData = {"ebriosus": [["Legimus", [["lego", None]], "Tertullianus - De anima (CPL 0017) ", "Legimus quidem pleraque aquarum genera miranda, sed aut ebriosos reddit lyncestarum uena uinosa  aut lymphaticos efficit colophonis scaturigo daemonica aut alexandrum occidit nonacris arcadiae  uenenata. "], ["pleraque", [["pleraque", None]], "Tertullianus - De anima (CPL 0017) ", "Legimus quidem pleraque aquarum genera miranda, sed aut ebriosos reddit lyncestarum uena uinosa  aut lymphaticos efficit colophonis scaturigo daemonica aut alexandrum occidit nonacris arcadiae  uenenata. "], ["aquarum", [["aqua", None]], "Tertullianus - De anima (CPL 0017) ", "Legimus quidem pleraque aquarum genera miranda, sed aut ebriosos reddit lyncestarum uena uinosa  aut lymphaticos efficit colophonis scaturigo daemonica aut alexandrum occidit nonacris arcadiae  uenenata. "], ["genera", [["genero", None], ["genus", None]], "Tertullianus - De anima (CPL 0017) ", "Legimus quidem pleraque aquarum genera miranda, sed aut ebriosos reddit lyncestarum uena uinosa  aut lymphaticos efficit colophonis scaturigo daemonica aut alexandrum occidit nonacris arcadiae  uenenata. "], ["miranda", [["miro", None], ["mirandus", None], ["miror", None]], "Tertullianus - De anima (CPL 0017) ", "Legimus quidem pleraque aquarum genera miranda, sed aut ebriosos reddit lyncestarum uena uinosa  aut lymphaticos efficit colophonis scaturigo daemonica aut alexandrum occidit nonacris arcadiae  uenenata. "], ["ebriosos", [["ebriosus", None]], "Tertullianus - De anima (CPL 0017) ", "Legimus quidem pleraque aquarum genera miranda, sed aut ebriosos reddit lyncestarum uena uinosa  aut lymphaticos efficit colophonis scaturigo daemonica aut alexandrum occidit nonacris arcadiae  uenenata. "], ["reddit", [["reddo", None]], "Tertullianus - De anima (CPL 0017) ", "Legimus quidem pleraque aquarum genera miranda, sed aut ebriosos reddit lyncestarum uena uinosa  aut lymphaticos efficit colophonis scaturigo daemonica aut alexandrum occidit nonacris arcadiae  uenenata. "], ["uena", [["venum", None], ["vena", None]], "Tertullianus - De anima (CPL 0017) ", "Legimus quidem pleraque aquarum genera miranda, sed aut ebriosos reddit lyncestarum uena uinosa  aut lymphaticos efficit colophonis scaturigo daemonica aut alexandrum occidit nonacris arcadiae  uenenata. "], ["uinosa", [["vinosus", None]], "Tertullianus - De anima (CPL 0017) ", "Legimus quidem pleraque aquarum genera miranda, sed aut ebriosos reddit lyncestarum uena uinosa  aut lymphaticos efficit colophonis scaturigo daemonica aut alexandrum occidit nonacris arcadiae  uenenata. "], ["lymphaticos", [["lymphaticus", None]], "Tertullianus - De anima (CPL 0017) ", "Legimus quidem pleraque aquarum genera miranda, sed aut ebriosos reddit lyncestarum uena uinosa  aut lymphaticos efficit colophonis scaturigo daemonica aut alexandrum occidit nonacris arcadiae  uenenata. "], ["efficit", [["efficio", None]], "Tertullianus - De anima (CPL 0017) ", "Legimus quidem pleraque aquarum genera miranda, sed aut ebriosos reddit lyncestarum uena uinosa  aut lymphaticos efficit colophonis scaturigo daemonica aut alexandrum occidit nonacris arcadiae  uenenata. "], ["daemonica", [["daemonicus", None]], "Tertullianus - De anima (CPL 0017) ", "Legimus quidem pleraque aquarum genera miranda, sed aut ebriosos reddit lyncestarum uena uinosa  aut lymphaticos efficit colophonis scaturigo daemonica aut alexandrum occidit nonacris arcadiae  uenenata. "], ["alexandrum", [["Alexander", "Person"]], "Tertullianus - De anima (CPL 0017) ", "Legimus quidem pleraque aquarum genera miranda, sed aut ebriosos reddit lyncestarum uena uinosa  aut lymphaticos efficit colophonis scaturigo daemonica aut alexandrum occidit nonacris arcadiae  uenenata. "], ["occidit", [["occaedes", None], ["occido", None], ["occido", None]], "Tertullianus - De anima (CPL 0017) ", "Legimus quidem pleraque aquarum genera miranda, sed aut ebriosos reddit lyncestarum uena uinosa  aut lymphaticos efficit colophonis scaturigo daemonica aut alexandrum occidit nonacris arcadiae  uenenata. "], ["nonacris", [["Nonacris", None]], "Tertullianus - De anima (CPL 0017) ", "Legimus quidem pleraque aquarum genera miranda, sed aut ebriosos reddit lyncestarum uena uinosa  aut lymphaticos efficit colophonis scaturigo daemonica aut alexandrum occidit nonacris arcadiae  uenenata. "], ["arcadiae", [["Arcadia", None], ["Arcadia", None], ["Arcadius", "Person"]], "Tertullianus - De anima (CPL 0017) ", "Legimus quidem pleraque aquarum genera miranda, sed aut ebriosos reddit lyncestarum uena uinosa  aut lymphaticos efficit colophonis scaturigo daemonica aut alexandrum occidit nonacris arcadiae  uenenata. "], ["uenenata", [["veneno", None], ["venenata", None]], "Tertullianus - De anima (CPL 0017) ", "Legimus quidem pleraque aquarum genera miranda, sed aut ebriosos reddit lyncestarum uena uinosa  aut lymphaticos efficit colophonis scaturigo daemonica aut alexandrum occidit nonacris arcadiae  uenenata. "], ["epistulis", [["epistula", None]], "Cyprianus Carthaginensis - Ad Quirinum (CPL 0039) ", "  In epistulis pauli ad corinthios i: neque fornicarii neque idolis seruientes neque adulteri neque molles  neque masculorum adpetitores neque fures neque fraudulenti neque ebriosi neque maledici neque  raptores regnum dei consequentur. "], ["pauli", [["paulum", None], ["paulus", None]], "Cyprianus Carthaginensis - Ad Quirinum (CPL 0039) ", "  In epistulis pauli ad corinthios i: neque fornicarii neque idolis seruientes neque adulteri neque molles  neque masculorum adpetitores neque fures neque fraudulenti neque ebriosi neque maledici neque  raptores regnum dei consequentur. "], ["corinthios", [["Corinthii", None], ["Corinthius", None]], "Cyprianus Carthaginensis - Ad Quirinum (CPL 0039) ", "  In epistulis pauli ad corinthios i: neque fornicarii neque idolis seruientes neque adulteri neque molles  neque masculorum adpetitores neque fures neque fraudulenti neque ebriosi neque maledici neque  raptores regnum dei consequentur. "], ["fornicarii", [["fornicarius", None]], "Cyprianus Carthaginensis - Ad Quirinum (CPL 0039) ", "  In epistulis pauli ad corinthios i: neque fornicarii neque idolis seruientes neque adulteri neque molles  neque masculorum adpetitores neque fures neque fraudulenti neque ebriosi neque maledici neque  raptores regnum dei consequentur. "], ["idolis", [["idolum", None]], "Cyprianus Carthaginensis - Ad Quirinum (CPL 0039) ", "  In epistulis pauli ad corinthios i: neque fornicarii neque idolis seruientes neque adulteri neque molles  neque masculorum adpetitores neque fures neque fraudulenti neque ebriosi neque maledici neque  raptores regnum dei consequentur. "], ["seruientes", [["servio", None]], "Cyprianus Carthaginensis - Ad Quirinum (CPL 0039) ", "  In epistulis pauli ad corinthios i: neque fornicarii neque idolis seruientes neque adulteri neque molles  neque masculorum adpetitores neque fures neque fraudulenti neque ebriosi neque maledici neque  raptores regnum dei consequentur. "], ["adulteri", [["adulterium", None], ["adulter", None]], "Cyprianus Carthaginensis - Ad Quirinum (CPL 0039) ", "  In epistulis pauli ad corinthios i: neque fornicarii neque idolis seruientes neque adulteri neque molles  neque masculorum adpetitores neque fures neque fraudulenti neque ebriosi neque maledici neque  raptores regnum dei consequentur. "], ["molles", [["molleo", None], ["mollis", None]], "Cyprianus Carthaginensis - Ad Quirinum (CPL 0039) ", "  In epistulis pauli ad corinthios i: neque fornicarii neque idolis seruientes neque adulteri neque molles  neque masculorum adpetitores neque fures neque fraudulenti neque ebriosi neque maledici neque  raptores regnum dei consequentur. "], ["masculorum", [["masculus", None]], "Cyprianus Carthaginensis - Ad Quirinum (CPL 0039) ", "  In epistulis pauli ad corinthios i: neque fornicarii neque idolis seruientes neque adulteri neque molles  neque masculorum adpetitores neque fures neque fraudulenti neque ebriosi neque maledici neque  raptores regnum dei consequentur. "], ["adpetitores", [["appetitor", None]], "Cyprianus Carthaginensis - Ad Quirinum (CPL 0039) ", "  In epistulis pauli ad corinthios i: neque fornicarii neque idolis seruientes neque adulteri neque molles  neque masculorum adpetitores neque fures neque fraudulenti neque ebriosi neque maledici neque  raptores regnum dei consequentur. "], ["fures", [["furo", None], ["fur", None]], "Cyprianus Carthaginensis - Ad Quirinum (CPL 0039) ", "  In epistulis pauli ad corinthios i: neque fornicarii neque idolis seruientes neque adulteri neque molles  neque masculorum adpetitores neque fures neque fraudulenti neque ebriosi neque maledici neque  raptores regnum dei consequentur. "], ["fraudulenti", [["fraudulentus", None]], "Cyprianus Carthaginensis - Ad Quirinum (CPL 0039) ", "  In epistulis pauli ad corinthios i: neque fornicarii neque idolis seruientes neque adulteri neque molles  neque masculorum adpetitores neque fures neque fraudulenti neque ebriosi neque maledici neque  raptores regnum dei consequentur. "], ["ebriosi", [["ebriosus", None]], "Cyprianus Carthaginensis - Ad Quirinum (CPL 0039) ", "  In epistulis pauli ad corinthios i: neque fornicarii neque idolis seruientes neque adulteri neque molles  neque masculorum adpetitores neque fures neque fraudulenti neque ebriosi neque maledici neque  raptores regnum dei consequentur. "], ["maledici", [["maledico", None], ["maledicus", None]], "Cyprianus Carthaginensis - Ad Quirinum (CPL 0039) ", "  In epistulis pauli ad corinthios i: neque fornicarii neque idolis seruientes neque adulteri neque molles  neque masculorum adpetitores neque fures neque fraudulenti neque ebriosi neque maledici neque  raptores regnum dei consequentur. "], ["raptores", [["raptor", None]], "Cyprianus Carthaginensis - Ad Quirinum (CPL 0039) ", "  In epistulis pauli ad corinthios i: neque fornicarii neque idolis seruientes neque adulteri neque molles  neque masculorum adpetitores neque fures neque fraudulenti neque ebriosi neque maledici neque  raptores regnum dei consequentur. "], ["regnum", [["regnum", None]], "Cyprianus Carthaginensis - Ad Quirinum (CPL 0039) ", "  In epistulis pauli ad corinthios i: neque fornicarii neque idolis seruientes neque adulteri neque molles  neque masculorum adpetitores neque fures neque fraudulenti neque ebriosi neque maledici neque  raptores regnum dei consequentur. "], ["dei", [["deeo", None], ["deus", None]], "Cyprianus Carthaginensis - Ad Quirinum (CPL 0039) ", "  In epistulis pauli ad corinthios i: neque fornicarii neque idolis seruientes neque adulteri neque molles  neque masculorum adpetitores neque fures neque fraudulenti neque ebriosi neque maledici neque  raptores regnum dei consequentur. "], ["consequentur", [["consequor", None]], "Cyprianus Carthaginensis - Ad Quirinum (CPL 0039) ", "  In epistulis pauli ad corinthios i: neque fornicarii neque idolis seruientes neque adulteri neque molles  neque masculorum adpetitores neque fures neque fraudulenti neque ebriosi neque maledici neque  raptores regnum dei consequentur. "], ["sanctificatio", [["sanctificatio", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["dei", [["deeo", None], ["deus", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["dignatione", [["dignatio", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["confertur", [["confero", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["apostolus", [["apostolus", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["praedicat", [["praedico", None], ["praedico", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["dicens", [["dico", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["fornicarii", [["fornicarius", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["idolis", [["idolum", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["seruientes", [["servio", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["adulteri", [["adulterium", None], ["adulter", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["molles", [["molleo", None], ["mollis", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["masculorum", [["masculus", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["appetitores", [["appetitor", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["fures", [["furo", None], ["fur", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["fraudulenti", [["fraudulentus", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["ebriosi", [["ebriosus", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["maledici", [["maledico", None], ["maledicus", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["raptores", [["raptor", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["regnum", [["regnum", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["dei", [["deeo", None], ["deus", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["consequentur", [["consequor", None]], "Cyprianus Carthaginensis - De dominica oratione (CPL 0043) ", "  Quae autem sit sanctificatio quae nobis de dei dignatione confertur apostolus praedicat dicens: neque  fornicarii neque idolis seruientes neque adulteri neque molles neque masculorum appetitores neque  fures neque fraudulenti neque ebriosi neque maledici neque raptores regnum dei consequentur. "], ["nolo", [["nolo", None]], "Cyprianus Carthaginensis (pseudo) - De singularitate clericorum (CPL 0062) ", "nolo mihi de martyrio quisquam moueat actionem, quia saepius et moechi et sanguinarii et ebriosi et  omnium scelerum rei reperta pugnationis occasione conuersi meruerunt ad martyrii ueniam  peruenire. "], ["martyrio", [["martyrium", None]], "Cyprianus Carthaginensis (pseudo) - De singularitate clericorum (CPL 0062) ", "nolo mihi de martyrio quisquam moueat actionem, quia saepius et moechi et sanguinarii et ebriosi et  omnium scelerum rei reperta pugnationis occasione conuersi meruerunt ad martyrii ueniam  peruenire. "], ["moueat", [["moveo", None]], "Cyprianus Carthaginensis (pseudo) - De singularitate clericorum (CPL 0062) ", "nolo mihi de martyrio quisquam moueat actionem, quia saepius et moechi et sanguinarii et ebriosi et  omnium scelerum rei reperta pugnationis occasione conuersi meruerunt ad martyrii ueniam  peruenire. "], ["actionem", [["actio", None]], "Cyprianus Carthaginensis (pseudo) - De singularitate clericorum (CPL 0062) ", "nolo mihi de martyrio quisquam moueat actionem, quia saepius et moechi et sanguinarii et ebriosi et  omnium scelerum rei reperta pugnationis occasione conuersi meruerunt ad martyrii ueniam  peruenire. "], ["saepius", [["saepis", None]], "Cyprianus Carthaginensis (pseudo) - De singularitate clericorum (CPL 0062) ", "nolo mihi de martyrio quisquam moueat actionem, quia saepius et moechi et sanguinarii et ebriosi et  omnium scelerum rei reperta pugnationis occasione conuersi meruerunt ad martyrii ueniam  peruenire. "], ["moechi", [["moechus", None]], "Cyprianus Carthaginensis (pseudo) - De singularitate clericorum (CPL 0062) ", "nolo mihi de martyrio quisquam moueat actionem, quia saepius et moechi et sanguinarii et ebriosi et  omnium scelerum rei reperta pugnationis occasione conuersi meruerunt ad martyrii ueniam  peruenire. "]]}

c = Corpus(testData)
c.windowCorpus(4)