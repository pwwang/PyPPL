"""
A set of utitities for PyPPL
"""
import inspect
import re
import cmdy
import json
import safefs
import psutil
from os import path, walk
from box import Box
from time import sleep
from hashlib import md5
from threading import Thread, Lock
from simpleconf import Config
cmdy   = cmdy(_raise = False)
config = Config()


try:
	from Queue import Queue, PriorityQueue, Empty as QueueEmpty
except ImportError: # pragma: no cover
	from queue import Queue, PriorityQueue, Empty as QueueEmpty

try:
	string_types = basestring
except NameError: # pragma: no cover
	string_types = str

try:
	from ConfigParser import ConfigParser
except ImportError: # pragma: no cover
	from configparser import ConfigParser

ftools = Box()
try:
	from functools import reduce, map, filter
	ftools.reduce = reduce
	ftools.map    = map
	ftools.filter = filter
except ImportError: # pragma: no cover
	ftools.reduce = reduce
	ftools.map    = map
	ftools.filter = filter

try:
	unicode
	def _byteify(input, encoding='utf-8'):
		if isinstance(input, dict):
			return {_byteify(key): _byteify(value) for key, value in input.items()}
		elif isinstance(input, list):
			return [_byteify(element) for element in input]
		elif isinstance(input, unicode):
			return input.encode(encoding)
		else:
			return input
	jsonLoads = lambda s, encoding = 'utf-8': _byteify(json.loads(s), encoding)
except NameError: # py3
	jsonLoads = json.loads

try:
	ftools.range = xrange
except NameError: # pragma: no cover
	ftools.range = range

def varname(context = 31):
	"""
	Get the variable name for ini
	@params:
		`maxline`: The max number of lines to retrive. Default: 20
		`incldot`: Whether include dot in the variable name. Default: False
	@returns:
		The variable name
	"""
	stacks   = inspect.stack(context)
	parent   = stacks[1]
	grandpar = stacks[2]
	keyword  = parent[3]
	# find the class name
	if keyword == '__init__': 
		keyword = parent[0].f_locals['self'].__class__.__name__
	
	for i in range(grandpar[5], 0, -1):
		code = grandpar[4][i]
		if not keyword in code:
			continue
		m = re.search(r'([\w_]+)\s*=\s*[\w_.]*' + keyword, code)
		if not m:
			break
		return m.group(1)
	
	varname.index += 1
	return 'var_%s' % (varname.index - 1)

varname.index = 0

def reduce(func, vec):
	"""
	Python2 and Python3 compatible reduce
	@params:
		`func`: The reduce function
		`vec`: The list to be reduced
	@returns:
		The reduced value
	"""
	return ftools.reduce(func, vec)

def map(func, vec):
	"""
	Python2 and Python3 compatible map
	@params:
		`func`: The map function
		`vec`: The list to be maped
	@returns:
		The maped list
	"""
	return list(ftools.map(func, vec))

def filter(func, vec):
	"""
	Python2 and Python3 compatible filter
	@params:
		`func`: The filter function
		`vec`:  The list to be filtered
	@returns:
		The filtered list
	"""
	return list(ftools.filter(func, vec))

def range (i, *args, **kwargs):
	"""
	Convert a range to list, because in python3, range is not a list
	@params:
		`r`: the range data
	@returns:
		The converted list
	"""
	return list(ftools.range(i, *args, **kwargs))

