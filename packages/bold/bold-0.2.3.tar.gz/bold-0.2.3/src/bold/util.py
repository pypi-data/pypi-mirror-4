import contextlib
import os
import errno
import fnmatch
import glob
import imp
import hashlib
import platform
import subprocess
import logging
import sys


USER_MODULE_NAME = 'build'


log = logging.getLogger(__name__)


@contextlib.contextmanager
def change_cwd (path):
	old_dir = os.getcwd()
	os.chdir(path)
	try:
		yield old_dir
	finally:
		os.chdir(old_dir)

def create_dir_recursive (path):
	try:
		os.makedirs(path)
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
	else:
		return path

def get_file_paths_recursive (top_dirname, exclude = None):
	exclude = exclude or []

	for dirname, _dirs, files in os.walk(top_dirname):
		for name in files:
			fpath = os.path.join(dirname, name)
			if not any(fnmatch.fnmatch(fpath, ex) for ex in exclude):
				yield fpath

def lazy_glob (pattern):
	return lambda _self: glob.glob(pattern)

def file_hash (path):
	with open(path, 'rb') as f:
		return hashlib.md5(f.read()).digest()

def load_user_module ():
	# sys.path.append(os.getcwd())
	# import build

	(file, pathname, description) = imp.find_module(USER_MODULE_NAME, [os.getcwd()])
	try:
		module = imp.load_module(USER_MODULE_NAME, file, pathname, description)
	finally:
		if file:
			file.close()

	return module

def is_on_windows ():
	return platform.system().lower() == 'windows'

def is_on_linux ():
	return platform.system().lower() == 'linux'

def preprocess_header (includes, extra_cc_params = ''):
	#TODO make "cc" customizable
	cmd = 'cc -E -dD %s -' % extra_cc_params
	log.info(cmd + "\nInput: " + includes)
	process = subprocess.Popen(cmd, shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE, bufsize = -1)
	output = process.communicate(includes)[0]
	if process.returncode:
		log.error("Process returned %s" % process.returncode)
		sys.exit(1)
	return output