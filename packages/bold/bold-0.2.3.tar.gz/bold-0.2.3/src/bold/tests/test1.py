import unittest
import bold.util
import subprocess

class Test1 (unittest.TestCase):
	def test_1 (self):
		with bold.util.changed_cwd('src/bold/tests/test1'):
			subprocess.check_call('bold')
