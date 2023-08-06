def build (**args):
	prop = {}
	for arg in args:
		prop[arg] = args[arg]
	
	obj = type('pyobj', (object,), prop)
	
	return obj
