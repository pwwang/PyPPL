"""
Custome logger for PyPPL
"""
import re
import sys
import logging
import threading
from collections import OrderedDict
from copy import copy
from functools import partial

import colorama
# Fore/Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL
from .utils import config

colorama.init(autoreset = False)

LOGFMT     = "[%(asctime)s%(message)s"
LOGTIMEFMT = "%Y-%m-%d %H:%M:%S"

THEMES = dict(
	greenOnBlack = OrderedDict([
		('DONE', '{s.BRIGHT}{f.GREEN}'),
		('DEBUG', '{s.DIM}{f.WHITE}'),
		('PROCESS', '{s.BRIGHT}{f.CYAN}'),
		('DEPENDS', '{f.MAGENTA}'),
		('in:INFO,P_PROPS,OUTPUT,EXPORT,INPUT,P_ARGS,BLDING,SUBMIT,RUNNING,JOBDONE,KILLING',
		 '{f.GREEN}'),
		('CMDERR', '{s.BRIGHT}{f.YELLOW}'),
		('has:ERR', '{f.RED}'),
		('in:WARNING,RETRY,RESUMED,SKIPPED', '{s.BRIGHT}{f.YELLOW}'),
		('in:WORKDIR,CACHED,P_DONE', '{f.YELLOW}'),
		('', ''),
	]),

	blueOnBlack = OrderedDict([
		('DONE', '{s.BRIGHT}{f.BLUE}'),
		('DEBUG', '{s.DIM}{f.WHITE}'),
		('PROCESS', '{s.BRIGHT}{f.CYAN}'),
		('DEPENDS', '{f.GREEN}'),
		('in:INFO,P_PROPS,OUTPUT,EXPORT,INPUT,P_ARGS,BLDING,SUBMIT,RUNNING,JOBDONE,KILLING',
		 '{f.BLUE}'),
		('CMDERR', '{s.BRIGHT}{f.YELLOW}'),
		('has:ERR', '{f.RED}'),
		('in:WARNING,RETRY,RESUMED,SKIPPED', '{s.BRIGHT}{f.YELLOW}'),
		('in:WORKDIR,CACHED,P_DONE', '{f.YELLOW}'),
		('', ''),
	]),

	magentaOnBlack = OrderedDict([
		('DONE', '{s.BRIGHT}{f.MAGENTA}'),
		('DEBUG', '{s.DIM}{f.WHITE}'),
		('PROCESS', '{s.BRIGHT}{f.GREEN}'),
		('DEPENDS', '{f.BLUE}'),
		('in:INFO,P_PROPS,OUTPUT,EXPORT,INPUT,P_ARGS,BLDING,SUBMIT,RUNNING,JOBDONE,KILLING',
		 '{f.MAGENTA}'),
		('CMDERR', '{s.BRIGHT}{f.YELLOW}'),
		('has:ERR', '{f.RED}'),
		('in:WARNING,RETRY,RESUMED,SKIPPED', '{s.BRIGHT}{f.YELLOW}'),
		('in:WORKDIR,CACHED,P_DONE', '{f.YELLOW}'),
		('', ''),
	]),

	greenOnWhite = OrderedDict([
		('DONE', '{s.BRIGHT}{f.GREEN}'),
		('DEBUG', '{s.DIM}{f.BLACK}'),
		('PROCESS', '{s.BRIGHT}{f.BLUE}'),
		('DEPENDS', '{f.MAGENTA}'),
		('in:INFO,P_PROPS,OUTPUT,EXPORT,INPUT,P_ARGS,BLDING,SUBMIT,RUNNING,JOBDONE,KILLING',
		 '{f.GREEN}'),
		('CMDERR', '{s.BRIGHT}{f.YELLOW}'),
		('has:ERR', '{f.RED}'),
		('in:WARNING,RETRY,RESUMED,SKIPPED', '{s.BRIGHT}{f.YELLOW}'),
		('in:WORKDIR,CACHED,P_DONE', '{f.YELLOW}'),
		('', ''),
	]),

	blueOnWhite = OrderedDict([
		('DONE', '{s.BRIGHT}{f.BLUE}'),
		('DEBUG', '{s.DIM}{f.BLACK}'),
		('PROCESS', '{s.BRIGHT}{f.GREEN}'),
		('DEPENDS', '{f.MAGENTA}'),
		('in:INFO,P_PROPS,OUTPUT,EXPORT,INPUT,P_ARGS,BLDING,SUBMIT,RUNNING,JOBDONE,KILLING',
		 '{f.BLUE}'),
		('CMDERR', '{s.BRIGHT}{f.YELLOW}'),
		('has:ERR', '{f.RED}'),
		('in:WARNING,RETRY,RESUMED,SKIPPED', '{s.BRIGHT}{f.YELLOW}'),
		('in:WORKDIR,CACHED,P_DONE', '{f.YELLOW}'),
		('', ''),
	]),

	magentaOnWhite = OrderedDict([
		('DONE', '{s.BRIGHT}{f.MAGENTA}'),
		('DEBUG', '{s.DIM}{f.BLACK}'),
		('PROCESS', '{s.BRIGHT}{f.BLUE}'),
		('DEPENDS', '{f.GREEN}'),
		('in:INFO,P_PROPS,OUTPUT,EXPORT,INPUT,P_ARGS,BLDING,SUBMIT,RUNNING,JOBDONE,KILLING',
		 '{f.MAGENTA}'),
		('CMDERR', '{s.BRIGHT}{f.YELLOW}'),
		('has:ERR', '{f.RED}'),
		('in:WARNING,RETRY,RESUMED,SKIPPED', '{s.BRIGHT}{f.YELLOW}'),
		('in:WORKDIR,CACHED,P_DONE', '{f.YELLOW}'),
		('', ''),
	]),
)

