import helpers, testly, unittest

from os import path, getcwd, makedirs
from shutil import rmtree
from tempfile import gettempdir
from hashlib import md5
from collections import OrderedDict
from pyppl import Job, Proc, utils
from pyppl.runners import Runner, RunnerLocal, RunnerDry, RunnerSsh, RunnerSge, RunnerSlurm
from pyppl.template import TemplateLiquid
from pyppl.exception import RunnerSshError
from pyppl.runners.helpers import Helper, LocalHelper, SgeHelper, SlurmHelper, SshHelper

__folder__ = path.realpath(path.dirname(__file__))

def clearMockQueue():
	qsubQfile   = path.join(__folder__, 'mocks', 'qsub.queue.txt')
	sbatchQfile = path.join(__folder__, 'mocks', 'sbatch.queue.txt')
	helpers.writeFile(qsubQfile, '')
	helpers.writeFile(sbatchQfile, '')

def _generateJob(testdir, index = 0, pProps = None, jobActs = None):
	p = Proc()
	uid = dict(index = index, pProps = pProps, jobActs = jobActs)
	p.props['workdir'] = path.join(testdir, 'p.' + utils.uid(str(uid)), 'workdir')
	p.props['script']  = TemplateLiquid('')
	p.props['ncjobids']  = list(range(40))
	if pProps:
		p.props.update(pProps)
	job = Job(index, p)
	job.init()
	if jobActs:
		jobActs(job)
	return job

class TestHelper(testly.TestCase):

	def setUpMeta(self):
		self.testdir = path.join(gettempdir(), 'PyPPL_unittest', 'TestHelper')
		if path.exists(self.testdir):
			rmtree(self.testdir)
		makedirs(self.testdir)
	
	def testInit(self, script):
		h = Helper(script)
		h.submit()
		h.run()
		h.kill()
		h.alive()
		self.assertEqual(h.script , script)
		self.assertEqual(h.pidfile, path.join(path.dirname(h.script), 'job.pid'))
		self.assertEqual(h.rcfile , path.join(path.dirname(h.script), 'job.rc'))
		self.assertEqual(h.outfile, path.join(path.dirname(h.script), 'job.stdout'))
		self.assertEqual(h.errfile, path.join(path.dirname(h.script), 'job.stderr'))
		self.assertEqual(h.outfd  , None)
		self.assertEqual(h.errfd  , None)
		self.assertEqual(h.cmds   , {})
		self.assertEqual(h._pid   , None)
	
	def dataProvider_testInit(self):
		yield path.join(self.testdir, 'job.script'),

	def testPid(self, h, pid):
		self.assertEqual(h.pid, pid)
		h.pid = 1
		self.assertEqual(h.pid, 1)

	def dataProvider_testPid(self):
		script = path.join(self.testdir, 'job.script')
		h = Helper(script)
		yield h, None

		script2 = path.join(self.testdir, 'testPid', 'job.script')
		makedirs(path.dirname(script2))
		h2 = Helper(script2)
		h2.pid = None
		yield h2, None

class TestLocalHelper(testly.TestCase):

	def setUpMeta(self):
		self.testdir = path.join(gettempdir(), 'PyPPL_unittest', 'TestLocalHelper')
		if path.exists(self.testdir):
			rmtree(self.testdir)
		makedirs(self.testdir)

	def testSubmit(self, h):
		c = h.submit()
		self.assertEqual(c.rc, 0)

	def dataProvider_testSubmit(self):
		script = path.join(self.testdir, 'job.script')
		helpers.writeFile(script, '#!/usr/bin/env bash\n')
		yield LocalHelper(script),

	def testRun(self, h, rc, stdout):
		h.run()
		h.outfd.close()
		h.errfd.close()
		self.assertEqual(h.proc.rc, rc)
		with open(h.outfile) as f:
			self.assertEqual(utils.asStr(f.read()).strip(), stdout)

	def dataProvider_testRun(self):
		script = path.join(self.testdir, 'testRun', 'job.script')
		makedirs(path.dirname(script))
		helpers.writeFile(script, '#!/usr/bin/env bash\necho 123')
		yield LocalHelper(script), 0, '123'

	def testKill(self, h):
		h.pid = h.submit().pid
		for pid in utils.ps.children(h.pid):
			self.assertTrue(utils.ps.exists(pid))
		h.kill()
		for pid in utils.ps.children(h.pid):
			self.assertFalse(utils.ps.exists(pid))

	def dataProvider_testKill(self):
		script = path.join(self.testdir, 'job.script')
		helpers.writeFile(script, '#!/usr/bin/env bash\nsleep .1')
		yield LocalHelper(script),

	def testAlive(self, h, alive, aliveAfterSubmit):
		self.assertEqual(h.alive(), alive)
		c = h.submit()
		h.pid = c.pid
		self.assertEqual(h.alive(), aliveAfterSubmit)
		c.run()
		self.assertEqual(h.alive(), False)

	def dataProvider_testAlive(self):
		script1 = path.join(self.testdir, 'testAlive', 'job.script')
		makedirs(path.dirname(script1))
		# not exists
		h1 = LocalHelper(script1)
		yield h1, False, True

		script2 = path.join(self.testdir, 'testAlive2', 'job.script')
		makedirs(path.dirname(script2))
		helpers.writeFile(script2, '#!/usr/bin/env bash\nsleep .1')
		h3 = LocalHelper(script2)
		yield h3, False, True

	def testQuit(self, h, rc):
		h.run()
		h.quit()
		with open(h.rcfile) as f:
			self.assertEqual(utils.asStr(f.read()), rc)

	def dataProvider_testQuit(self):
		script = path.join(self.testdir, 'testQuit', 'job.script')
		makedirs(path.dirname(script))
		helpers.writeFile(script, '#!/usr/bin/env bash\n')
		yield LocalHelper(script), '0'

