#!/usr/bin/env python


from __future__ import print_function
from distutils.core import setup, Extension, Command
import os
import os.path
import glob
import sys
import shutil


class _TestCommand(Command):
    user_options = []

    def initialize_options(self):
        self._dir = os.getcwd()

    def finalize_options(self):
        pass

    def run(self):
        try:
            os.chdir('tests')
            run_str = '%s __init__.py' % ('python3' if sys.version_info.major >= 3 else 'python')
            os.system(run_str)
        finally:       
            os.chdir('..')


setup(
    name = 'UnittestRandGenState',
    version = '0.1.2',
    author = 'Ami Tavory',
    author_email = 'atavory at gmail.com',
    packages = ['unittest_rand_gen_state'],
    url = 'http://pypi.python.org/pypi/UnittestRandState',
    license = 'BSD',
    description = 'Smart random-generation state persistence for unittest',
    long_description = open('README.txt').read(),
    cmdclass = {
        'test': _TestCommand},
    classifiers = [   
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',  
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing '])
