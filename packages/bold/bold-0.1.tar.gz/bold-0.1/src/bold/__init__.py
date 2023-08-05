import collections
import os
import errno
import sys
import argparse
import subprocess
import logging
import logging.config
from contextlib import contextmanager
import shelve
import re
import pprint
import fnmatch
from multiprocessing import Pool, cpu_count


DB_FNAME = 'bold_db'


@contextmanager
def change_cwd (path):
	old_dir = os.getcwd()

	os.chdir(path)
	try:
		yield
	finally:
		os.chdir(old_dir)

def init_logging ():
	#https://bitbucket.org/fillest/rss/src/221ede1de22a/src/arss/config.py
	#logging.config.dictConfig(config.logging)
	#log = logging.getLogger(__name__)
	logging.basicConfig(format="%(levelname)-" + str(len('warning') + 2) + "s%(message)s")
	log = logging.getLogger()
	log.setLevel(logging.DEBUG)
	return log

def makedirs (path):
	try:
		os.makedirs(path)
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise

def run (cmd, dry, log):
	log.info("run: " + cmd)

	if not dry:
		if subprocess.call(cmd, shell=True):
			log.error("fail")
			sys.exit(1)

def clean (db, log, dry):
	log.info("clean")

	clean = db.get('clean', set())
	for path in clean:
		log.info("remove " + path)
		if not dry:
			try:
				os.remove(path)
			except OSError as e:
				if e.errno == errno.ENOENT:
					log.warn('failed to remove "%s" - file not found' % path)
				else:
					raise
	if not dry:
		db['clean'] = set()

class Builder (object):
	def __init__ (self):
		self._builders = []
		self.opts = None

	def _init_parser (self):
		parser = argparse.ArgumentParser()

		#parser.add_argument('params', nargs='*')
		parser.add_argument('--dry', '-d', dest='dry', action='store_true')
		parser.add_argument('--clean', '-c', dest='clean', action='store_true')
		parser.add_argument('--reset', '-r', dest='reset', action='store_true', help="remove Bold db")
		parser.add_argument('--deps', action='store_true', help="show stored dependencies and exit")

		self.add_options(parser)

		self.opts = parser.parse_args()

	def task (self, builder_class):
		self._builders.append(builder_class)
		return builder_class

	def run (self, build_dir):
		makedirs(build_dir)

		log = init_logging()

		self._init_parser()

		db_filename = DB_FNAME
		if self.opts.reset:
			os.remove(db_filename)
		else:
			PICKLE_PROTOCOL = 2
			db = shelve.open(db_filename, protocol = PICKLE_PROTOCOL)
			try:
				if self.opts.clean:
					clean(db, log, self.opts.dry)
				else:
					build(db, log, self.opts.dry, build_dir, self._builders, self.opts.deps)
			finally:
				db.close()

	def add_options (self, parser):
		pass

class Deps (object):
	def __init__ (self):
		self._deps = {}

	def add (self, target, source, builder):
		dep = self._deps.get(target)
		if not dep:
			dep = self._deps[target] = {
				'sources': set(),
				'modified': True,
			}

		if dep['modified']:
			s = os.stat(target)
			dep['mtime'] = s.st_mtime
			dep['size'] = s.st_size
			dep['modified'] = False

		dep['sources'].add((source, builder.__class__))

	def mark_modified (self, target):
		self._deps[target]['modified'] = True


def _build_exe (libs, build_dir, exe_name, obj_fpaths, flags, libpaths, dry, log, clean):
	libs_s = ' '.join('-l' + n for n in libs)
	exe_path = '{build_dir}/{exe_name}'.format(
		build_dir = build_dir,
		exe_name = exe_name,
	)
	cmd = 'gcc -o {exe_path} {flags} {objs} {libpaths} {libs}'.format(
		libs = libs_s,
		objs = ' '.join(obj_fpaths),
		exe_path = exe_path,
		flags = flags,
		libpaths = ' '.join('-L%s' % p for p in libpaths),
	)
	run(cmd, dry, log)
	clean.append(exe_path)



#import time
#def fn(x):
#	print x
#	time.sleep(3)
#	return "%s%s" % (x, x)