class TestSshHelper(testly.TestCase):

	def setUpMeta(self):
		self.testdir = path.join(gettempdir(), 'PyPPL_unittest', 'TestSshHelper')
		if path.exists(self.testdir):
			rmtree(self.testdir)
		makedirs(self.testdir)
		self.commands = 'bash -c'

	def testSubmit(self, h):
		c = h.submit()
		self.assertEqual(c.rc, 0)

	def dataProvider_testSubmit(self):
		script = path.join(self.testdir, 'job.script')
		helpers.writeFile(script, '#!/usr/bin/env bash\n')
		yield SshHelper(script, self.commands),

	def testKill(self, h):
		h.pid = h.submit().pid
		for pid in utils.ps.children(h.pid):
			self.assertTrue(utils.ps.exists(pid))
		h.kill()
		for pid in utils.ps.children(h.pid):
			self.assertFalse(utils.ps.exists(pid))

	def dataProvider_testKill(self):
		script = path.join(self.testdir, 'job.script')
		helpers.writeFile(script, '#!/usr/bin/env bash\nsleep .1')
		yield SshHelper(script, self.commands),

	def testAlive(self, h, alive, aliveAfterSubmit):
		self.assertEqual(h.alive(), alive)
		c = h.submit()
		h.pid = c.pid
		self.assertEqual(h.alive(), aliveAfterSubmit)
		c.run()
		self.assertEqual(h.alive(), False)

	def dataProvider_testAlive(self):
		script1 = path.join(self.testdir, 'testAlive', 'job.script')
		makedirs(path.dirname(script1))
		# not exists
		h1 = SshHelper(script1, self.commands)
		yield h1, False, False

		script2 = path.join(self.testdir, 'testAlive2', 'job.script')
		makedirs(path.dirname(script2))
		helpers.writeFile(script2, '#!/usr/bin/env bash\nsleep .1')
		h3 = SshHelper(script2, self.commands)
		yield h3, False, True

class TestSgeHelper(testly.TestCase):

	def setUpMeta(self):
		self.testdir = path.join(gettempdir(), 'PyPPL_unittest', 'TestSgeHelper')
		if path.exists(self.testdir):
			rmtree(self.testdir)
		makedirs(self.testdir)
		self.commands = {
			'qsub' : path.join(__folder__, 'mocks', 'qsub'),
			'qstat': path.join(__folder__, 'mocks', 'qstat'),
			'qdel' : path.join(__folder__, 'mocks', 'qdel')
		}

	def testSubmit(self, h, rc):
		c = h.submit()
		self.assertEqual(c.rc, rc)

	def dataProvider_testSubmit(self):
		script = path.join(self.testdir, 'job.script')
		helpers.writeFile(script, '#!/usr/bin/env bash')
		yield SgeHelper(script, self.commands), 0
		yield SgeHelper(script, {'qsub': 'nosuchqsub'}), 1
		yield SgeHelper(script, {'qsub': 'echo'}), 1


	def testAlive(self, h, alive, aliveAfterSubmit):
		self.assertEqual(h.alive(), alive)
		h.submit()
		self.assertEqual(h.alive(), aliveAfterSubmit)
		h.kill()
		self.assertEqual(h.alive(), False)

	def dataProvider_testAlive(self):
		script1 = path.join(self.testdir, 'testAlive', 'job.script')
		makedirs(path.dirname(script1))
		# not exists
		h1 = SgeHelper(script1, self.commands)
		yield h1, False, True

		script2 = path.join(self.testdir, 'testAlive2', 'job.script')
		makedirs(path.dirname(script2))
		helpers.writeFile(script2, '#!/usr/bin/env bash\nsleep .1')
		h3 = SgeHelper(script2, self.commands)
		yield h3, False, True

class TestSlurmHelper(testly.TestCase):

	def setUpMeta(self):
		self.testdir = path.join(gettempdir(), 'PyPPL_unittest', 'TestSlurmHelper')
		if path.exists(self.testdir):
			rmtree(self.testdir)
		makedirs(self.testdir)
		self.commands = {
			'sbatch' : path.join(__folder__, 'mocks', 'sbatch'),
			'squeue': path.join(__folder__, 'mocks', 'squeue'),
			'srun' : path.join(__folder__, 'mocks', 'srun'),
			'scancel' : path.join(__folder__, 'mocks', 'scancel')
		}

	def testSubmit(self, h):
		c = h.submit()
		self.assertEqual(c.rc, 0)

	def dataProvider_testSubmit(self):
		script = path.join(self.testdir, 'job.script')
		helpers.writeFile(script, '#!/usr/bin/env bash')
		yield SlurmHelper(script, self.commands),

	def testAlive(self, h, alive, aliveAfterSubmit):
		self.assertEqual(h.alive(), alive)
		h.submit()
		self.assertEqual(h.alive(), aliveAfterSubmit)
		h.kill()
		self.assertEqual(h.alive(), False)

	def dataProvider_testAlive(self):
		script1 = path.join(self.testdir, 'testAlive', 'job.script')
		makedirs(path.dirname(script1))
		# not exists
		h1 = SlurmHelper(script1, self.commands)
		yield h1, False, True

		script2 = path.join(self.testdir, 'testAlive2', 'job.script')
		makedirs(path.dirname(script2))
		helpers.writeFile(script2, '#!/usr/bin/env bash\nsleep .1')
		h3 = SlurmHelper(script2, self.commands)
		yield h3, False, True

