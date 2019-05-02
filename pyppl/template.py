"""
Template adaptor for PyPPL
"""
from __future__ import unicode_literals

import json, inspect
from os import path, readlink
from liquid import Liquid
from .utils import string_types
Liquid.MODE  = 'mixed'
Liquid.DEBUG = False

__all__ = ['Template', 'TemplateLiquid', 'TemplateJinja2']

class _TemplateFilter(object):
	"""
	A set of builtin filters
	"""

	@staticmethod
	def read(var):
		with open(var) as fvar:
			return fvar.read()

	@staticmethod
	def readlines(var, skip_empty_lines = True):
		ret = []
		with open(var) as fvar:
			for line in fvar:
				line = line.rstrip('\n\r')
				if not line and skip_empty_lines:
					continue
				ret.append(line)
		return ret

	@staticmethod
	def basename(var, orig = False):
		bname = path.basename(var)
		if orig or not bname.startswith('['): 
			return bname

		return bname[bname.find(']')+1:]

	@staticmethod
	def filename(var, orig = False, dot = -1):
		"""
		Return the stem of the basename (stripping extension(s))
		@params:
			`var`: The path
			`orig`: If the path is a renamed file (like: `origin[1].txt`), 
				- whether return its original filename or the parsed filename (`origin.txt`)
			`dot`: Strip to which dot. 
				- `-1`: the last one
				- `-2`: the 2nd last one ...
				- `1` : remove all dots.
		"""
		bname = _TemplateFilter.basename(var, orig)
		if '.' not in bname:
			return bname
		return '.'.join(bname.split('.')[0:dot])
	
	@staticmethod
	def prefix(var, orig = False, dot = -1):
		return path.join(path.dirname(var), _TemplateFilter.filename(var, orig, dot))

	@staticmethod
	def R(var, ignoreintkey = True): # pylint: disable=invalid-name
		if var is True:
			return 'TRUE'
		if var is False:
			return 'FALSE'
		if var is None:
			return 'NULL'
		if isinstance(var, string_types):
			if var.upper() in ['+INF', 'INF']:
				return 'Inf'
			if var.upper() == '-INF':
				return '-Inf'
			if var.upper() == 'TRUE':
				return 'TRUE'
			if var.upper() == 'FALSE':
				return 'FALSE'
			if var.upper() == 'NA' or var.upper() == 'NULL':
				return var
			if var.startswith('r:') or var.startswith('R:'):
				return str(var)[2:]
			return repr(str(var))
		if isinstance(var, (list, tuple, set)):
			return 'c({})'.format(','.join([_TemplateFilter.R(i) for i in var]))
		if isinstance(var, dict):
			# list allow repeated names
			return 'list({})'.format(','.join([
				'`{0}`={1}'.format(
					k, 
					_TemplateFilter.R(v)) if isinstance(k, int) and not ignoreintkey else \
					_TemplateFilter.R(v) if isinstance(k, int) and ignoreintkey else \
					'`{0}`={1}'.format(str(k).split('#')[0], _TemplateFilter.R(v)) 
				for k, v in sorted(var.items())]))
		return repr(var)

	@staticmethod
	def Rlist(var, ignoreintkey = True): # pylint: disable=invalid-name
		assert isinstance(var, (list, tuple, set, dict))
		if isinstance(var, dict):
			return _TemplateFilter.R(var, ignoreintkey)
		return 'as.list({})'.format(_TemplateFilter.R(var, ignoreintkey))
	
	@staticmethod
	def render(var, data = None):
		"""
		Render a template variable, using the shared environment
		"""
		if not isinstance(var, string_types):
			return var
		frames = inspect.getouterframes(inspect.currentframe())
		evars  = data or {}
		for frame in frames:
			lvars = frame[0].f_locals
			if lvars.get('__engine') == 'liquid':
				lvars.update(evars)
				evars = lvars
				break
			if '_Context__self' in lvars:
				lvars = dict(lvars['_Context__self'])
				lvars.update(evars)
				evars = lvars
				break
		
		engine = evars.get('__engine')
		if not engine:
			raise RuntimeError(
				"I don't know which template engine to use to render {}...".format(var[:10]))
		
		engine = TemplateJinja2 if engine == 'jinja2' else TemplateLiquid
		return engine(var).render(evars)

