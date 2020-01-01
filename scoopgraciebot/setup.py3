#!/usr/bin/env python3
import sys,os,re,json

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if os.path.exists(os.getenv("HOME") + '/scoopgraciebot'):
	eprint('error: lock file ~/scoopgraciebot already exists')
	exit(1)
	
export=open(os.getenv("HOME") + '/scoopgraciebot.json', 'w+')
open(os.getenv("HOME") + '/scoopgraciebot', 'w+').close()

regex = re.compile(
	r'^(?:http)s?://' # http:// or https://
	r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
	r'localhost|' #localhost...
	r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
	r'(?::\d+)?' # optional port
	r'(?:/?|[/?]\S+)$', re.IGNORECASE)

if len(sys.argv) is not 2:
	eprint("error: exactly one argument required. usage:")
	eprint(sys.argv[0] + " <url>")
	os.unlink(os.getenv("HOME") + '/scoopgraciebot')
	exit(1);

if re.match(regex, sys.argv[1]) is None:
	eprint("error: argument 1 must be a valid URL. usage:")
	eprint(sys.argv[0] + " <url>")
	os.unlink(os.getenv("HOME") + '/scoopgraciebot')
	exit(1);

json.dump({"queue":[sys.argv[1]], "crawled": [], "webMap":{}}, export)
os.unlink(os.getenv("HOME") + '/scoopgraciebot')
	
print('done.')
