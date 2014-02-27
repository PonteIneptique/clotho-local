import json
import codecs
import hashlib
import os

class Cache(object):
	def __init__(self):
		self.folder = "./cache/"

	def hash(self, sentence):
		sentence = hashlib.md5(sentence).hexdigest()
		return sentence

	def filename(self, sentence):
		return self.hash(sentence) + ".json"

	def sentence(self, sentence, data = False):
		filename = self.filename(sentence)
		filename = self.folder + filename
		if data == False:
			if os.path.isfile(filename):
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
