'''
File: split.py
Author: Jon Eisen
Description: Provide helpers for splitter.py
'''

class SqlSplit:
	def __init__(self, sqltype, connargs, query):
		self.sqltype = sqltype
		self.connargs = connargs
		self.query = query

	def __str__(self):
		return self.uri()

	def uri(self):
		'''Format as json to be passed as the uri parameter'''
		import json
		return json.dumps({
			'dummy': 'notatag://',
			'sqltype': self.sqltype,
			'connargs': self.connargs,
			'query': self.query,
		})

