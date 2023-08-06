from settings import *

from distutils.core import setup
from distutils.command.build_py import build_py as _build_py

class build_py(_build_py):
	description

setup(name = name,
      version = version,
      url = url,
      description = description,
      author = author,
      author_email = email,
      py_modules = ["jhpy", "settings"],
      scripts = ["jhpy"],
      classifiers = [
            'Environment :: Console',
      	'Environment :: Web Environment',
      	'Intended Audience :: Developers',
      	'Programming Language :: Python',
      	'Topic :: Software Development',
      	]
      )
