"""
~~~~~~~~~~~~~~~~~~~~~
Nose-Pyversion-Plugin
~~~~~~~~~~~~~~~~~~~~~

"""

import os
import sys
from setuptools import find_packages, setup

# Required for nose.collector, see http://bugs.python.org/issue15881#msg170215
try:
    import multiprocessing
except ImportError:
    pass

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

# Requirements for the package
install_requires = [
    'nose',
]

# Requirement for running tests
test_requires = install_requires

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(name='Nose-PyVersion',
      version='0.1b1',
      description="Nose plugin for excluding files based on python version",
      long_description=README,
      url='http://github.com/danielholmstrom/nose-pyversion/',
      license='MIT',
      author='Daniel Holmstrom',
      author_email='holmstrom.daniel@gmail.com',
      platforms='any',
      classifiers=['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: MIT License',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                   'Topic :: Software Development :: '
                   'Libraries :: Python Modules'],
      py_modules=['nose_pyversion'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=test_requires,
      test_suite='nose.collector',
      entry_points="""
      [nose.plugins]
      pyversion=nose_pyversion:PyVersion
      """,
      **extra
      )