class Template(object):
	"""
	Template wrapper base
	"""

	DEFAULT_ENVS = {
		'R'        : _TemplateFilter.R,
		'Rvec'     : _TemplateFilter.R, # will be deprecated!
		'Rlist'    : _TemplateFilter.Rlist,
		'realpath' : path.realpath,
		'readlink' : readlink,
		'dirname'  : path.dirname,
		# /a/b/c[1].txt => c.txt
		'basename' : _TemplateFilter.basename,
		'bn'       : _TemplateFilter.basename,
		'stem'     : _TemplateFilter.filename,
		'filename' : _TemplateFilter.filename,
		'fn'       : _TemplateFilter.filename,
		# /a/b/c.d.e.txt => c
		'filename2': lambda var, orig = False, dot = 1: _TemplateFilter.filename(var, orig, dot),
		'fn2'      : lambda var, orig = False, dot = 1: _TemplateFilter.filename(var, orig, dot),
		# /a/b/c.txt => .txt
		'ext'      : lambda var: path.splitext(var)[1],
		# /a/b/c[1].txt => /a/b/c
		'prefix'   : _TemplateFilter.prefix,
		# /a/b/c.d.e.txt => /a/b/c
		'prefix2'  : lambda var, orig = False, dot = 1: _TemplateFilter.prefix(var, orig, dot),
		'quote'    : lambda var: json.dumps(str(var)),
		'squote'   : repr,
		'json'     : json.dumps,
		'read'     : _TemplateFilter.read,
		'readlines': _TemplateFilter.readlines,
		'render'   : _TemplateFilter.render,
		# single quote of all elements of an array
		'asquote'  : lambda var: '''%s''' % (" " .join([json.dumps(str(e)) for e in var])),
		# double quote of all elements of an array
		'acquote'  : lambda var: """%s""" % (", ".join([json.dumps(str(e)) for e in var]))
	}

	def __init__(self, source, **envs):
		self.source = source
		self.envs   = Template.DEFAULT_ENVS.copy()
		self.envs.update(envs)

	def registerEnvs(self, **envs):
		"""
		Register extra environment
		@params:
			`**envs`: The environment
		"""
		self.envs.update(envs)

	def render(self, data = None):
		"""
		Render the template
		@parmas:
			`data`: The data used to render
		"""
		return self._render(data or {})

	# in order to dump setting
	def __str__(self):
		lines = self.source.splitlines()
		if len(lines) <= 1:
			return '%s < %s >' % (self.__class__.__name__, ''.join(lines))

		ret  = ['%s <<<' % self.__class__.__name__]
		ret += ['\t' + line for line in self.source.splitlines()]
		ret += ['>>>']
		return '\n'.join(ret)

	def __repr__(self):
		return str(self)

	def _render(self, data):
		raise NotImplementedError()

class TemplateLiquid (Template):
	"""
	liquidpy template wrapper.
	"""

	def __init__(self, source, **envs):
		"""
		Initiate the engine with source and envs
		@params:
			`source`: The souce text
			`envs`: The env data
		"""
		super(TemplateLiquid, self).__init__(source ,**envs)
		self.envs['__engine'] = 'liquid'
		self.engine = Liquid(source, **self.envs)
		self.source = source

	def _render(self, data):
		"""
		Render the template
		@params:
			`data`: The data used for rendering
		@returns:
			The rendered string
		"""
		return self.engine.render(**data)

class TemplateJinja2 (Template):
	"""
	Jinja2 template wrapper
	"""

	def __init__(self, source, **envs):
		"""
		Initiate the engine with source and envs
		@params:
			`source`: The souce text
			`envs`: The env data
		"""
		import jinja2
		super(TemplateJinja2, self).__init__(source ,**envs)
		self.envs['__engine'] = 'jinja2'
		self.engine = jinja2.Template(source)
		self.engine.globals = self.envs
		self.source = source

	def _render(self, data):
		"""
		Render the template
		@params:
			`data`: The data used for rendering
		@returns:
			The rendered string
		"""
		return self.engine.render(data)
