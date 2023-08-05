"""
setup packaging script for configuration
"""

import os

version = "0.3.1"
dependencies = ['PyYAML']

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
      configuration-template = configuration.template:main
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


setup(name='configuration',
      version=version,
      description="multi-level unified configuration",
      long_description=description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Jeff Hammel',
      author_email='jhammel@mozilla.com',
      url='http://k0s.org/mozilla/hg/configuration',
      license='MPL',
      packages=['configuration'],
      include_package_data=True,
      zip_safe=False,
      **kw
      )