class ProgramBuilder (object):
	def build (self, build_dir, clean, dry, log, deps, targets):
		exe_fpath = getattr(self, 'target') #todo friendly error

		obj_fpaths = []

		#~ pool = Pool(processes = cpu_count())
		#~ for r in pool.imap_unordered(fn, range(10)):
			#~ print r
		#~ print "end"
		#~ sys.exit()

		#TODO order doesnt matter, parallelize
		filepaths = getattr(self, 'source') #todo friendly error
		for src_fpath in filepaths:
			src_name, ext = os.path.splitext(os.path.basename(src_fpath))

			if ext == '.c':
				#http://gcc.gnu.org/onlinedocs/gcc-4.5.2/gcc/Preprocessor-Options.html
				obj_fpath = '%s/%s.o' % (build_dir, src_name)
				obj_fpaths.append(obj_fpath)
				if (not targets) or obj_fpath in targets:
					cmd_compile = 'gcc -c -MMD -o {obj_path} {includes} {flags} {src_fpath}'.format(
						obj_path = obj_fpath,
						src_fpath = src_fpath,
						includes = ' '.join('-I%s' % i for i in getattr(self, 'includes', [])),
						flags = getattr(self, 'flags', ''),
					)
					run(cmd_compile, dry, log)

					clean.append(obj_fpath)

					deps.add(obj_fpath, obj_fpath, self)

					dep_fpath = build_dir + '/' + src_name + '.d'
					clean.append(dep_fpath)
					if not dry:
						with open(dep_fpath) as f:
							c = f.read().strip()
						paths = re.split(r': | \\\s+|\s+', c)
						o = paths[0]
						for p in paths[1:]:
							deps.add(p, o, self)
			elif ext == '.txt':
				deps.add(src_fpath, exe_fpath, self)
			else:
				raise NotImplementedError("Handling of '%s' files is not implemented (yet?)" % ext)

		if (not targets) or exe_fpath in targets:
			libs = getattr(self, 'libs', [])
			exe_flags = getattr(self, 'exe_flags', '')
			libpaths = getattr(self, 'libpaths', [])
			_build_exe(libs, build_dir, os.path.basename(exe_fpath), obj_fpaths, exe_flags, libpaths, dry, log, clean)
			for p in obj_fpaths:
				deps.add(p, exe_fpath, self)


def build (db, log, dry, build_dir, builders, do_list_deps):
	deps = db.get('deps', Deps())  #TODO if class changed, we get AttributeError: 'module' object has no attribute 'ProgramBuilder'
	if do_list_deps:
		pprint.pprint(deps._deps) #todo
		sys.exit(0)


	log.info("build all")

	clean_fpaths = []
	try:
		modified_builders = collections.defaultdict(set)
		used_builders = set()
		def proc_dep (target, modified = False):
			state = deps._deps[target]
			for _source, builder in state['sources']:
				used_builders.add(builder)

			try:
				s = os.stat(target)
			except OSError as e:
				if e.errno == errno.ENOENT:
					modified = True
				else:
					raise
			if modified or s.st_mtime != state['mtime'] or s.st_size != state['size']:
				modified = True

			if modified:
				#print "***", target, state['sources']
				deps.mark_modified(target)

				for source, builder in state['sources']:
					modified_builders[builder].add(source)
					if source in deps._deps and source != target:
						proc_dep(source, True)
		for target in deps._deps:
			proc_dep(target)

		#+reset modified builders somehow to drop garbage?


		all_builders = set(builders)
		unused_builders = all_builders - used_builders
		for builder in unused_builders:
			modified_builders[builder] = modified_builders.default_factory()


		#print "-->", modified_builders
		def cmp ((b1, _s1), (b2, _s2)):
			r1 = getattr(b1, 'require', [])
			if not isinstance(r1, list):
				r1 = [r1]
			r2 = getattr(b2, 'require', [])
			if not isinstance(r2, list):
				r2 = [r2]

			if b2 in r1: #b1 requires b2
				return 1
			elif b1 in r2:
				return -1
			else:
				return 0

		#TODO make graph and parallelize
		bs = sorted(modified_builders.iteritems(), cmp=cmp)
		if bs:
			for builder, targets in bs:
				builder().build(build_dir, clean_fpaths, dry, log, deps, targets)
		else:
			log.info("nothing changed")

#		pprint.pprint(deps._deps)

		#+dep script self

		db['deps'] = deps
	finally:
		if not dry:
			dclean = db.get('clean', set())
			dclean |= set(clean_fpaths)
			db['clean'] = dclean

def recursive_list_files (top_dirname, exclude=None):
	exclude = exclude or []

	for dirname, _dirs, files in os.walk(top_dirname):
		for name in files:
			fpath = os.path.join(dirname, name)
			if not any(fnmatch.fnmatch(fpath, ex) for ex in exclude):
				yield fpath

class LuajitBuilder (object):
	install_dir = None
	src_dir = 'src/luajit'

	def build (self, _build_dir, clean, dry, log, deps, _targets):
		log.info("build luajit")

		with change_cwd(self.src_dir):
			cmd = "make amalg CCDEBUG=' -g' BUILDMODE=' dynamic' PREFIX={prefix} && make install PREFIX={prefix}".format(prefix = self.install_dir)
			log.info("running: " + cmd)
			fail = subprocess.call(cmd, shell=True)

			subprocess.call(['make', 'clean'])

			if fail:
				sys.exit(1)

			out_fpath = self.install_dir + '/lib/libluajit-5.1.so'
			assert os.path.isfile(out_fpath)

			#clean.append(out_fpath)

		for fpath in recursive_list_files(self.src_dir, [self.src_dir + '/doc/*']):
			deps.add(fpath, out_fpath, self)
		deps.add(out_fpath, None, self)
		#its .so so we don't rebuild exe on change
