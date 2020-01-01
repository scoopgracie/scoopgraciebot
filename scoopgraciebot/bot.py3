#!/usr/bin/env python3
import sys,os,re,requests,urllib,json,tempfile,signal,subprocess
from bs4 import BeautifulSoup
dataStore=open(os.getenv("HOME") + '/scoopgraciebot.json', 'r')

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if os.path.exists(os.getenv("HOME") + '/scoopgraciebot'):
	eprint('error: lock file ~/scoopgraciebot already exists')
	exit(1)

open(os.getenv("HOME") + '/scoopgraciebot', 'w+').close()

if not os.path.exists(os.getenv("HOME") + '/scoopgraciebot.json'):
	eprint('error: status file ~/scoopgraciebot.json does not exist')
	exit(1)

#if True:
try:
	jsonData = json.load(dataStore)
	if type(jsonData['queue']) is not list or type(jsonData['crawled']) is not list:
		eprint('error: status file ~/scoopgraciebot.json is not valid')
		exit(1)
except:
	eprint('error: status file ~/scoopgraciebot.json is not valida')
	exit(1)

dataStore.close();

def parseMetas(specific, general):
	units=[]

	for i in general:
		for j in re.findall(r"[\w']+", i):
			if j.lower() == 'nofollow' or j.lower() == 'noindex' or j.lower() == 'follow' or j.lower() == 'index':
				units.append(j.lower())

	for i in specific:
		for j in re.findall(r"[\w']+", i):
			if j.lower() == 'nofollow' or j.lower() == 'follow':
				try:
					units.pop(units.index('follow'))
				except:
					pass

				try:
					units.pop(units.index('nofollow'))
				except:
					pass

				units.append(j.lower())

			if j.lower() == 'noindex' or j.lower() == 'index':
				try:
					units.pop(units.index('index'))
				except:
					pass

				try:
					units.pop(units.index('noindex'))
				except:
					pass

				units.append(j.lower())

	if not 'follow' in units and not 'nofollow' in units:
		units.append('follow')

	if not 'index' in units and not 'noindex' in units:
		units.append('index')

	return units

def parseHeader(header):
	splitHeader = header.split(' ')
	on = True
	units = []
	for i in splitHeader:
		if i is None or i.strip() == '':
			continue

		if i[len(i)-1] == ':':
			on = i.lower() == 'scoopgraciebot:'.lower()
		elif on:
			units.append(re.findall(r"[\w']+", i)[0])
	returnList = ['index', 'follow']
	units.reverse()
	for i in units:
		if i == 'nofollow' or i == 'follow':
			try:
				returnList.pop(returnList.index('nofollow'))
			except:
				pass

			try:
				returnList.pop(returnList.index('follow'))
			except:
				pass
			returnList.append(i)

		if i == 'noindex' or i == 'index':
			try:
				returnList.pop(returnList.index('noindex'))
			except:
				pass

			try:
				returnList.pop(returnList.index('index'))
			except:
				pass
			returnList.append(i)
	return returnList

def parseurl(url, referer):
	try:
		regex = re.compile(
			r'^(?:http)s?://' # http:// or https://
			r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
			r'localhost|' #localhost...
			r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
			r'(?::\d+)?' # optional port
			r'(?:/?|[/?]\S+)$', re.IGNORECASE)
		if url is None or url is '':                           #If the URL is empty,
			return None                                    #Return None.
		elif re.match(regex, url) is not None:                 #If the URL is complete,
			return url                                     #Just return it.
		elif url[0] is '/':                                   
			if len(url) > 1 and url[1] is '/':             #If the URL is protocol-relative,
				temp=urllib.parse.urlparse(referer)    #Get the referer's protocol,
				return temp.scheme + url               #And combine the URLs.
			else:                                          #If the URL is an absolute path without a domain name,
				temp=urllib.parse.urlparse(referer)            #Get the domain of the referer,
				return temp.scheme + '://' + temp.netloc + url #And combine the URLs.
		elif referer[len(url)] is '/':		               #At this point, we know the URL is a
			                                               #relative path.
			                                               #If the referer is a directory,
			return referer + url                           #Just concatenate the referer and URL.
		else:                                                  #Otherwise,
			path = referer.split('/')                      #Split the referer,
			path[len(path) - 1]=url                        #Replace the last section with the URL,
			return '/'.join(path)                          #And concatenate and return the path.
	except:
		return None

headers = {'user-agent': 'Mozilla/5.0 (compatible, ScoopGracieBot 2.0) https://geonavweb.com/scoopgraciebot/'}
queue=jsonData['queue']
crawled=jsonData['crawled']
webMap=jsonData['webMap']
robotses={}

