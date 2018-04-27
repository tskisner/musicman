"""Set up musicman
"""

from os import path

import glob

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

import unittest

# Versioneer
import versioneer

here = path.abspath(path.dirname(__file__))

# Starting cmdclass structure from versioneer
cmdcls = versioneer.get_cmdclass()

# Custom test loader

class CustomTestCommand(TestCommand):

    def __init__(self, *args, **kwargs):
        super(CustomTestCommand, self).__init__(*args, **kwargs)

    def initialize_options(self):
        TestCommand.initialize_options(self)

    def finalize_options(self):
        TestCommand.finalize_options(self)
        #self.test_args = []
        self.test_suite = True

    def run(self):
        loader = unittest.TestLoader()
        runner = unittest.TextTestRunner(verbosity=2)
        suite = loader.discover('tests', pattern='test_*.py', top_level_dir='.')
        runner.run(suite)

cmdcls['test'] = CustomTestCommand

scripts = glob.glob('bin/*')

setup(
    name='musicman',
    version=versioneer.get_version(),
    description='Music Management',
    url='https://github.com/tskisner/musicman',
    author='Theodore Kisner',
    author_email='tskisner.public@gmail.com',
    keywords='Music',
    provides=['musicman'],
    requires=['Python (>=3.4.0)'],
    scripts=scripts,
    packages=find_packages(exclude=['docs', 'tests']),  # Required
    cmdclass=cmdcls
)