LEVELS = {
	'all'   : set(['INPUT', 'OUTPUT', 'P_ARGS', 'P_PROPS', 'DEBUG', 'WARNING']),
	'basic' : set(),
	'normal': set(['INPUT', 'OUTPUT', 'P_ARGS', 'P_PROPS', 'WARNING'])
}

LEVELS_ALWAYS = set([
	'PROCESS', 'WORKDIR', 'RESUMED', 'SKIPPED', 'DEPENDS', 'STDOUT', 'STDERR', 'ERROR',
	'INFO', 'DONE', 'EXPORT', 'PYPPL', 'TIPS', 'CONFIG', 'CMDOUT', 'CMDERR', 'BLDING',
	'SUBMIT', 'RUNNING', 'RETRY', 'JOBDONE', 'KILLING', 'P_DONE', 'CACHED'
])

DEBUG_LINES = {
	'EXPORT_CACHE_OUTFILE_EXISTS'  : -1,
	'EXPORT_CACHE_USING_SYMLINK'   : 1,
	'EXPORT_CACHE_USING_EXPARTIAL' : 1,
	'EXPORT_CACHE_EXFILE_NOTEXISTS': 1,
	'EXPORT_CACHE_EXDIR_NOTSET'    : 1,
	'CACHE_EMPTY_PREVSIG'          : -1,
	'CACHE_EMPTY_CURRSIG'          : -2,
	'CACHE_SCRIPT_NEWER'           : -1,
	'CACHE_SIGINVAR_DIFF'          : -1,
	'CACHE_SIGINFILE_DIFF'         : -1,
	'CACHE_SIGINFILE_NEWER'        : -1,
	'CACHE_SIGINFILES_DIFF'        : -1,
	'CACHE_SIGINFILES_NEWER'       : -1,
	'CACHE_SIGOUTVAR_DIFF'         : -1,
	'CACHE_SIGOUTFILE_DIFF'        : -1,
	'CACHE_SIGOUTDIR_DIFF'         : -1,
	'CACHE_SIGFILE_NOTEXISTS'      : -1,
	'EXPECT_CHECKING'              : -1,
	'INFILE_RENAMING'              : -1,
	'INFILE_EMPTY'                 : -1,
	'SUBMISSION_FAIL'              : -3,
	'OUTFILE_NOT_EXISTS'           : -1,
	'OUTDIR_CREATED_AFTER_RESET'   : -1,
	'SCRIPT_EXISTS'                : -2,
	'JOB_RESETTING'                : -1
}

class Theme(object):
	"""
	The theme for the logger
	"""
	def __init__(self, theme = 'greenOnBlack'):
		if theme is True:
			theme = 'greenOnBlack'
		if not theme:
			self.theme = {}
		elif isinstance(theme, dict):
			self.theme = theme
		elif theme in THEMES:
			self.theme = THEMES[theme]
		else:
			raise ValueError('No such theme: %s' % theme)

		self.colors = dict(
			Style = colorama.Style, s = colorama.Style,
			Back  = colorama.Back,  b = colorama.Back,
			Fore  = colorama.Fore,  f = colorama.Fore,
		)

	def getColor(self, level):
		"""
		Get the color for a given level
		@params:
			`level`: The level
		@returns:
			The color of the level by the theme.
		"""
		level = level.upper()
		for key, val in self.theme.items():
			if key == level:
				return val.format(**self.colors)
			if key.startswith('in:') and level in key[3:].split(','):
				return val.format(**self.colors)
			if key.startswith('starts:') and level.startswith(key[7:]):
				return val.format(**self.colors)
			if key.startswith('has:') and key[4:] in level:
				return val.format(**self.colors)
			if key.startswith('re:') and re.search(key[3:], level):
				return val.format(**self.colors)
		return ''

