"""
setup packaging script for CommandParser
"""

import os

version = "0.2"
dependencies = []

try:
    import json
except ImportError:
    dependencies.append('simplejson')

# allow use of setuptools/distribute or distutils
kw = {}
try:
    from setuptools import setup
    kw['entry_points'] = """
      [console_scripts]
"""
    kw['install_requires'] = dependencies
except ImportError:
    from distutils.core import setup
    kw['requires'] = dependencies

try:
    here = os.path.dirname(os.path.abspath(__file__))
    description = file(os.path.join(here, 'README.txt')).read()
except IOError:
    description = ''


setup(name='CommandParser',
      version=version,
      description="change objects to OptionParser instances via reflection",
      long_description=description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Jeff Hammel',
      author_email='jhammel@mozilla.com',
      url='http://k0s.org/hg/CommandParser',
      license='MPL',
      packages=['commandparser'],
      include_package_data=True,
      zip_safe=False,
      **kw
      )