while len(queue) is not 0:

	url=queue.pop(0)

	if url in crawled:
		continue

	req = None

	parsedUrl=urllib.parse.urlparse(url)

	if parsedUrl.scheme + '://' + parsedUrl.netloc in robotses and robotses[parsedUrl.scheme + '://' + parsedUrl.netloc]['num'] < 10:
		robotses[parsedUrl.scheme + '://' + parsedUrl.netloc]['num'] = robotses[parsedUrl.scheme + '://' + parsedUrl.netloc]['num'] + 1
		robots=robotses[parsedUrl.scheme + '://' + parsedUrl.netloc]['text']
	else:
		try:
			req = requests.get(parsedUrl.scheme + '://' + parsedUrl.netloc + '/robots.txt', headers=headers)
			robots = ''
			print('grabbed robots.txt for ' + parsedUrl.scheme + '://' + parsedUrl.netloc)
			if req is not None and req.status_code is 200:
				robots=req.text
		except:
			robots = 'User-Agent: *\nDisallow: /'

		robotses[parsedUrl.scheme + '://' + parsedUrl.netloc]={'text': robots, 'num': 1}

	temp_name = next(tempfile._get_candidate_names())
	robotsf=open('/tmp/' + temp_name, 'w')
	robotsf.write(robots)
	robotsloc = robotsf.name
	robotsf.close()
	path = parsedUrl.path.strip() or '/'
	cmd = './robots ' + robotsloc + ' ScoopGracieBot ' + "'" + path + "'"
	p = subprocess.Popen(cmd, shell=True)
	c = p.wait()
	os.remove(robotsloc)
	if c is 1:
		print("page " + url + " denied in robots.txt")
		continue

	req = None

	try:
		req = requests.get(url, headers=headers)
	except:
		pass

	if req is not None and req.status_code is 200:
		pass
	else:
		eprint("error: invalid url in queue: " + url + " skipping...");
		continue

	if req.url in crawled:
		crawled.append(url)
		continue

	skip = False
	soup = BeautifulSoup(req.text, 'html.parser')
	for link in soup.find_all('link'):
		try:
			if link.get('rel')[0].lower().strip() == "canonical".lower().strip() and not parseurl(link.get('href'), req.url) == req.url and not parseurl(link.get('href'), req.url) == url:
				queue.insert(0, parseurl(link.get('href'), req.url))
				crawled.append(    url)
				crawled.append(req.url)
				skip = True
		except:
			pass

	if skip:
		continue

	if not req.url in webMap:
		webMap[req.url] = {'linksTo': [], 'isLinkedToBy': []}

	crawled.append(    url)
	crawled.append(req.url)

	denied = False
	metaTagsSpecific=[]
	metaTagsGeneral=[]
	for meta in soup.find_all('meta'):
		name=meta.get('name')
		if name is not None and name.lower().strip() == "robots".lower().strip():
			metaTagsGeneral.append(meta.get('content'))
			continue
		if name is not None and name.lower().strip() == "ScoopGracieBot".lower().strip():
			metaTagsSpecific.append(meta.get('content'))
			continue

	parsedMetas = parseMetas(metaTagsSpecific, metaTagsGeneral)
	if "noindex" in parsedMetas or "nofollow" in parsedMetas:
		print("page " + url + " denied by meta tag")
		continue


	try:
		parsedHeader = parseHeader(req.headers['X-Robots-Tag'] or '')
	except:
		parsedHeader = parseHeader('')

	if "nofollow" in parsedHeader or "noindex" in parsedHeader:
		print("page " + url + " denied by HTTP header")
		continue

	for link in soup.find_all('a'):
		if (link.get('rel') is None or not 'nofollow' in link.get('rel')) and parseurl(link.get('href'), req.url) is not None and not link.get('href') in crawled and not link.get('href') in queue:
			queue.append(parseurl(link.get('href'), req.url))
		if (link.get('rel') is None or not 'nofollow' in link.get('rel')) and parseurl(link.get('href'), req.url) is not None:
			if not parseurl(link.get('href'), req.url) in webMap:
				webMap[parseurl(link.get('href'), req.url)] = {'linksTo': [], 'isLinkedToBy': []}
			webMap[parseurl(link.get('href'), req.url)]['isLinkedToBy'].append(req.url)
			webMap[parseurl(link.get('href'), req.url)]['isLinkedToBy']=list(dict.fromkeys(webMap[parseurl(link.get('href'), req.url)]['isLinkedToBy']))
			webMap[req.url]['linksTo'].append(parseurl(link.get('href'), req.url))

	webMap[req.url]['linksTo']=list(dict.fromkeys(webMap[req.url]['linksTo']))
	dataStore=open(os.getenv("HOME") + '/scoopgraciebot.json', 'w')
	json.dump({"queue": queue, "crawled": crawled, "webMap": webMap}, dataStore)
	dataStore.close()
	print('visited ' + req.url)
	print('queue size: ' + str(len(queue)));
	if not os.path.exists(os.getenv("HOME") + '/scoopgraciebot'):
		print('manual shutdown detected. exiting.')
		exit(0)

os.unlink(os.getenv("HOME") + '/scoopgraciebot')
print('no more pages in queue. exiting.')
