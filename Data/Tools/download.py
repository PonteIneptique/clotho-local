#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import wget
import subprocess

class File(object):
	def __init__(self, url, path, filename, mime = None):
		self.__dir__ = os.path.dirname(os.path.abspath(__file__))
		self.path = os.path.join(self.__dir__, "../..{0}/{1}".format(path, filename))
		self.filename = filename
		self.url = url
		self.mime = mime

	def download(self):
		try:
			filename = wget.download(self.url)
			os.rename(os.path.join(self.__dir__, filename), self.path)
			return True
		except:
			return False

	def check(self, force = False):
		if os.path.isfile(self.path) == False:
			if force == True:
				return self.download()
			else:
				return False
		return True

class Github(object):
	def __init__(self, user, repository, path):
		self.__dir__ = os.path.dirname(os.path.abspath(__file__))
		self.path = os.path.join(self.__dir__, "../..{0}".format(path))
		self.repository = repository
		self.user = user

	def url(self):
		return "https://github.com/{0}/{1}.git".format(self.user, self.repository)

	def check(self):
		return os.path.isdir(self.path)

	def clone(self):
		return subprocess.call(['git', 'clone', self.url(), self.path])