class TestRunner(testly.TestCase):

	def setUpMeta(self):
		self.testdir = path.join(gettempdir(), 'PyPPL_unittest', 'TestRunner')
		if path.exists(self.testdir):
			rmtree(self.testdir)
		makedirs(self.testdir)
	
	def dataProvider_testInit(self):
		yield _generateJob(self.testdir),

	def testInit(self, job):
		r = Runner(job)
		self.assertIsInstance(r, Runner)
		self.assertIs(r.job, job)
		self.assertEqual(r.script, [job.script])
		self.assertEqual(r.cmd2run, job.script)
		self.assertEqual(r.ntry.value, 0)
		
	def dataProvider_testIsRunning(self):
		yield _generateJob(self.testdir), False
		yield _generateJob(self.testdir, index = 1, jobActs = lambda job: job.pid(0)), False
		
	def testIsRunning(self, job, ret):
		r = Runner(job)
		self.assertEqual(r.isRunning(), ret)
		
	# def dataProvider_testSubmit(self):
	# 	# job cached
	# 	yield _generateJob(self.testdir, pProps = {'ncjobids': []}), True
	# 	# job is running
	# 	yield _generateJob(
	# 		self.testdir,
	# 		index = 1,
	# 		jobActs = lambda job: job.pid(0)
	# 	), True, ['SUBMIT', "[2/0] is already running, skip submission."]
	# 	# submission failure
	# 	yield _generateJob(
	# 		self.testdir,
	# 		index = 2,
	# 		pProps = {'script': TemplateLiquid('#!/usr/bin/env bash\nexit 1')}
	# 	), False, ['ERROR', "[3/0] Submission failed with return code: 1."]
	# 	# submission failure exception
	# 	yield _generateJob(
	# 		self.testdir,
	# 		index = 3,
	# 		pProps = {'script': TemplateLiquid('exit 1')}
	# 	), False, ['ERROR', "[4/0] Submission failed with exception: [Errno 8] Exec format error"]
	# 	# submission success
	# 	yield _generateJob(
	# 		self.testdir,
	# 		index = 4,
	# 		pProps = {'script': TemplateLiquid('#!/usr/bin/env bash\nexit 0')}
	# 	), True
		
	# def testSubmit(self, job, ret, errs = []):
	# 	r = Runner(job)
	# 	with helpers.log2str(levels = 'all') as (out, err):
	# 		o = r.submit()
	# 	stderr = err.getvalue()
	# 	self.assertEqual(o, ret)
	# 	for err in errs:
	# 		self.assertIn(err, stderr)
	# 	if not ret:
	# 		self.assertEqual(job.rc(), Job.RC_SUBMITFAIL)
	
	def dataProvider_testFinish(self):
		yield _generateJob(self.testdir),
		
	def testFinish(self, job):
		r = Runner(job)
		self.assertIsNone(r.finish())
		
	def dataProvider_testGetpid(self):
		yield _generateJob(self.testdir),
		
	def testGetpid(self, job):
		r = Runner(job)
		self.assertIsNone(r.getpid())
	
	def dataProvider_testRetry(self):
		yield _generateJob(self.testdir, pProps = {'errhow': 'terminate'}), False
		yield _generateJob(self.testdir, index = 1, pProps = {'errhow': 'retry', 'errntry': 3}), True, [
			'RETRY',
			'[2/0]',
			'Retrying job (1/3) ...'
		]
		yield _generateJob(self.testdir, index = 2, pProps = {'errhow': 'retry', 'errntry': 0}), False
		
	def testRetry(self, job, ret, errs = []):
		r = Runner(job)
		with helpers.log2str() as (out, err):
			o = r.retry()
		stderr = err.getvalue()
		self.assertEqual(o, ret)
		for err in errs:
			self.assertIn(err, stderr)
			
	def dataProvider_testFlush(self):
		job = _generateJob(self.testdir, pProps = {'echo': {'jobs': []}})
		yield job, {'': ('', None)}, {'': ('', None)}
		
		job1 = _generateJob(self.testdir, index = 1, pProps = {'echo': {'jobs': [1], 'type': {'stdout': None}}})
		yield job1, {'': ('', '')}, {}
		yield job1, {'123': ('123', '')}, {}
		yield job1, OrderedDict([
			('123\n', ('123', '')),
			('456\n78', ('456', '78')),
			('910', ('78910', ''))
		]), {}
		# filter
		job2 = _generateJob(self.testdir, index = 2, pProps = {'echo': {'jobs': [2], 'type': {'stdout': '^a'}}})
		yield job1, {'': ('', '')}, {}
		yield job1, {'123': ('', '')}, {}
		yield job1, OrderedDict([
			('123\n', ('', '')),
			('456\na78', ('', 'a78')),
			('910', ('a78910', ''))
		]), {}
		# stderr
		job3 = _generateJob(self.testdir, index = 3, pProps = {'echo': {'jobs': [3], 'type': {'stderr': None}}})
		yield job3, {}, OrderedDict([
			('pyppl.log: 123', ('[4/0] 123', ''))
		])
		yield job3, {}, OrderedDict([
			('456\n78', ('456', '78')),
			('9\npyppl.log', ('789', 'pyppl.log')),
			(': 123', ('', 'pyppl.log: 123')),
			('a\n78', ('[4/0] 123a', '78')),
			('b', ('78b', '')),
		])
		# stderr filter
		job4 = _generateJob(self.testdir, index = 4, pProps = {'echo': {'jobs': [4], 'type': {'stderr': '^7'}}})
		yield job4, {}, OrderedDict([
			('pyppl.log.flag ', ('[5/0] ', ''))
		])
		yield job4, {}, OrderedDict([
			('456\n78', ('', '78')),
			('9\npyppl.log', ('789', 'pyppl.log')),
			(': 123', ('', 'pyppl.log: 123')),
			('a\n78', ('[5/0] 123a', '78')),
			('b', ('78b', '')),
		])
		
			
	def testFlush(self, job, outs, errs):
		r = Runner(job)
		lastout, lasterr = '', ''
		foutr = open(job.outfile, 'r')
		ferrr = open(job.errfile, 'r')
		foutw = open(job.outfile, 'w')
		ferrw = open(job.errfile, 'w')
		for i, k in enumerate(outs.keys()):
			o, lo = outs[k] # out, lastout
			end = i == len(outs) - 1
			foutw.write(k)
			foutw.flush()
			with helpers.log2str() as (out, err):
				lastout, lasterr = r._flush(foutr, ferrr, lastout, lasterr, end)
			self.assertEqual(lastout, lo)
			self.assertIn(o, out.getvalue())
		for i, k in enumerate(errs.keys()):
			e, le = errs[k]
			end = i == len(errs) - 1
			ferrw.write(k)
			ferrw.flush()
			with helpers.log2str() as (out, err):
				lastout, lasterr = r._flush(foutr, ferrr, lastout, lasterr, end)
			self.assertEqual(lasterr, le)
			self.assertIn(e, err.getvalue())
		foutr.close()
		ferrr.close()
		foutw.close()
		ferrw.close()
	
	# def dataProvider_testRun(self):
	# 	# job cached
	# 	yield _generateJob(self.testdir, pProps = {'ncjobids': []}), True
	# 	yield _generateJob(
	# 		self.testdir,
	# 		index = 1,
	# 		pProps = {'ncjobids': [1], 'echo': {'jobs': []}},
	# 		jobActs = lambda job: job.rc(1)
	# 	), False
	# 	yield _generateJob(
	# 		self.testdir,
	# 		index = 2,
	# 		pProps = {
	# 			'ncjobids': [2],
	# 			'echo': {'jobs': [2], 'type': {'stdout': None}},
	# 			'script': TemplateLiquid('#!/usr/bin/env bash\nprintf 1\nbash -c \'sleep .5; echo 1 > "{{job.dir}}/job.rc"\'\nprintf 3')
	# 		}
	# 	), False, ['13']
	# 	yield _generateJob(
	# 		self.testdir,
	# 		index = 3,
	# 		pProps = {
	# 			'expect': TemplateLiquid(''),
	# 			'ncjobids': [3],
	# 			'echo': {'jobs': [3], 'type': {'stdout': None}},
	# 			'script': TemplateLiquid('#!/usr/bin/env bash\nprintf 2\nbash -c \'sleep .5; echo 0 > "{{job.dir}}/job.rc"\'\nprintf 4')
	# 		}
	# 	), True, ['24']
		
	# def testRun(self, job, ret, outs = [], errs = []):
	# 	Runner.INTERVAL = .1
	# 	r = Runner(job)
	# 	with helpers.log2str() as (out, err):
	# 		r.submit()
	# 		o = r.run()
	# 	self.assertEqual(o, ret)
	# 	stdout = out.getvalue()
	# 	stderr = err.getvalue()

	# 	for o in outs:
	# 		self.assertIn(o, stdout)
	# 	for e in errs:
	# 		self.assertIn(e, stderr)

