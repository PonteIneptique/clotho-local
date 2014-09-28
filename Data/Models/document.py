class Document(object):
	def __init__(self, uid = None, metadata = None):
		if isinstance(uid, basestring):
			self.uid = uid
		if isinstance(metadata, dict):
			self.metadata = metadata

	def property(self, key = None, value = None, metadata = None):
		if isinstance(metadata, dict):
			for key in metadata:
				self.metadata[key] = metadata[key]
		if key and isinstance(key, basestring) and value:
			self.metadata[key] = value

