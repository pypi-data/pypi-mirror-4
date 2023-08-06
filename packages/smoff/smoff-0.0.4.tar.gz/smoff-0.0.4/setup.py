#!/usr/bin/env python2

from distutils.core import setup

from distutils.core import Command
from unittest import TextTestRunner, TestLoader
from glob import glob
from os.path import splitext, basename, join as pjoin, walk
import os

class TestCommand(Command):
    user_options = [ ]

    def initialize_options(self):
        self._dir = os.getcwd()

    def finalize_options(self):
        pass

    def run(self):
        '''
        Finds all the tests modules in tests/, and runs them.
        '''
        testfiles = [ ]
        for t in glob(pjoin(self._dir, 'tests', '*.py')):
            if not t.endswith('__init__.py'):
                testfiles.append('.'.join(
                    ['tests', splitext(basename(t))[0]])
                )

        tests = TestLoader().loadTestsFromNames(testfiles)
        t = TextTestRunner(verbosity = 1)
        t.run(tests)

setup(name='smoff', version='0.0.4', description='Wicket-inspired template engine for python/django', author='Michael Donaghy', author_email='michael@optimalsocial.com', url='https://bitbucket.org/lmm/smoff', packages=['smoff'],
 requires=['lxml', 'django'],
 cmdclass = { 'test': TestCommand,}
 
 )