class StreamFormatter(logging.Formatter):
	"""
	Logging formatter for stream (sys.stderr)
	"""
	def __init__(self, theme):
		logging.Formatter.__init__(self, LOGFMT, LOGTIMEFMT)
		self.theme = theme

	def format(self, record):
		if hasattr(record, 'formatted') and record.formatted:
			return record.formatted

		# save the formatted, for all handlers
		level = record.mylevel
		if '\n' in record.msg:
			record.tails = []
			msgs = record.msg.splitlines()
			record.msg = msgs[0]
			for msg in msgs[1:]:
				rec     = copy(record)
				rec.msg = msg
				self.format(rec)
				record.tails.append(rec)

		record.msg = ' {COLOR}{LEVEL}{RESET_ALL}] {COLOR}{PROC}{JOBS}{MSG}{RESET_ALL}'.format(
			COLOR     = self.theme.getColor(level),
			LEVEL     = level.rjust(7),
			RESET_ALL = colorama.Style.RESET_ALL,
			PROC      = record.proc + ': ' if record.proc else '',
			MSG       = record.msg,
			JOBS      = '' if record.jobidx is None else '[{ji}/{jt}] '.format(
				ji = str(record.jobidx + 1).zfill(len(str(record.joblen))),
				jt = record.joblen)
		)
		setattr(record, 'formatted', logging.Formatter.format(self, record))
		return record.formatted

class StreamHandler(logging.StreamHandler):
	"""
	Logging handler for stream (sys.stderr)
	"""
	CACHE = threading.local()

	@staticmethod
	def putprev(record):
		"""
		Put a pbar record in the cache
		@params:
			`record`: The record to put
		"""
		if not hasattr(StreamHandler.CACHE, 'prevlog'):
			setattr(StreamHandler.CACHE, 'prevlog', None)
		StreamHandler.CACHE.prevlog = record

	@staticmethod
	def getprev():
		"""
		Get a cached pbar record
		@returns:
			The pbar record
		"""
		if not hasattr(StreamHandler.CACHE, 'prevlog'):
			setattr(StreamHandler.CACHE, 'prevlog', None)
		return StreamHandler.CACHE.prevlog

	def __init__(self, stream = None):
		super(StreamHandler, self).__init__(stream)
		self.terminator = "\n"

	def _emit(self, record, terminator = "\n"):
		"""
		Helper function implementing a python2,3-compatible emit.
		Allow to add "\n" or "\r" as terminator.
		"""
		#terminator = '\n'
		if sys.version_info.major > 2: # pragma: no cover
			self.terminator = terminator
			super(StreamHandler, self).emit(record)
		else:
			msg    = self.format(record)
			stream = self.stream
			tmsg   = "%s" + terminator
			# if no unicode support...
			# # pragma: no cover # pylint: disable=no-member
			if not logging._unicode:
				stream.write(tmsg % msg)
			else:
				try:
					# # pragma: no cover pylint: disable=undefined-variable
					if isinstance(msg, unicode) \
						and getattr(stream, 'encoding', None):

						ufs = u'%s' + terminator
						try:
							stream.write(ufs % msg)
						except UnicodeEncodeError:
							#Printing to terminals sometimes fails. For example,
							#with an encoding of 'cp1251', the above write will
							#work if written to a stream opened or wrapped by
							#the codecs module, but fail when writing to a
							#terminal even when the codepage is set to cp1251.
							#An extra encoding step seems to be needed.
							stream.write((ufs % msg).encode(stream.encoding))
					else:
						stream.write(tmsg % msg)
				except UnicodeError: # pragma: no cover
					stream.write(tmsg % msg.encode("UTF-8"))
			self.flush()

	def emit(self, record):
		if record.ispbar:
			StreamHandler.putprev(record)
			self._emit(record, '\n' if record.done else '\r')
		else:
			pbarlog = StreamHandler.getprev()
			if pbarlog:
				self.stream.write(' ' * len(pbarlog.formatted) + '\r')

			self._emit(record, '\n')
			if hasattr(record, 'tails'):
				for tail in record.tails:
					self._emit(tail, '\n')

			if pbarlog:
				self._emit(pbarlog, '\r')

