class ModuleDoesNotExist(KeyError):
	pass

_modules = {}

def register(name, module):
	_modules[name] = module

def get(name):
	try:
		return _modules[name]
	except KeyError:
		raise ModuleDoesNotExist()

def get_all():
	return _modules

