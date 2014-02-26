try:
	import lucene
	#Java imports
	from java.io import File
	from org.apache.lucene.store import MMapDirectory
	from org.apache.lucene.analysis.standard import StandardAnalyzer
	from org.apache.lucene.search import IndexSearcher
	from org.apache.lucene.util import Version
	from org.apache.lucene.queryparser.classic import QueryParser
	from org.apache.lucene.index import DirectoryReader

	luceneImport = True
except:
	luceneImport = False

class PyLucene(object):
	def __init__(self):
		if luceneImport:
			self.lucene = True
		else:
			self.lucene = False

		#Lucene connection
		lucene.initVM()
		indexDir = "texts/index"
		directory = MMapDirectory(File(indexDir))
		directory = DirectoryReader.open(directory)
		self.analyzer = StandardAnalyzer(Version.LUCENE_30)
		self.searcher = IndexSearcher(directory)

	def query(self, terms = []):
		query = QueryParser(Version.LUCENE_30, "text", self.analyzer).parse(" OR ".join(terms))
		MAX = 1000
		hits = self.searcher.search(query, MAX)

		results = []
		for hit in hits.scoreDocs:
			doc = self.searcher.doc(hit.doc)
			results.append([doc.get("doc_id").encode("utf-8"), doc.get("head").encode("utf-8")])

		return results

	def occurencies(self, term, morphs):
		query = []
		print morphs
		for morph in morphs:
			query.append(morph)
			#Sometime, when there is doubt about a term, because of xml hashing in Lucene, you would find twice a lemma like wordword
			query.append(morph+morph)

		results = self.query(query)
		print query
		return results, len(results)

	def chunk(self, occurency):
		#Could be updated using the section information but could be only milesone

		return occurency#, len(occurency)