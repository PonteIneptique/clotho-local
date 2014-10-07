CONSTANT_DATA_STORAGE = "MySQL"
import sys, os
import xml

sys.path.append("../..")

from Data import Models
from Linguistic.Lemma.form import Lemmatizer
from Services.Perseus.Common import Chunk
from Linguistic.Contextualiser.common import Dots as DotsList
from Data import Tools


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