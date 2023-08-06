import jsonpatch
from simplejson import dumps
import collections
from copy import deepcopy


class Doc(collections.Mapping):
	"""This represents a single version controlled doc. The class should be
	initalized with the dict that holds the version controlled document in the
	format specified in `./document.schema.json`. Changing the document must
	be done with the provided `commit()` method. You cannot directly modify
	this object because it is made to act as a "FrozenDict" since
	modifications would cause the current state to get out of sync with the
	history"""
	def __init__(self, *args, **kwargs):
		self.doc = dict(*args, **kwargs)
		if 'history' not in self.doc:
			self.doc['history'] = []
		if 'current' not in self.doc:
			self.doc['current'] = {}

	def __getitem__(self, key):
		return self.doc[key]

	def __iter__(self):
		return iter(self.doc)

	def __len__(self):
		return len(self.doc)

	def __hash__(self):
		return hash(self.doc)

	def __repr__(self):
		"""just output the json representation of the current doc"""
		return dumps(self.doc, separators=(',', ':'))

	def commit(self, new_doc, meta_data={}):
		"""add a revision to the history. the new_doc will replace the current
		doc and a patch will be stored in the history which can be used to
		calculate the previous state of the document"""
		self.doc['history'].append({
			'patch': jsonpatch.make_patch(new_doc, self.doc['current']).patch,
			'meta': meta_data
		})
		self.doc['current'] = new_doc

	def history(self):
		"""return a list of all revisions done to the doc"""
		return self.doc['history']

	def old_doc(self, index):
		"""calculate the state of the document at the given index. if the
		requested revision is too high, it will just return the current
		document"""
		patches = []
		for i in range(len(self.doc['history']), index, -1):
			patches += deepcopy(self.doc['history'][i - 1]['patch'])
		return jsonpatch.apply_patch(self.doc['current'], patches)
