CONSTANT_DATA_STORAGE = "MySQL"
import sys, os
import xml
import subprocess

sys.path.append("../..")

from Data import Models
from Data.Tools import Github
from Linguistic.Lemma.form import Lemmatizer
from Services.Perseus.Common import Chunk
from Linguistic.Contextualiser.common import Dots as DotsList
from Data import Tools
import External.BaseXClient as BaseXClient

class Config(object):
	def __init__(self):
		self.Session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')
		self.DBName = "perseus-canonical-TEI"
		self.path = "/texts/perseus-canonical"
		self.tei = "/CTS_XML_TEI"
		self.perseids = "/CTS_XML_EpiDoc"
		self.metadata = "/CTS_XML_TextInventory"

		self.github = Github("PerseusDL", "canonical", "/texts/perseus-canonical")


	def _checkDB(self):
		try:
			self.Session.execute("OPEN {0}".format(self.DBName))
			return True
		except Exception as E:
			print E
			return False
		return False

	def _checkRepo(self):
		return self.github.check()

	def check(self):
		if not self._checkDB() or self._checkRepo():
			return False

	def _installRepo(self):
		self.github.install()

	def _installDB(self, force = False):
		if force and self._checkDB():
			self.Session.execute("DROP DB {0}".format(self.DBName))

		try:
			self.Session.execute("SET INTPARSE false")
			self.Session.execute("CREATE DB {0} {1}".format(self.DBName, self.folder(self.path + self.tei)))
			return True
		except Exception as E:
			print E
			return False
		return False

	def install(self):
		if not self._checkRepo():
			self.github.install()
			self._installDB(True)
			return True
		else:
			self._installDB()
		return True

		

	def folder(self, path, filename = None):
		__dir__ = os.path.dirname(os.path.abspath(__file__))
		if filename:
			path = os.path.join(__dir__, "../..{0}/{1}".format(path, filename))
		else:
			path = os.path.join(__dir__, "../..{0}".format(path))
		return path

class Occurence(object):
	def __init__(self):
		pass

	def search(self, lemma):
		if not(isinstance(lemma, Models.lang.Lemma)):
			raise TypeError("Lemma is not an instance of Models.lang.Lemma")

		#Results array to get

		chunks = []
		for result in results:
			chunks.append(
				Models.documents.Occurence(
					#uid = c["id"], 
					#document = Models.documents.Text(uid = c["document_id"]), 
					lemma = lemma,
					chunk = Chunk(
						uid = c["id"], 
						document = Models.documents.Text(uid = c["document_id"]),
						section = Models.documents.Section(
							section = c["type"], 
							identifier = c["value"], 
							position = c["position"], 
							absolute_position = c["abs_position"]
						), 
						xml = Models.documents.XmlChunk(
							opening = c["open_tags"], 
							closing = c["close_tags"]
						),
						offset = Models.documents.Offset(
							start = c["start_offset"],
							end = c["end_offset"]
						)
					)
				)
			)
		return chunks