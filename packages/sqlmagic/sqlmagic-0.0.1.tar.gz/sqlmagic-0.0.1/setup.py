import sqlmagic

from distutils.core import setup

import os
import sys

extra = {}

setup(name=sqlmagic.__name__,
      version=sqlmagic.__version__,
      url = 'http://github.com/pyfony/sqlmagic',
      license = 'BSD',
      author = sqlmagic.__author__,
      author_email = 'pyfony@paars-dev.de',
      description = 'lightweight SQLAlchemy based ORM',
      long_description = "doc: http://docs.paars-dev.de/sqlmagic",
      install_requires = [
          "SQLAlchemy >= 0.7.0", "zope.sqlalchemy"
      ],
      py_modules=[
          "sqlmagic",
      ],
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Apache Software License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3",
          "Topic :: Database :: Front-Ends",
          "Topic :: Software Development :: Libraries :: Python Modules"
      ],
      platforms = 'any',
      **extra)
