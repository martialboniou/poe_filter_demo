#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
try:
	import py2exe
except:
	raw_input('Please install py2exe first...')
import shutil
from distutils.core import setup

sys.argv.append('py2exe')

setup(
		console = [{"script": 'classy_smoother.py'}],
		options = {'py2exe': {"bundle_files": 1, "compressed": True}},
		zipfile = None,
		)

shutil.move('dist\\classy_smoother.exe', '.\\classy_smoother.exe')
shutil.rmtree('dist')
