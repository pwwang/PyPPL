import sys
import json
from six import string_types
from box import Box
from six.moves import configparser
from . import utils

class Parameter (object):
	"""
	The class for a single parameter
	"""
	def __init__(self, name, value):
		"""
		Constructor
		@params:
			`name`:  The name of the parameter
			`value`: The initial value of the parameter
		"""
		self.__dict__['props'] = {
			'desc'    : '',
			'required': False,
			'show'    : True,
			'type'    : None,
			'name'    : name,
			'value'   : value if not isinstance(value, string_types) else str(value)
		}
		self.setType(type(self.value))
	
	def __setattr__(self, name, value):
		getattr(self, 'set' + name[0].upper() + name[1:])(value)
	
	def __getattr__(self, name):
		return self.props[name]
	
	def __repr__(self):
		return 'Parameter({})[{}]'.format(','.join([key+'='+str(val) for key, val in self.props.items()]), hex(id(self)))
	
	def __str__(self):
		return str(self.value)
	
	def setDesc (self, d = ''):
		"""
		Set the description of the parameter
		@params:
			`d`: The description
		"""
		self.props['desc'] = d
		return self
		
	def setRequired (self, r = True):
		"""
		Set whether this parameter is required
		@params:
			`r`: True if required else False. Default: True
		"""
		if self.props['type'] == bool:
			raise ValueError('Bool option "{}" cannot be set as required.'.format(self.name))
		self.props['required'] = r
		return self
		
	def setType (self, t = str):
		"""
		Set the type of the parameter
		@params:
			`t`: The type of the value. Default: str
			- Note: str rather then 'str'
		"""
		if t not in [str, int, float, bool, list]:
			raise TypeError ('Unexpected type "{}" for param {}, only support one of the types: [str, int, float, bool, list]'.format(str(t), self.name))
		self.props['type'] = t
		self._forceType()
		return self
	
	def setShow (self, s = True):
		"""
		Set whether this parameter should be shown in help information
		@params:
			`s`: True if it shows else False. Default: True
		"""
		self.props['show'] = s
		return self
		
	def setValue (self, v):
		"""
		Set the value of the parameter
		@params:
			`v`: The value
		"""
		self.props['value'] = v if not isinstance(v, string_types) else str(v)
		return self
	
	def setName (self, n):
		"""
		Set the name of the parameter
		@params:
			`n`: The name
		"""
		self.props['name'] = n
		return self
		
	def _forceType (self):
		"""
		Coerce the value to the type specified
		TypeError will be raised if error happens
		"""
		try:
			if self.type == bool and self.value == 'False':
				self.value = False
			else:
				self.value = self.type(self.value)
		except (ValueError, TypeError):
			sys.stderr.write('Cannot coerce value "{}" to type "{}" for {}'.format(str(self.value), self.type.__name__, repr(self)))
		
	def _printName (self, prefix):
		"""
		Get the print name with type for the parameter
		@params:
			`prefix`: The prefix of the option
		"""
		if self.type == bool:
			return prefix + self.name + ' (bool)'
			
		return prefix + self.name + ' <{}>'.format(self.type.__name__)