def split (s, delimter, trim = True):
	"""
	Split a string using a single-character delimter
	@params:
		`s`: the string
		`delimter`: the single-character delimter
		`trim`: whether to trim each part. Default: True
	@examples:
		```python
		ret = split("'a,b',c", ",")
		# ret == ["'a,b'", "c"]
		# ',' inside quotes will be recognized.
		```
	@returns:
		The list of substrings
	"""
	ret   = []
	special1 = ['(', ')', '[', ']', '{', '}']
	special2 = ['\'', '"']
	special3 = '\\'
	flags1   = [0, 0, 0]
	flags2   = [False, False]
	flags3   = False
	start = 0
	for i, c in enumerate(s):
		if c == special3:
			flags3 = not flags3
		elif not flags3:
			if c in special1:
				index = special1.index(c)
				if index % 2 == 0:
					flags1[int(index/2)] += 1
				else:
					flags1[int(index/2)] -= 1
			elif c in special2:
				index = special2.index(c)
				flags2[index] = not flags2[index]
			elif c == delimter and not any(flags1) and not any(flags2):
				r = s[start:i]
				if trim: r = r.strip()
				ret.append(r)
				start = i + 1
		else:
			flags3 = False
	r = s[start:]
	if trim: r = r.strip()
	ret.append(r)
	return ret

def dictUpdate(origDict, newDict):
	"""
	Update a dictionary recursively.
	@params:
		`origDict`: The original dictionary
		`newDict`:  The new dictionary
	@examples:
		```python
		od1 = {"a": {"b": {"c": 1, "d":1}}}
		od2 = {key:value for key:value in od1.items()}
		nd  = {"a": {"b": {"d": 2}}}
		od1.update(nd)
		# od1 == {"a": {"b": {"d": 2}}}, od1["a"]["b"] is lost
		dictUpdate(od2, nd)
		# od2 == {"a": {"b": {"c": 1, "d": 2}}}
		```
	"""
	for k, v in newDict.items():

		if isinstance(v, list):
			origDict[k] = v[:]
		elif k in origDict and isinstance(origDict[k], dict) and isinstance(v, dict):
			dictUpdate(origDict[k], newDict[k])
		else:
			origDict[k] = newDict[k]

def funcsig (func):
	"""
	Get the signature of a function
	Try to get the source first, if failed, try to get its name, otherwise return None
	@params:
		`func`: The function
	@returns:
		The signature
	"""
	if callable (func):
		try:
			from inspect import getsource
			sig = getsource(func)
		except Exception: # pragma: no cover
			sig = func.__name__
	else:
		sig = 'None'
	return sig

