#!/usr/bin/env python

from distutils.core import setup, Command
from unittest import TextTestRunner
import copy
import os
import sys

package_dir = "lib"
script_dir = "scripts"
test_dir = "tests"
root_dir = os.path.split(os.path.join(os.getcwd(), sys.argv[0]))[0]

class TestCommand(Command):
    """Runs the unit tests"""

    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        sys.path.insert(0, os.path.join(root_dir, package_dir))
        sys.path.insert(0, os.path.join(root_dir, test_dir))
        import all_tests
        t = TextTestRunner(verbosity=2)
        t.run(all_tests.suite())

with open('README.txt') as file:
    long_description = file.read()

setup(name='pyMosaic',
      version='0.1',
      description='MOlecular SimulAtion Interchange Conventions',
      long_description=long_description,
      author='Konrad Hinsen',
      author_email='research@khinsen.fastmail.net',
      url='https://bitbucket.org/molsim/mosaic',
      package_dir = {'': package_dir},
      packages=['mosaic', 'mosaic_pdb'],
      scripts=[os.path.join(script_dir, s) for s in os.listdir(script_dir)],
      cmdclass = {'test': TestCommand},
     )