class Parameters (object):
	"""
	A set of parameters
	"""
	
	def __init__(self):
		"""
		Constructor
		"""
		self.__dict__['_props']  = {
			'usage': '',
			'example': '',
			'desc': '',
			'hopts': ['-h', '--help', '-H', '-?', ''],
			'prefix': '--param-',
			'params': {}
		}
			
	def __setattr__(self, name, value):
		if name == '_props':
			raise ValueError('A preserved parameter name used: _props.')
		
		if name in self._props['params']:
			self._props['params'][name].setValue(value)
		self._props['params'][name] = Parameter(name, value)
		
	def __getattr__(self, name):
		if not name in self._props['params']:
			self._props['params'][name] = Parameter(name, '')
		return self._props['params'][name]
		
	def prefix (self, p):
		"""
		Set the prefix of options
		@params:
			`p`: The prefix. No default, but typically '--param-'
		"""
		if not p.startswith('-'):
			raise ValueError('Expecting a prefix starting with "-"')
		self._props['prefix'] = p
		return self
	
	def helpOpts (self, h):
		"""
		The options to popup help information
		An empty string '' implys help information pops up when no arguments specified
		@params:
			`h`: The options. It could be either list or comma separated.
		"""
		if not isinstance(h, list):
			h = list(map(lambda x: x.strip(), h.split(',')))
		self._props['hopts'] = h
		return self
	
	def usage(self, u):
		"""
		Set the usage of the program. Otherwise it'll be automatically calculated.
		@params
			`u`: The usage, no program name needed. Multiple usages in multiple lines.
		"""
		self._props['usage'] = list(filter(None, list(map(lambda x: x.strip(), u.splitlines()))))
		return self
		
	def example(self, e):
		"""
		Set the examples of the program
		@params:
			`e`: The examples. Multiple examples in multiple lines
		"""
		self._props['example'] = list(filter(None, list(map(lambda x: x.strip(), e.splitlines()))))
		return self
		
	def desc(self, d):
		"""
		Set the description of the program
		@params:
			`d`: The description
		"""
		self._props['desc'] = list(filter(None, list(map(lambda x: x.strip(), d.splitlines()))))
		return self
	
	def parse (self):
		"""
		Parse the arguments from `sys.argv`
		"""
		args = sys.argv[1:]
		if (not args and '' in self._props['hopts']) or (set(filter(None, self._props['hopts'])) & set(args)):
			sys.stderr.write (self.help())
			sys.exit (1)
		else:
			i = 0
			listKeysFirstHit = {}
			while i < len(args):
				# support '--param-a=b'
				arg  = args[i].split('=')
				karg = arg.pop(0)
				if karg.startswith(self._props['prefix']):
					key = karg[len(self._props['prefix']):]
					if key not in self._props['params']:
						sys.stderr.write ('WARNING: Unkown option {}.\n'.format(karg))
					val = self._props['params'][key]
					
					if val.type == bool:
						if arg or (i+1 < len(args) and not args[i+1].startswith(self._props['prefix'])):
							val.value = arg[0] if arg else args[i+1]
							i += (1 if arg else 2)
						else:
							val.value = True
							i += (1 if not arg else 2)
					elif val.type == list:
						if key not in listKeysFirstHit:
							listKeysFirstHit[key] = True
							val.value = []
							
						if arg:
							val.value += arg
						j = i + 1
						while j < len(args) and not args[j].startswith(self._props['prefix']):
							val.value.append (args[j])
							j += 1
						i = j 
					else:
						if arg:
							val.value = arg[0]
							i += 1
						else:
							if i+1 >= len(args) or args[i+1].startswith(self._props['prefix']):
								raise ValueError('No value assigned for option: {}'.format(karg))
							val.value = args[i+1]
							i += 2				
						
				else:
					sys.stderr.write ('WARNING: Unused value found: {}.\n'.format(args[i]))
					i += 1
					
			for key, val in self._props['params'].items():
				if val.required and not val.value:
					sys.stderr.write ('ERROR: Option {}{} is required.\n\n'.format(self._props['prefix'], key))
					sys.stderr.write (self.help())
					sys.exit(1)
				if val.type == bool:
					if isinstance(val.value, bool):
						pass
					elif val.value.lower() in ['t', 'true', 'yes', 'y', '1', 'on', '']:
						val.value = True
					elif val.value.lower() in ['f', 'false', 'no', 'n', '0', 'off']:
						val.value = False
					else:
						raise ValueError('Cannot coerce "{}" to bool for option: {}, expect T[rue]/F[alse], Y[es]/N[o], 1/0 or on/off.'.format(val.value, val.name))
				try:
					val._forceType()
				except TypeError:
					sys.stderr.write('ERROR: Cannot coerce "{}" to {} for option: {}' % (val.value, val.type, karg))
		return self				
		
	def help (self):
		"""
		Calculate the help page
		@return:
			The help information
		"""
		ret = ''
		
		requiredOptions = {}
		optionalOptions = {}
		
		keylen = 40 # '--param-xxx'
		
		for key, val in self._props['params'].items():
			if not val.show:
				continue
			if val.required:
				requiredOptions[key] = val
			else:
				optionalOptions[key] = val
			keylen = max(len(self._props['prefix']) + 4 + len(key), keylen)
			
		keylen = max (4 + len(', '.join(filter(None, self._props['hopts']))), keylen)
			
		if self._props['desc']:
			ret += 'DESCRIPTION:\n'
			ret += '\n'.join('  ' + d for d in self._props['desc']) + '\n\n'
		ret += 'USAGE:\n'
		if self._props['usage']:
			ret += '  ' + '\n	{}'.format(sys.argv[0]).join(list(self._props['usage'])) + '\n\n'
		else:
			ret += '  ' + sys.argv[0]  \
				+ ('' if not requiredOptions else ' ' + ' '.join([val._printName(self._props['prefix']) for key, val in requiredOptions.items()])) \
				+ ('' if not optionalOptions else ' [OPTIONS]') + '\n\n'
		if self._props['example']:
			ret += 'EXAMPLE:\n'
			ret += '\n'.join('  ' + d for d in self._props['example']) + '\n\n'

		if requiredOptions:
			ret += 'REQUIRED OPTIONS:\n'
			for key, val in requiredOptions.items():
				descs = val.desc.split("\n")
				ret  += '  {}'.format(val._printName(self._props['prefix'])).ljust(keylen) + (descs.pop(0) if descs else '') + '\n'
				for desc in descs:
					ret += ''.ljust(keylen) + desc + '\n'
			ret += '\n'
		
		ret += 'OPTIONAL OPTIONS:\n'
		if optionalOptions:
			for key, val in optionalOptions.items():
				descs = (val.desc + ' ' if val.desc else '') + 'Default: ' + str(val)
				descs = descs.split("\n")
				ret  += '  {}'.format(val._printName(self._props['prefix'])).ljust(keylen) \
					 + (descs.pop(0) if descs else '') + '\n'
				for desc in descs:
					ret += ''.ljust(keylen) + desc + '\n'
		ret += '  ' + ', '.join(filter(None, self._props['hopts'])).ljust(keylen - 2) + 'Print this help information.\n\n'

		return ret
	
	def loadDict (self, dictVar, show = False):
		"""
		Load parameters from a dict
		@params:
			`dictVar`: The dict variable.
			- Properties are set by "<param>.required", "<param>.show", ...
			`show`:    Whether these parameters should be shown in help information
				- Default: False (don't show parameter from config object in help page)
				- It'll be overwritten by the `show` property inside dict variable.
				- If it is None, will inherit the param's show value
		"""
		for key, val in dictVar.items():
			if '.' in key: continue
			self._props['params'][key] = Parameter(key, val)
			if show is not None:
				self._props['params'][key].show = show
		for key, val in dictVar.items():
			if '.' not in key: continue
			(k, _, prop) = key.rpartition('.')
			if not k in self._props['params']:
				raise ValueError('Propterty set for undefined option: {}'.format(key))
			if not prop in ['desc', 'required', 'show', 'type']:
				raise ValueError('Unknown property "{}" for option: {}'.format(prop, k))
			
			setattr (self._props['params'][k], prop, val)	
		return self
		
	def loadFile (self, cfgfile, show = False):
		"""
		Load parameters from a json/config file
		If the file name ends with '.json', `json.load` will be used,
		otherwise, `ConfigParser` will be used.
		For config file other than json, a section name is needed, whatever it is.
		@params:
			`cfgfile`: The config file
			`show`:    Whether these parameters should be shown in help information
				- Default: False (don't show parameter from config file in help page)
				- It'll be overwritten by the `show` property inside the config file.
		"""
		config = {} 
		if cfgfile.endswith('.json'):
			with open(cfgfile) as f:
				config = json.load (f)
		else:
			cp = configparser.ConfigParser()
			cp.optionxform = str
			cp.read(cfgfile)
			config = dict(cp.items(cp.sections()[0]))
		for key, val in config.items():
			if key.endswith(".type"):
				config[key] = eval(val)
				if config[key] == list and key[:-5] in config and not isinstance(config[key[:-5]], list):
					config[key[:-5]] = list(filter(None, config[key[:-5]].splitlines()))
		self.loadDict(config, show = show)
		return self
	
	def toDict (self):
		"""
		Convert the parameters to Box object
		@returns:
			The Box object
		"""
		ret = Box()
		for name in self._props['params']:
			ret[name] = self._props['params'][name].value
		return ret

params = Parameters()