def uid(s, l = 8, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'):
	"""
	Calculate a short uid based on a string.
	Safe enough, tested on 1000000 32-char strings, no repeated uid found.
	This is used to calcuate a uid for a process
	@params:
		`s`: the base string
		`l`: the length of the uid
		`alphabet`: the charset used to generate the uid
	@returns:
		The uid
	"""
	s = md5(str(s).encode('utf-8')).hexdigest()
	number = int (s, 16)
	base = ''

	while number != 0:
		number, i = divmod(number, len(alphabet))
		base = alphabet[i] + base

	return base[:l]

def formatSecs (seconds):
	"""
	Format a time duration
	@params:
		`seconds`: the time duration in seconds
	@returns:
		The formated string.
		For example: "01:01:01.001" stands for 1 hour 1 min 1 sec and 1 minisec.
	"""
	m, s = divmod(seconds, 60)
	h, m = divmod(m, 60)
	return "%02d:%02d:%02d.%03.0f" % (h, m, s, 1000*(s-int(s)))

def alwaysList (data):
	"""
	Convert a string or a list with element
	@params:
		`data`: the data to be converted
	@examples:
		```python
		data = ["a, b, c", "d"]
		ret  = alwaysList (data)
		# ret == ["a", "b", "c", "d"]
		```
	@returns:
		The split list
	"""
	if isinstance(data, string_types):
		ret = split (data, ',')
	elif isinstance(data, list):
		ret = []
		for d in data:
			if ',' in d:
				ret += split(d, ',')
			else:
				ret.append (d)
	else:
		raise ValueError('Expect string or list to convert to list.')
	return [x.strip() for x in ret]

def briefList(l):
	"""
	Briefly show an integer list, combine the continuous numbers.
	@params:
		`l`: The list
	@returns:
		The string to show for the briefed list.
	"""
	if not l: return "[]"
	if len(l) == 1: return str(l[0])
	l       = sorted(l)
	groups  = [[]]
	ret     = []
	for i in range(0, len(l) - 1):
		e0 = l[i]
		e1 = l[i + 1]
		if e1 - e0 > 1:
			groups[-1].append(e0)
			groups.append([])
		else:
			groups[-1].append(e0)
	groups[-1].append(l[-1])
	for group in groups:
		if len(group) == 1:
			ret.append(str(group[0]))
		elif len(group) == 2:
			ret.append(str(group[0]))
			ret.append(str(group[1]))
		else:
			ret.append(str(group[0]) + '-' + str(group[-1]))
	return ', '.join(ret)

def briefPath(p, cutoff = 0, keep = 1):
	"""
	Show briefed path in logs
	/abcde/hijklm/opqrst/uvwxyz/123456 will be shorted as:
	/a/h/opqrst/uvwxyz/123456
	@params:
		`p`       : The path
		`cutoff`  : Shorten the whole path if it more than length of cutoff. Default: `0`
		`keep`    : First N alphabetic chars to keep. Default: `1`
	@returns:
		The shorted path
	"""
	if not cutoff or not p:
		return p
	from os import path, sep
	p = path.normpath(p)
	lenp = len(p)
	if lenp <= cutoff:
		return p
	
	more = lenp - cutoff
	parts = p.split(sep)
	parts[0] = parts[0] or sep
	
	for i, part in enumerate(parts[:-1]):
		newpart = re.sub(r'^([^A-Za-z0-9]*\w{%s}).*$' % keep, r'\1', part)
		newlen  = len(newpart)
		more = more - (len(part) - newlen)
		if more < 0:
			parts[i] = part[:newlen-more]
			break
		parts[i] = newpart
	return path.join(*parts)

def killtree(pid, killme = True, sig = 9, timeout = None): # signal.SIGKILL

	me = psutil.Process(pid)
	children = me.children(recursive=True)
	if killme:
		children.append(me)
	for p in children:
		p.send_signal(sig)
	
	return psutil.wait_procs(children, timeout=timeout)

def chmodX(filepath, filetype = None):
	"""
	Convert file1 to executable or add extract shebang to cmd line
	@returns:
		A list with or without the path of the interpreter as the first element and the script file as the last element
	"""
	from stat import S_IEXEC
	from os import path, chmod, stat
	if not path.isfile(filepath):
		raise OSError('Unable to make {} as executable'.format(filepath))

	try:
		ChmodError = (OSError, PermissionError, UnicodeDecodeError)
	except NameError:
		ChmodError = OSError
	
	ret = [filepath]
	try:
		chmod(filepath, stat(filepath).st_mode | S_IEXEC)
	except ChmodError:
		shebang = None
		fsb = open(filepath)
		try:
			shebang = fsb.readline().strip()
		except ChmodError: # pragma: no cover
			# may raise UnicodeDecodeError for python3
			pass
		finally:
			# make sure file's closed, otherwise a File text busy will be raised when trying to execute it
			fsb.close()
		if not shebang or not shebang.startswith('#!'):
			raise OSError('Unable to make {} as executable by chmod and detect interpreter from shebang.'.format(filepath))
		ret = shebang[2:].strip().split() + [filepath]
	return ret

def filesig(filepath, dirsig = True):
	"""
	Generate a signature for a file
	@params:
		`dirsig`: Whether expand the directory? Default: True
	@returns:
		The signature
	"""
	if not filepath:
		return ['', 0]
	if not safefs.exists(filepath):
		return False
	
	if dirsig and safefs.isdir(filepath):
		mtime = path.getmtime(filepath)
		for root, dirs, files in walk(filepath):
			for d in dirs:
				mtime2 = path.getmtime(path.join(root, d))
				mtime  = max(mtime, mtime2)
			for f in files:
				mtime2 = path.getmtime(path.join(root, f))
				mtime  = max(mtime, mtime2)
	else:
		mtime = path.getmtime(filepath)
	return [filepath, int(mtime)]

def fileflush(fd, lastmsg, end = False):
	"""
	Flush a file descriptor
	@params:
		`fd`     : The file handler
		`lastmsg`: The remaining content of last flush
		`end`    : The file ends? Default: `False`
	"""
	fd.flush()
	# OSX cannot tell the pointer automatically
	fd.seek(fd.tell())
	lines = fd.readlines() or []
	if lines:
		lines[0] = lastmsg + lines[0]
		lastmsg  = '' if lines[-1].endswith('\n') else lines.pop(-1)
		if lastmsg and end:
			lines.append(lastmsg + '\n')
			lastmsg = ''
	elif lastmsg and end:
		lines.append(lastmsg + '\n')
		lastmsg = ''
	return lines, lastmsg

class ThreadEx(Thread):
	"""
	A thread able to send exception to main thread
	thread.ex will hold the exception.
	"""

	def __init__(self, group=None, target=None, name=None, args=None, kwargs=None):
		Thread.__init__(self, group, target, name, args or (), kwargs or {})
		self.daemon = True
		self.ex     = None

	def run(self):
		try:
			Thread.run(self)
		except Exception as ex:
			from traceback import format_exc
			self.ex = RuntimeError(format_exc()) if isinstance(ex, cmdy.CmdyReturnCodeException) \
				else type(ex)(format_exc())

class ThreadPool(object):
	"""
	A thread manager for ThreadEx.
	"""

	def __init__(self, nthread, initializer = None, initargs = None):
		self.threads = []
		if not isinstance(initargs, list):
			initargs = [(initargs, ) if initargs else ()] * nthread
		for i in range(nthread):
			thread = ThreadEx(target = initializer, args = initargs[i])
			thread.start()
			self.threads.append(thread)

	def join(self, interval = 1, cleanup = None):
		"""
		Try to join the threads, able to respond to KeyboardInterrupt
		@params:
			`interval`: The interval/timeout to join every time.
			`cleanup` : The cleanup function
		"""
		try:
			while any(thread.isAlive() for thread in self.threads):
				for thread in self.threads:
					if thread.ex:
						if callable(cleanup):
							cleanup(ex = thread.ex)
						else:
							raise thread.ex
					thread.join(timeout = interval)
		except KeyboardInterrupt as ex:
			if callable(cleanup):
				cleanup(ex = ex)

class PQueue(PriorityQueue):
	"""
	A modified PriorityQueue, which allows jobs to be submitted in batch
	"""

	def __init__(self, maxsize = 0, batch_len = None):
		"""
		Initialize the queue
		@params:
			`maxsize`  : The maxsize of the queue
			`batch_len`: What's the length of a batch
		"""
		if not batch_len:
			raise ValueError('`batch_len` is required for PQueue.')
		PriorityQueue.__init__(self, maxsize)
		self.batch_len = batch_len
		self.lock      = Lock()

	def put(self, item, block = True, timeout = None, where = 0):
		"""
		Put item to the queue, just like `PriorityQueue.put` but with an extra argument
		@params:
			`where`: Which batch to put the item
		"""
		with self.lock:
			PriorityQueue.put(self, item + where * self.batch_len, block, timeout)
	
	def put_nowait(self, item, where = 0):
		"""
		Put item to the queue, just like `PriorityQueue.put_nowait` but with an extra argument
		@params:
			`where`: Which batch to put the item
		"""
		with self.lock:
			PriorityQueue.put_nowait(self, item + where * self.batch_len)

	def get(self, block = True, timeout = None):
		"""
		Get an item from the queue
		"""
		item = PriorityQueue.get(self, block, timeout)
		ret  = divmod(item, self.batch_len)
		return (ret[1], ret[0])

	def get_nowait(self):
		"""
		Get an item from the queue without waiting
		"""
		item = PriorityQueue.get(self)
		ret  = divmod(item, self.batch_len)
		return (ret[1], ret[0])



