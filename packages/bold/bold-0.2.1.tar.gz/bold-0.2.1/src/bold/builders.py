import subprocess
import os
import re
import logging
from bold import util
import bold
import sys
import errno
import collections


logger = logging.getLogger(__name__)


_registered_builders = []

class BuilderMeta (type):
	def __init__ (class_, name, bases, attrs):
		super(BuilderMeta, class_).__init__(name, bases, attrs)
		if not attrs.get('abstract'):
			_registered_builders.append(class_)

class Builder (object):
	__metaclass__ = BuilderMeta
	abstract = True

	required_by = None

	def __init__ (self, db, build_path):
		self._db = db
		self.build_path = build_path  #TODO optional for class-lavel assigning?

		self._tmp_files = set()
		self._tmp_deps = collections.defaultdict(set)

	def _process_deps (self, force_rebuild = False):
		changed_targets = set()

		def on_changed (path, changed_targets=changed_targets):
			# print path
			# print self._tmp_deps[path]
			changed_targets |= self._tmp_deps[path]

		old_files = self._db.get(self.__class__.__name__ + 'files', {})
		# print old_files
		old_deps = self._db.get(self.__class__.__name__ + 'deps', {})

		cur_files = {}
		# print self._tmp_deps
		for path in self._tmp_files:
			# print path
			try:
				cur_size = os.stat(path).st_size
				cur_hash = util.file_hash(path)
				cur_files[path] = {'size': cur_size, 'hash': cur_hash}
			except OSError as e:
				if e.errno == errno.ENOENT:
					on_changed(path)
				else:
					raise
			else:
				old_file = old_files.get(path)
				if force_rebuild or (not old_file) or (old_file['size'] != cur_size) or (old_file['hash'] != cur_hash):
					on_changed(path)

		if changed_targets:
			self._db[self.__class__.__name__ + 'files'] = cur_files #TODO no need for ns here?
			self._db[self.__class__.__name__ + 'deps'] = self._tmp_deps

		return changed_targets

	def _set_dep (self, target_path, source_paths, is_external = False):
		target_path = self.resolve(target_path)
		source_paths = map(self.resolve, source_paths)

		if not is_external:
			self._tmp_files.add(target_path)
		self._tmp_files |= set(source_paths)

		# if not is_external:
		self._tmp_deps[target_path].add(target_path)
		for path in source_paths:
			self._tmp_deps[path].add(target_path)

		return self

	def _update_target (self, path):
		path = self.resolve(path)

		fs = self._db[self.__class__.__name__ + 'files']
		fs[path]= {'size': os.stat(path).st_size, 'hash': util.file_hash(path)}
		self._db[self.__class__.__name__ + 'files'] = fs
		return self

	def build (self, changed_targets, src_paths):
		raise NotImplementedError("Abstract method")

	def shell_run (self, cmd, return_status = False):
		cmd = self.resolve(cmd)
		logger.info(cmd)
		(subprocess.call if return_status else subprocess.check_call)(cmd, shell = True)

	def resolve (self, path):
		return (path._path if isinstance(path, bold.Lazy_build_path) else path).format(build_path = self.build_path)

	def handle_dependencies (self, actual_src_paths):
		self._set_dep(self.target, actual_src_paths)
		if self.required_by:
			self._set_dep(self.required_by.__func__() if callable(self.required_by) else self.required_by,
				[self.target] + actual_src_paths,
				is_external = True)

DEP_RE = re.compile(r': | \\\s+|\s+')

def _compile (compiler, source_file_path, o_file_path, compile_flags, includes):
	cmd = ' '.join([
		compiler, '-c',
		'-o', o_file_path,
		compile_flags,
		' '.join('-I%s' % p for p in includes),
		source_file_path,
	])
	logger.info(cmd)
	return subprocess.call(cmd, shell = True)

def _link (compiler, exe_path, o_file_paths, lib_paths, libs, link_flags):
	cmd = ' '.join([
		compiler,
		'-o', exe_path,
		' '.join(o_file_paths),
		link_flags,
		' '.join('-L%s' % p for p in lib_paths),
		' '.join('-l%s' % n for n in libs),
	])
	logger.info(cmd)
	return subprocess.call(cmd, shell = True)

def _src_to_o (src_path, build_path):
	src_fname, _ext = os.path.splitext(os.path.basename(src_path))
	return build_path + src_fname + '.o'

class CProgram (Builder):
	abstract = True

	sources = None #TODO declaration-level check
	includes = []
	compile_flags = ''
	link_flags = ''
	libs = []
	lib_paths = []
	compiler = 'cc'
	target = 'run'

	def _get_deps (self, source_file_path):
		#note: don't forget to use quotes for headers when needed (http://gcc.gnu.org/bugzilla/show_bug.cgi?id=42921)
		dep_file_path = 'dep.d'
		cmd = ' '.join([
			self.compiler, '-MM -MF',
			dep_file_path,
			' '.join('-I%s' % p for p in [self.resolve(p() if callable(p) else p) for p in self.includes]),
			self.compile_flags,  #TODO need?
			source_file_path,
		])
		# logger.debug(cmd)
		subprocess.check_call(cmd, shell = True)
		try:
			with open(dep_file_path) as f:
				c = f.read().strip()
				# print c
		finally:
			os.remove(dep_file_path)

		parts = DEP_RE.split(c)
		_o_file_name = parts[0]
		dep_paths = parts[1:]
		return dep_paths
	
	def handle_dependencies (self, actual_src_paths):
		o_paths = []
		o_deps_all = []
		for src_path in actual_src_paths:
			o_path = _src_to_o(src_path, self.build_path)
			o_deps = self._get_deps(src_path)
			o_deps_all += o_deps
			self._set_dep(o_path, o_deps)
			o_paths.append(o_path)
		self._set_dep(self.target, o_paths + actual_src_paths + o_deps_all)
		# print self._tmp_deps

	def build (self, changed_targets, src_paths):
		o_paths = []
		for src_path in src_paths:
			o_path = _src_to_o(src_path, self.build_path)
			o_paths.append(o_path)
			if o_path in changed_targets:
				_compile(self.compiler, src_path, o_path, self.compile_flags,
					[self.resolve(p() if callable(p) else p) for p in self.includes]) and sys.exit(1)
				self._update_target(o_path)

		exe_path = self.resolve(self.target)
		if exe_path in changed_targets:
			_link(self.compiler, exe_path, o_paths,
				[self.resolve(p() if callable(p) else p) for p in self.lib_paths], self.libs,
				self.resolve(self.link_flags.__func__() if callable(self.link_flags) else self.link_flags)) and sys.exit(1)
			self._update_target(exe_path)
