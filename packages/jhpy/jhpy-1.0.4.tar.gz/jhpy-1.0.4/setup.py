from distutils.command.build_py import build_py as _build_py
from distutils.core import setup

class build_py(_build_py):
	"""Command-line tool for JHPY."""

setup(name = "jhpy",
      version = "1.0.4",
      url = "https://github.com/djwatt5/jhpy-clt",
      description = "Command-line manager and template builder for JHPY.",
      author = "Daniel Watson",
      author_email = "watsondaniel6@gmail.com",
      py_modules = ["jhpy", "jhpy_clt"],
      scripts = ["jhpy"],
      classifiers = [
      	  'Environment :: Console',
      	  'Environment :: Web Environment',
      	  'Intended Audience :: Developers',
      	  'Programming Language :: Python',
      	  'Topic :: Software Development',
      	  ]
      )
