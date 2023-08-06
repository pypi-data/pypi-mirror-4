import sys
import argparse
import subprocess

class Parser(argparse.ArgumentParser):
	def __init__(self, desc):
		argparse.ArgumentParser.__init__(self, description=desc)
	
	def add(self, *a, **kw):
		self.add_argument(*a, **kw)

# Print without newline
def write(s):
	sys.stdout.write(s)

# Run command in shell
def run(c):
	command = c.split()
	subprocess.call(command)
