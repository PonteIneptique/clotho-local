import json
import codecs
import hashlib
import os

class Cache(object):
	def __init__(self):
		self.folder = {
			"sentence" : "./cache/sentence/",
			"search" : "./cache/search/"
		}

	def hash(self, sentence, mode = "sentence"):
		if mode == "search":
			sentence = " ".join([term.encode("UTF-8") for term in sentence["terms"]]) + " " + sentence["name"] + " " + sentence["mode"]

		sentence = hashlib.md5(sentence).hexdigest()
		return sentence

	def filename(self, sentence, mode = "sentence"):
		return self.hash(sentence, mode = mode) + ".json"

	def sentence(self, sentence, data = False, check = False):

		filename = self.filename(sentence, mode = "sentence")
		filename = self.folder["sentence"] + filename

		if data == False:
			if os.path.isfile(filename):
				if check == True:
					return True
				else:
					with codecs.open(filename, "r") as f:
						d = json.load(f)
						f.close()
						return d
			return False
		else:
			with codecs.open(filename, "w") as f:
				d = f.write(json.dumps(data))
				f.close()
			return True

	def search(self, sentence, data = False, check = False):
		
		filename = self.filename(sentence, mode = "search")
		filename = self.folder["search"] + filename

		if data == False:
			if os.path.isfile(filename):
				if check == True:
					return True
				else:
					with codecs.open(filename, "r") as f:
						d = json.load(f)
						f.close()
						return d
			return False
		else:
			with codecs.open(filename, "w") as f:
				d = f.write(json.dumps(data))
				f.close()
			return True
