#!/usr/bin/env python
import jhpy_clt as J

VERSION = "1.0.3"
DESCRIPTION = "JHPY Command-Line Tool"

# Methods
def deploy():
     print "Deploying application..."
def new():
	print "Creating structure template..."
def quick():
	print "Creating quick template..."
def test(p):
	print "Testing at port %s..." % p
def version():
	print VERSION
def default():
  print "Type `jhpy.py -h` to see all the options available."

# Console stuff
parser = J.Parser(DESCRIPTION)

parser.add('-d', '--deploy',
           default=False,
           action="store_true",
           help="deploy your application to google")
parser.add('-n', '--new',
           default=False,
           action="store_true",
           help="create a new structure template")
parser.add('-q', '--quick',
           default=False,
           action="store_true",
           help="create a new quick template")
parser.add('-t', '--test',
           default=False,
           help="start localhost server on port TEST")
parser.add('-v', '--version',
           default=False,
           action="store_true",
           help="get the installed version of jhpy")

# Wrap up
args = parser.parse_args()

if args.deploy:
	deploy()
elif args.new:
	new()
elif args.quick:
	quick()
elif args.test:
	test(args.test)
elif args.version:
	version()
else:
  default()
