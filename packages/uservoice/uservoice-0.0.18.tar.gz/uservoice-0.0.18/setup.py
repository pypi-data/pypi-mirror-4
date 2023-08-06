import os
import sys
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
execfile('uservoice/version.py')

setup(name='uservoice',
      version=__version__,
      description='UserVoice Python library',
      url = 'http://pypi.python.org/pypi/uservoice/',
      long_description=re.sub(r'```[^\s]*', '', open('README.md').read()),
      author='Raimo Tuisku',
      author_email='dev@uservoice.com',
      packages=['uservoice'],
      install_requires=[
          'simplejson',
          'pycrypto',
          'pytz',
          'PyYAML',
          'requests',
          'requests-oauthlib'],
      test_suite='test',
)