from distutils.core import setup

import os
import sys

extra = {}

name = "sqlMagic"
version = "dev"
license = "unknown"
author = "unkown"

with open("sqlmagic.py") as f:
	for line in f.readlines():
		if line.startswith("__version__"):
			version = line.split(" = ")[1].strip("'\"\r\n")
		elif line.startswith("__title__"):
			name = line.split(" = ")[1].strip("'\"\r\n")
		elif line.startswith("__license__"):
			license = line.split(" = ")[1].strip("'\"\r\n")
		elif line.startswith("__author__"):
			author = line.split(" = ")[1].strip("'\"\r\n")

setup(name=name,
      version=version,
      url = 'http://github.com/pyfony/sqlmagic',
      license = license,
      author = author,
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