class TestRunnerLocal(testly.TestCase):

	def setUpMeta(self):
		self.testdir = path.join(gettempdir(), 'PyPPL_unittest', 'TestRunnerLocal')
		if path.exists(self.testdir):
			rmtree(self.testdir)
		makedirs(self.testdir)
	
	def dataProvider_testInit(self):
		yield _generateJob(
			self.testdir, 
			pProps = {'localRunner': {'preScript': 'prescript', 'postScript': 'postscript'}}
		),

	def testInit(self, job):
		r = RunnerLocal(job)
		self.assertIsInstance(r, RunnerLocal)
		self.assertTrue(path.exists(job.script + '.local'))
		# self.assertTrue(path.exists(job.script + '.submit'))
		# helpers.assertTextEqual(self, helpers.readFile(job.script + '.local', str), '\n'.join([
		# 	"#!/usr/bin/env bash",
		# 	"echo $$ > '%s'",
		# 	'trap "status=\\$?; echo \\$status >\'%s\'; exit \\$status" 1 2 3 6 7 8 9 10 11 12 15 16 17 EXIT',
		# 	'prescript',
		# 	'',
		# 	"%s 1>'%s' 2>'%s'",
		# 	'postscript',
		# ]) % (job.pidfile, job.rcfile, job.script, job.outfile, job.errfile) + '\n')
		# helpers.assertTextEqual(self, helpers.readFile(job.script + '.submit', str), '\n'.join([
		# 	"#!/usr/bin/env bash",
		# 	"exec '%s' &"
		# ]) % (job.script + '.local') + '\n')
		
	
	def dataProvider_testSubmitNRun(self):
		yield _generateJob(
			self.testdir,
			pProps = {
				'expect': TemplateLiquid(''),
				'ncjobids': [0],
				'echo': {'jobs': [0], 'type': {'stdout': None}},
				'script': TemplateLiquid('#!/usr/bin/env bash\nprintf 123\nsleep .2\nprintf 456')
			}
		), True, ['123456']
		yield _generateJob(
			self.testdir,
			index = 1,
			pProps = {
				'expect': TemplateLiquid(''),
				'ncjobids': [1],
				'echo': {'jobs': [1], 'type': {'stdout': None}},
				'script': TemplateLiquid('#!/usr/bin/env bash\nprintf 123 >&2\nsleep .2\nprintf 456 >&2\nexit 1')
			}
		), False, [], ['123456']
		yield _generateJob(
			self.testdir,
			index = 2,
			pProps = {
				'expect': TemplateLiquid(''),
				'ncjobids': [2],
				'echo': {'jobs': [2], 'type': {'stdout': None}},
				'script': TemplateLiquid('#!/usr/bin/env bash\nprintf 123 >&2\nsleep .2\nprintf 4566 >&2\nexit 1')
			}
		), False, [], ['1234566']
	
	def testSubmitNRun(self, job, ret, outs = [], errs = []):
		from time import sleep
		RunnerLocal.INTERVAL = .01
		r = RunnerLocal(job)
		r.submit()
		while not path.isfile(r.helper.pidfile):
			sleep (.01)
		with helpers.log2str():
			r.submit() # is running
			o = r.run()
		self.assertEqual(o, ret)
		stdout = helpers.readFile(job.outfile, str)
		stderr = helpers.readFile(job.errfile, str)
		for o in outs:
			self.assertIn(o, stdout)
		for e in errs:
			self.assertIn(e, stderr)

