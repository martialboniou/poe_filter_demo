#!/usr/bin/env python3
# -*- coding: utf-8 -*-
program_name = 'py2exe'

import platform
if platform.system() != 'Windows':
	print('This script works on Windows only')
	exit(1)

import sys
if not sys.argv[1:]:
	print("""usage: python standalone.py (<attach-python-dll>) <files>
with:
     <attach-python-dll>: optional (implicit default is 0)
                          0 for an executable using the local python dll (default)
                          1 for a standalone binary (recommended if shared)
     <files>: one or more python scripts' filenames to convert
              (the extension '.py' is not required)""")

import importlib
try:
	importlib.import_module(program_name)
except:
	print('Please install py2exe first...')
	exit(1)

from distutils.core import setup
from os import access, R_OK
import os.path
import shutil

if __name__ == "__main__":
	try:
		 standalone = int(sys.argv[1])
	except ValueError:
		standalone = 0
	else:
		del(sys.argv[1])
	if standalone == 0:
		bundle_files = 2
	else:
		bundle_files = 1
	files = sys.argv[1:]
	sys.argv = [sys.argv[0]] + [program_name]
	for f in files:
		if not f.endswith(".py"):
			f += ".py"
		if not access(f, R_OK):
			print('{0} not found'.format(f))
			continue
		try:
			setup(
				console = [{"script": f}],
				options = {program_name: {"bundle_files": bundle_files, "compressed": True}},
				zipfile = None,
				)
		except:
			print('Error during {0} process with {1}'.format(program_name, f))
		else:
			(root, _) = os.path.splitext(f)
			exe = root + ".exe"
			shutil.move('dist\\'+exe, '.\\'+exe)
			shutil.rmtree('dist')
