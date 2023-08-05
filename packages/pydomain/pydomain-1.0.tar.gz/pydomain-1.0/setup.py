##############################################################################
#
# Copyright (c) 2013 Web Consulting and Contributors.
# All Rights Reserved.
#
##############################################################################

import os
import sys

from setuptools import setup, find_packages

py_version = sys.version_info[:2]

PY3 = py_version[0] == 3

if PY3:
    if py_version < (3, 2):
        raise RuntimeError('On Python 3, Pyramid requires Python 3.2 or better')
else:
    if py_version < (2, 6):
        raise RuntimeError('On Python 2, Pyramid requires Python 2.6 or better')

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

install_requires=[
    'setuptools'
    ]


setup(name='pydomain',
      version='1.0',
      description=('The descusr web application development framework, a '
                   'Pylons project'),
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "License :: Repoze Public License",
        ],
      keywords='get domain, get host, get subdomain',
      author="descusr",
      author_email="descusr@163.com",
      url="http://www.piadu.com",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires = install_requires,
      entry_points = """\
      [console_scripts]
      get_host = pydomain.scripts.get_host:main
      get_subdomain = pydomain.scripts.get_subdomain:main
      """
      )