class TestRunnerDry(testly.TestCase):

	def setUpMeta(self):
		self.testdir = path.join(gettempdir(), 'PyPPL_unittest', 'TestRunnerDry')
		if path.exists(self.testdir):
			rmtree(self.testdir)
		makedirs(self.testdir)
	
	def dataProvider_testInit(self):
		yield _generateJob(
			self.testdir
		),

	def testInit(self, job):
		r = RunnerDry(job)
		self.assertIsInstance(r, RunnerDry)
		self.assertTrue(path.exists(job.script + '.dry'))
		# self.assertTrue(path.exists(job.script + '.submit'))
		helpers.assertTextEqual(self, helpers.readFile(job.script + '.dry', str), '\n'.join([
			"#!/usr/bin/env bash",
			''
		]) + '\n')
		# helpers.assertTextEqual(self, helpers.readFile(job.script + '.submit', str), '\n'.join([
		# 	"#!/usr/bin/env bash",
		# 	"exec '%s' &"
		# ]) % (job.script + '.dry') + '\n')
		
	
	def dataProvider_testSubmitNRun(self):
		yield _generateJob(
			self.testdir,
			pProps = {
				'expect': TemplateLiquid(''),
				'ncjobids': [0],
				'echo': {'jobs': [0], 'type': {'stdout': None}},
				'script': TemplateLiquid('')
			}
		), True
		
		job = _generateJob(
			self.testdir,
			index = 1,
			pProps = {
				'expect': TemplateLiquid(''),
				'ncjobids': [1],
				'echo': {'jobs': [1], 'type': {'stdout': None}},
				'script': TemplateLiquid(''),
				'output': {
					'a': ('file', TemplateLiquid('runndry.txt')),
					'b': ('dir', TemplateLiquid('runndry.dir')),
					'c': ('var', TemplateLiquid('runndry.dir')),
				}
			}
		)
		yield job, True, [path.join(job.outdir, 'runndry.txt')], [path.join(job.outdir, 'runndry.dir')]
	
	def testSubmitNRun(self, job, ret, files = [], dirs = []):
		RunnerDry.INTERVAL = .1
		r = RunnerDry(job)
		r.submit()
		o = r.run()
		self.assertEqual(o, ret)
		for f in files:
			self.assertTrue(path.isfile(f))
		for d in dirs:
			self.assertTrue(path.isdir(d))
			
	def dataProvider_testFinish(self):
		yield _generateJob(
			self.testdir,
			pProps = {
				'expect': TemplateLiquid(''),
			},
			jobActs = lambda job: job.rc(0) or job.cache()
		), 
			
	def testFinish(self, job):
		r = RunnerDry(job)
		r.finish()
		self.assertTrue(job.succeed())
		self.assertFalse(path.isfile(job.cachefile))

class TestRunnerSsh(testly.TestCase):

	def _localSshAlive():
		#return utils.dumbPopen('ps axf | grep sshd | grep -v grep', shell = True).wait() == 0
		return RunnerSsh.isServerAlive('localhost', None)
		
	def setUpMeta(self):
		self.testdir = path.join(gettempdir(), 'PyPPL_unittest', 'TestRunnerSsh')
		if path.exists(self.testdir):
			rmtree(self.testdir)
		makedirs(self.testdir)		
	
	def dataProvider_testIsServerAlive(self):
		if self._localSshAlive():
			yield 'localhost', None, True
		yield 'blahblah', None, False
	
	def testIsServerAlive(self, server, key, ret):
		self.assertEqual(RunnerSsh.isServerAlive(server, key), ret)
		
	def dataProvider_testInit(self):
		yield _generateJob(
			self.testdir
		), RunnerSshError, 'No server found for ssh runner.'
		
		servers = ['server1', 'server2', 'localhost']
		keys    = ['key1', 'key2', None]
		yield _generateJob(
			self.testdir,
			index = 1,
			pProps = {'sshRunner': {
				'servers': servers,
				'keys'   : keys,
				'checkAlive': False,
			}}
		),
		
		yield _generateJob(
			self.testdir,
			index = 2,
			pProps = {'sshRunner': {
				'servers': servers,
				'keys'   : keys,
				'checkAlive': False
			}}
		),
		
		yield _generateJob(
			self.testdir,
			index = 3,
			pProps = {'sshRunner': {
				'servers': servers,
				'keys'   : keys,
				'checkAlive': False,
				'preScript': 'ls',
				'postScript': 'ls',
			}}
		),
		
		if self._localSshAlive():
			# should be localhost'
			yield _generateJob(
				self.testdir,
				index = 4,
				pProps = {'sshRunner': {
					'servers': servers,
					'keys'   : keys,
					'checkAlive': True
				}}
			),
		else:
			yield _generateJob(
				self.testdir,
				index = 4,
				pProps = {'sshRunner': {
					'servers': servers,
					'keys'   : keys,
					'checkAlive': True
				}}
			), RunnerSshError, 'No server is alive.'
		
		# no server is alive
		yield _generateJob(
			self.testdir,
			index = 5,
			pProps = {'sshRunner': {
				'servers': ['server1', 'server2', 'server3'],
				'checkAlive': True,
			}}
		), RunnerSshError, 'No server is alive.'

	def testInit(self, job, exception = None, msg = None):
		self.maxDiff = None
		RunnerSsh.LIVE_SERVERS = None
		if exception:
			self.assertRaisesRegex(exception, msg, RunnerSsh, job)
		else:
			r = RunnerSsh(job)
			servers = job.proc.sshRunner['servers']
			keys = job.proc.sshRunner['keys']
			sid = (RunnerSsh.SERVERID.value - 1) % len(servers)
			server = servers[sid]
			key = ('-i ' + keys[sid]) if keys[sid] else ''
			self.assertIsInstance(r, RunnerSsh)
			self.assertTrue(path.exists(job.script + '.ssh'))
			#self.assertTrue(path.exists(job.script + '.submit'))
			preScript = r.job.proc.sshRunner.get('preScript', '')
			preScript = preScript and preScript + '\n'
			postScript = r.job.proc.sshRunner.get('postScript', '')
			postScript = postScript and '\n' + postScript
			helpers.assertTextEqual(self, helpers.readFile(job.script + '.ssh', str), '\n'.join([
				"#!/usr/bin/env bash",
				"",
				'%scd %s; %s%s',
			]) % (
				preScript, 
				getcwd(), 
				job.script, 
				postScript
			) + '\n')
			# helpers.assertTextEqual(self, helpers.readFile(job.script + '.submit', str), '\n'.join([
			# 	"#!/usr/bin/env bash",
			# 	"exec '%s' &"
			# ]) % (job.script + '.ssh') + '\n')
		
	
	def dataProvider_testSubmitNRun(self):
		yield _generateJob(
			self.testdir,
			pProps = {
				'expect': TemplateLiquid(''),
				'ncjobids': [0],
				'echo': {'jobs': [0], 'type': {'stdout': None}},
				'sshRunner': {
					'servers': ['server1', 'server2', 'localhost'],
					'checkAlive': True,
					'preScript': 'alias ssh="%s"' % (path.join(__folder__, 'mocks', 'ssh')),
					'postScript': ''
				},
				'script': TemplateLiquid('#!/usr/bin/env bash\nprintf 123\nsleep .5\nprintf 456')
			}
		), True, ['123456']
		yield _generateJob(
			self.testdir,
			index = 1,
			pProps = {
				'expect': TemplateLiquid(''),
				'ncjobids': [1],
				'echo': {'jobs': [1], 'type': {'stdout': None}},
				'sshRunner': {
					'servers': ['server1', 'server2', 'localhost'],
					'checkAlive': True,
					'preScript': 'alias ssh="%s"' % (path.join(__folder__, 'mocks', 'ssh')),
					'postScript': ''
				},
				'script': TemplateLiquid('#!/usr/bin/env bash\nprintf 123 >&2\nsleep .5\nprintf 456 >&2\nexit 1')
			}
		), False, [], ['123456']
	
	@unittest.skipIf(not RunnerSsh.isServerAlive('localhost'), 'Local ssh server is not alive.')
	def testSubmitNRun(self, job, ret, outs = [], errs = []):
		RunnerSsh.INTERVAL = .1
		r = RunnerSsh(job)
		r.submit()
		with helpers.log2str():
			o = r.run()
		self.assertEqual(o, ret)
		stdout = helpers.readFile(job.outfile, str)
		stderr = helpers.readFile(job.errfile, str)
		for o in outs:
			self.assertIn(o, stdout)
		for e in errs:
			self.assertIn(e, stderr)