class StreamFilter(logging.Filter):
	"""
	Logging filter for stream (sys.stderr)
	"""
	def __init__(self, name, levels):
		super(StreamFilter, self).__init__(name)
		self.levels = levels
		self.debugs = {}

	def filter(self, record):
		# logging is disabled
		if not self.levels:
			return False

		level = record.mylevel
		dlevel = record.dlevel if hasattr(record, 'dlevel') else None
		# user logs
		if level.startswith('_') or \
			(level in self.levels and \
			(not dlevel or dlevel not in DEBUG_LINES)): # debug
			return True

		if level not in self.levels or \
			not hasattr(record, 'proc') or not record.proc: # independent
			return False

		# the limitation is only for one process
		if record.proc not in self.debugs:
			self.debugs = {record.proc: dict(zip(DEBUG_LINES.keys(), [0] * len(DEBUG_LINES)))}

		self.debugs[record.proc][dlevel] += 1
		allowed_lines = abs(DEBUG_LINES[dlevel])
		print_summary = DEBUG_LINES[dlevel] < 0
		if self.debugs[record.proc][dlevel] > allowed_lines:
			return False
		if self.debugs[record.proc][dlevel] < allowed_lines:
			return True
		# ==
		if print_summary:
			record.msg += "\n...... max={max} ({dlevel}) reached".format(
				max = allowed_lines, dlevel = dlevel)
			record.msg += ", further information will be ignored."
		return True

class FileFilter(StreamFilter):
	"""
	Logging filter for file
	"""
	def filter(self, record):
		if record.ispbar and not record.done:
			return False
		return super(FileFilter, self).filter(record)

class FileFormatter(logging.Formatter):
	"""
	Logging formatter for file,
	Extends StreamFormatter, removes the terminal colors
	"""
	def __init__(self):
		logging.Formatter.__init__(self, LOGFMT, LOGTIMEFMT)
		self.ansiRegex = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

	def format(self, record):
		# record has already been formatted by StreamFormatter
		# just remove the colors
		return self.ansiRegex.sub('', record.formatted)

class Logger(object):
	"""
	A wrapper of logger
	"""
	@staticmethod
	def initLevels(levels, leveldiffs):
		"""
		Initiate the levels, get real levels.
		@params:
			`levels`: The levels or level names
			`leveldiffs`: The diffs of levels
		@returns:
			The real levels.
		"""
		ret = set()
		if isinstance(levels, (tuple, list, set)):
			ret |= set(levels)
			ret |= LEVELS_ALWAYS
		elif levels not in (None, False):
			if levels is True:
				levels = 'normal'
			if levels.lower() in LEVELS:
				ret |= LEVELS[levels.lower()]
			elif levels:
				ret.add(levels)
			ret |= LEVELS_ALWAYS

		if not leveldiffs:
			return ret
		if not isinstance(leveldiffs, (tuple, list, set)):
			leveldiffs = set([leveldiffs])
		for level in leveldiffs:
			level = level.upper()
			if level.startswith('-'):
				level = level[1:]
				if level in ret:
					ret.remove(level)
			else:
				if level.startswith('+'):
					level = level[1:]
				ret.add(level)
		return ret

	def __init__(self, name = 'PyPPL', bake = False):
		self.baked  = bake or {}
		self.name   = name
		self.ispbar = False
		if bake:
			self.logger = logging.getLogger(self.name)
		else:
			self.init()

	def init(self):
		"""
		Initiate the logger, called by the construct,
		Just in case, we want to change the config and
		Reinitiate the logger.
		"""
		self.logger = logging.getLogger(self.name)
		self.logger.setLevel(1)
		for handler in self.logger.handlers:
			handler.close()
		del self.logger.handlers[:]

		theme = Theme(config._log.theme)
		levels = Logger.initLevels(config._log.levels, config._log.leveldiffs)

		stream_handler = StreamHandler()
		stream_handler.addFilter(StreamFilter(self.name, levels))
		stream_handler.setFormatter(StreamFormatter(theme))
		self.logger.addHandler(stream_handler)

		if config._log.file:
			file_handler = logging.FileHandler(config._log.file)
			file_handler.addFilter(FileFilter(self.name, levels))
			file_handler.setFormatter(FileFormatter())
			self.logger.addHandler(file_handler)

	def bake(self, **kwargs):
		"""
		Bake the logger with certain arguments
		"""
		return self.__class__(self.name, bake = kwargs)

	@property
	def pbar(self):
		"""
		Mark the record as a progress record.
		Allow `logger.pbar.info` access
		"""
		self.ispbar = True
		return self

	def _emit(self, *args, **kwargs):
		extra = {'jobidx': None, 'proc': ''}
		extra.update(self.baked)
		extra.update({'mylevel': kwargs.pop('_level')})
		extra.update(kwargs.pop('_extra'))
		extra.update(kwargs.pop('extra', {}))
		extra.update(kwargs)
		self.logger.info(*args, extra = extra)

	def __getitem__(self, name):
		return self.__getattr__(name)

	def __getattr__(self, name):
		ispbar = self.ispbar
		self.ispbar = False
		return partial(self._emit, _level = name.upper(), _extra = dict(
			ispbar = ispbar, dlevel = None))

# pylint: disable=invalid-name
logger = Logger()
