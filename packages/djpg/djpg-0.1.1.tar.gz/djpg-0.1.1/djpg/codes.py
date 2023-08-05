class CodesDict(object):
	def __init__(self, codes={}):
		super(CodesDict, self).__setattr__('_codes', codes)

	def __setattr__(self, name, value):
		self._codes[name] = value

	def __getattr__(self, name):
		return self._codes[name]

_codes = {
	'waiting': 1,
	'analysis': 2,
	'paid': 3,
	'available': 4,
	'dispute': 5,
	'returned': 6,
	'canceled': 7,
}

codes = CodesDict(_codes)