class TestRunnerSge(testly.TestCase):

	def setUpMeta(self):
		self.testdir = path.join(gettempdir(), 'PyPPL_unittest', 'TestRunnerSge')
		if path.exists(self.testdir):
			rmtree(self.testdir)
		makedirs(self.testdir)
	
	def dataProvider_testInit(self):
		yield _generateJob(
			self.testdir,
			pProps = {
				'sgeRunner': {
					'sge.N': 'SgeJobName',
					'sge.q': 'queue',
					'sge.j': 'y',
					'sge.o': path.join(self.testdir, 'stdout'),
					'sge.e': path.join(self.testdir, 'stderr'),
					'sge.M': 'xxx@abc.com',
					'sge.m': 'yes',
					'sge.mem': '4G',
					'sge.notify': True,
					'preScript': 'alias qsub="%s"' % (path.join(__folder__, 'mocks', 'qsub')),
					'postScript': ''
				}
			}
		), 'SgeJobName', path.join(self.testdir, 'stdout'), path.join(self.testdir, 'stderr')
		
		yield _generateJob(
			self.testdir,
			index  = 1,
			pProps = {
				'sgeRunner': {
					'sge.q': 'queue',
					'sge.j': 'y',
					'sge.M': 'xxx@abc.com',
					'sge.m': 'yes',
					'sge.mem': '4G',
					'sge.notify': True,
					'preScript': 'alias qsub="%s"' % (path.join(__folder__, 'mocks', 'qsub')),
					'postScript': ''
				}
			}
		),
		
	def testInit(self, job, jobname = None, outfile = None, errfile = None):
		self.maxDiff = None
		r = RunnerSge(job)
		self.assertIsInstance(r, RunnerSge)
		self.assertTrue(path.exists(job.script + '.sge'))
		helpers.assertTextEqual(self, helpers.readFile(job.script + '.sge', str), '\n'.join([
			"#!/usr/bin/env bash",
			'#$ -N %s' % (jobname if jobname else '.'.join([
				job.proc.id,
				job.proc.tag,
				job.proc._suffix(),
				str(job.index + 1)
			])),
			'#$ -q queue',
			'#$ -j y',
			'#$ -o %s' % (outfile if outfile else job.outfile),
			'#$ -e %s' % (errfile if errfile else job.errfile),
			'#$ -cwd',
			'#$ -M xxx@abc.com',
			'#$ -m yes',
			'#$ -mem 4G',
			'#$ -notify',
			'',
			'trap "status=\\$?; echo \\$status >\'%s\'; exit \\$status" 1 2 3 6 7 8 9 10 11 12 15 16 17 EXIT' % job.rcfile,
			'alias qsub="%s"' % (path.join(__folder__, 'mocks', 'qsub')),
			'',
			job.script,
			'',
			''
		]))
		
	def dataProvider_testGetpid(self):
		job = _generateJob(
			self.testdir,
			pProps = {
				'sgeRunner': {
					'qsub': path.join(__folder__, 'mocks', 'qsub'),
					'qstat': path.join(__folder__, 'mocks', 'qstat'),
					'qdel': path.join(__folder__, 'mocks', 'qdel'),
					'preScript': '',
					'postScript': ''
				}
			}
		)
		helpers.writeFile(job.script, '\n'.join([
			'#!/usr/bin/env bash',
			'%s %s' % (
				# remove the pid after job id done
				path.join(__folder__, 'mocks', 'qsub_done'),
				#str(int(md5(str(job.script) + '.sge').hexdigest()[:8], 16))
				int(md5((job.script + '.sge').encode('utf-8')).hexdigest()[:8], 16)
			)
		]))
		yield job, 
		
	def testGetpid(self, job):
		r = RunnerSge(job)
		r.submit()
		# self.assertIn(helpers.readFile(job.pidfile, str), helpers.readFile(job.outfile, str))
		self.assertTrue(path.isfile(job.pidfile))
		
	def dataProvider_testIsRunning(self):
		job = _generateJob(
			self.testdir,
			pProps = {
				'expect': TemplateLiquid(''),
				'echo': {'jobs': [0], 'type': {'stdout': None}},
				'sgeRunner': {
					'qsub': path.join(__folder__, 'mocks', 'qsub'),
					'qstat': path.join(__folder__, 'mocks', 'qstat'),
					'preScript': '',
					'postScript': ''
				}
			}
		)
		helpers.writeFile(job.script, '\n'.join([
			'sleep .1',
			'touch %s' % job.outfile,
			'touch %s' % job.errfile,
			'%s %s' % (
			 	path.join(__folder__, 'mocks', 'qsub_done'),
			 	int(md5((job.script + '.sge').encode('utf-8')).hexdigest()[:8], 16)
			)
		]))
		# 0
		yield job,
		
		job1 = _generateJob(
			self.testdir,
			index = 1,
			pProps = {
				'expect': TemplateLiquid(''),
				'echo': {'jobs': [0], 'type': {'stdout': None}},
				'sgeRunner': {
					'qsub': path.join(__folder__, 'mocks', 'qsub'),
					'qstat': '__command_not_exists__',
					'preScript': '',
					'postScript': ''
				}
			}
		)
		helpers.writeFile(job1.script, '\n'.join([
			'#!/usr/bin/env bash',
			'sleep .1',
			'touch %s' % job1.outfile,
			'touch %s' % job1.errfile,
			'%s %s' % (
				path.join(__folder__, 'mocks', 'qsub_done'),
				int(md5((job1.script + '.sge').encode('utf-8')).hexdigest()[:8], 16)
			)
		]))
		# 1
		yield job1, False, False, False

		job2 = _generateJob(
			self.testdir,
			index = 2,
			pProps = {
				'expect': TemplateLiquid(''),
				'echo': {'jobs': [0], 'type': {'stdout': None}},
				'sgeRunner': {
					'qsub': '__command_not_exists__',
					'qstat': '__command_not_exists__',
					'preScript': '',
					'postScript': ''
				}
			}
		)
		helpers.writeFile(job2.script, '\n'.join([
			'#!/usr/bin/env bash',
			'sleep .1',
			'touch %s' % job2.outfile,
			'touch %s' % job2.errfile,
			'%s %s' % (
				path.join(__folder__, 'mocks', 'qsub_done'),
				int(md5((job2.script + '.sge').encode('utf-8')).hexdigest()[:8], 16)
			)
		]))
		# 2
		yield job2, False, False, False
		
	def testIsRunning(self, job, beforesub = False, aftersub = True, afterrun = False):
		RunnerSge.INTERVAL = .2
		r = RunnerSge(job)
		self.assertEqual(r.isRunning(), beforesub)
		if r.submit():
			self.assertEqual(r.isRunning(), aftersub)
			with helpers.log2str():
				r.run()
			self.assertEqual(r.isRunning(), afterrun)


