class Lemma(object):
	def __init__(self, uid = None, text = None, definition = None):
		if isinstance(uid, basestring):
			self.uid = uid
		if isinstance(text, basestring):
			self.text = text
		if isinstance(definition, basestring):
			self.definition = definition