class TestRunnerSlurm(testly.TestCase):

	def setUpMeta(self):
		self.testdir = path.join(gettempdir(), 'PyPPL_unittest', 'TestRunnerSlurm')
		if path.exists(self.testdir):
			rmtree(self.testdir)
		makedirs(self.testdir)
	
	def dataProvider_testInit(self):
		yield _generateJob(
			self.testdir,
			pProps = {
				'slurmRunner': {
					'slurm.J': 'SlurmJobName',
					'slurm.q': 'queue',
					'slurm.j': 'y',
					'slurm.o': path.join(self.testdir, 'stdout'),
					'slurm.e': path.join(self.testdir, 'stderr'),
					'slurm.M': 'xxx@abc.com',
					'slurm.m': 'yes',
					'slurm.mem': '4G',
					'slurm.notify': True,
					'cmdPrefix': 'srun prefix',
					'preScript': 'alias srun="%s"' % (path.join(__folder__, 'mocks', 'srun')),
					'postScript': ''
				}
			}
		), 'SlurmJobName', path.join(self.testdir, 'stdout'), path.join(self.testdir, 'stderr')
		
		yield _generateJob(
			self.testdir,
			index  = 1,
			pProps = {
				'slurmRunner': {
					'slurm.q': 'queue',
					'slurm.j': 'y',
					'slurm.M': 'xxx@abc.com',
					'slurm.m': 'yes',
					'slurm.mem': '4G',
					'slurm.notify': True,
					'cmdPrefix': 'srun prefix',
					'preScript': 'alias srun="%s"' % (path.join(__folder__, 'mocks', 'srun')),
					'postScript': ''
				}
			}
		),
		
	def testInit(self, job, jobname = None, outfile = None, errfile = None):
		self.maxDiff = None
		r = RunnerSlurm(job)
		self.assertIsInstance(r, RunnerSlurm)
		self.assertTrue(path.exists(job.script + '.slurm'))
		helpers.assertTextEqual(self, helpers.readFile(job.script + '.slurm', str), '\n'.join([
			"#!/usr/bin/env bash",
			'#SBATCH -J %s' % (jobname if jobname else '.'.join([
				job.proc.id,
				job.proc.tag,
				job.proc._suffix(),
				str(job.index + 1)
			])),
			'#SBATCH -o %s' % (outfile if outfile else job.outfile),
			'#SBATCH -e %s' % (errfile if errfile else job.errfile),
			'#SBATCH -M xxx@abc.com',
			'#SBATCH -j y',
			'#SBATCH -m yes',
			'#SBATCH --mem 4G',
			'#SBATCH --notify',
			'#SBATCH -q queue',
			'',
			'trap "status=\\$?; echo \\$status >\'%s\'; exit \\$status" 1 2 3 6 7 8 9 10 11 12 15 16 17 EXIT' % job.rcfile,
			'alias srun="%s"' % (path.join(__folder__, 'mocks', 'srun')),
			'',
			'srun prefix ' + job.script,
			'',
			''
		]))
		
	def dataProvider_testGetpid(self):
		job = _generateJob(
			self.testdir,
			pProps = {
				'echo': {'jobs': [0]},
				'slurmRunner': {
					'sbatch': path.join(__folder__, 'mocks', 'sbatch'),
					'squeue': path.join(__folder__, 'mocks', 'squeue'),
					'srun': path.join(__folder__, 'mocks', 'srun'),
					'scancel': path.join(__folder__, 'mocks', 'scancel'),
					'preScript': 'alias srun="%s"' % (path.join(__folder__, 'mocks', 'srun')),
					'postScript': ''
				}
			}
		)
		helpers.writeFile(job.script, '\n'.join([
			'touch %s' % job.outfile,
			'touch %s' % job.errfile,
			'%s %s' % (
				# remove the pid after job id done
				path.join(__folder__, 'mocks', 'sbatch_done'),
				#str(int(md5(str(job.script) + '.sge').hexdigest()[:8], 16))
				int(md5((job.script + '.slurm').encode('utf-8')).hexdigest()[:8], 16)
			)
		]))
		yield job, True
		
		job1 = _generateJob(
			self.testdir,
			index = 1,
			pProps = {
				'echo': {'jobs': [0]},
				'slurmRunner': {
					'sbatch': path.join(__folder__, 'mocks', 'sbatch'),
					'squeue': path.join(__folder__, 'mocks', 'squeue'),
					'srun': path.join(__folder__, 'mocks', 'srun'),
					'preScript': 'alias srun="%s"' % (path.join(__folder__, 'mocks', 'srun')),
					'postScript': 'echo >\'%s\'' % (path.join(self.testdir, 'p', 'workdir', '2', 'job.pid'))
				}
			}
		)
		yield job1, True

		job2 = _generateJob(
			self.testdir,
			index = 2,
			pProps = {
				'echo': {'jobs': [0]},
				'slurmRunner': {
					'sbatch': path.join(__folder__, 'mocks', 'sbatch'),
					'squeue': path.join(__folder__, 'mocks', 'squeue'),
					'srun': path.join(__folder__, 'mocks', 'srun'),
					'preScript': 'alias srun="%s"' % (path.join(__folder__, 'mocks', 'srun')),
					'postScript': 'echo >\'%s\'' % (path.join(self.testdir, 'p', 'workdir', '3', 'job.pid'))
				}
			}
		)
		helpers.writeFile(job2.script, '\n'.join([
			'echo Hello world! > "%s"' % job2.outfile, 
			'echo Hello world! > "%s"' % job2.errfile 
		]))
		yield job2,
		
	def testGetpid(self, job, pid = None):
		r = RunnerSlurm(job)
		r.submit()
		if pid:
			#self.assertIn(helpers.readFile(job.pidfile, str), helpers.readFile(job.outfile, str))
			self.assertTrue(path.isfile(job.pidfile))
		else:
			r.run()
			self.assertIsNone(r.getpid())

		
	def dataProvider_testIsRunning(self):
		job = _generateJob(
			self.testdir,
			pProps = {
				'expect': TemplateLiquid(''),
				'echo': {'jobs': [0], 'type': {'stdout': None}},
				'slurmRunner': {
					'sbatch': path.join(__folder__, 'mocks', 'sbatch'),
					'squeue': path.join(__folder__, 'mocks', 'squeue'),
					'srun': path.join(__folder__, 'mocks', 'srun'),
					'preScript': '',
					'postScript': ''
				}
			}
		)
		helpers.writeFile(job.script, '\n'.join([
			'#!/usr/bin/env bash',
			'sleep .1',
			'touch %s' % job.outfile,
			'touch %s' % job.errfile,
			'%s %s' % (
				path.join(__folder__, 'mocks', 'sbatch_done'),
				int(md5((job.script + '.slurm').encode('utf-8')).hexdigest()[:8], 16)
			)
		]))
		yield job,
		
		job1 = _generateJob(
			self.testdir,
			index = 1,
			pProps = {
				'expect': TemplateLiquid(''),
				'echo': {'jobs': [0], 'type': {'stdout': None}},
				'slurmRunner': {
					'sbatch': path.join(__folder__, 'mocks', 'sbatch'),
					'squeue': '__command_not_exists__',
					'srun': path.join(__folder__, 'mocks', 'srun'),
					'postScript': ''
				}
			}
		)
		helpers.writeFile(job1.script, '\n'.join([
			'#!/usr/bin/env bash',
			'sleep .1',
			'touch %s' % job1.outfile,
			'touch %s' % job1.errfile,
			'%s %s' % (
				path.join(__folder__, 'mocks', 'sbatch_done'),
				int(md5((job1.script + '.slurm').encode('utf-8')).hexdigest()[:8], 16)
			)
		]))
		yield job1, False, False, False
		
		job2 = _generateJob(
			self.testdir,
			index = 2,
			pProps = {
				'expect': TemplateLiquid(''),
				'echo': {'jobs': [0], 'type': {'stdout': None}},
				'slurmRunner': {
					'sbatch': '__command_not_exists__',
					'squeue': path.join(__folder__, 'mocks', 'squeue'),
					'srun': path.join(__folder__, 'mocks', 'srun'),
					'postScript': ''
				}
			}
		)
		helpers.writeFile(job2.script)
		yield job1, False, False, False
		
	def testIsRunning(self, job, beforesub = False, aftersub = True, afterrun = False):
		RunnerSlurm.INTERVAL = .2
		r = RunnerSlurm(job)
		job.proc.echo = {'job':0, 'type':{'stdout': None, 'stderr': None}}
		self.assertEqual(r.isRunning(), beforesub)
		r.submit()
		self.assertEqual(r.isRunning(), aftersub)
		with helpers.log2str():
			r.run()
		self.assertEqual(r.isRunning(), afterrun)


if __name__ == '__main__':
	clearMockQueue()
	testly.main(verbosity=2, failfast = True)
