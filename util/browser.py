# -*- coding:utf-8 -*-
"""
	20-11-2009. Pasqual @ cawiki
	Classes:
		Site
		Browser
"""

import codecs, getpass, HTMLParser, httplib, json, os, urllib
import sched
from urlparse import urlparse
from functions import encode, WikiLink, projects, families

actions = (	'sitematrix', 'opensearch', 'query', 'expandtemplates', 'parse', 'feedwatchlist',
			'help', 'paraminfo', 'purge', 'rollback', 'delete', 'undelete', 'protect', 'block', 'unblock', 'move',
			'edit', 'upload', 'emailuser', 'watch', 'patrol', 'import', 'userrights'
)
post_actions=('login', 'purge', 'rollback', 'delete', 'undelete', 'protect', 'block', 'unblock', 'move', 'edit', 'upload', 'emailuser', 'import', 'userrights')		

class Site:
	def __init__(self, lang=None, family=None):
		self._lang   = lang or "en"
		self._family = family or "wikipedia"

	def __repr__(self):
		return self.abredge_site()

	def lang(self):
		return self._lang

	def family(self):
		return self._family
	
	#def splice(self, string):
	#	string = string.replace("[[","").replace("]]", "")
	#	chunks = string.split(":")
	#	if len(chunks) == 1:
	#		page = chunks[0]
	#		lang = self._lang
	#		fam = self._fam
	#	else:
	#		if fam in 

	def make_site(self, lang=None, fam=None):
		if not lang:
			lang = self._lang
		if not fam:
			fam = self._family
		if lang == "meta":
			fam = "wikimedia"
			self._family = fam

		if fam and fam in projects:
			site=projects[families[fam]]
		else:
			if not fam: fam = families[self.fam]
			if not lang: lang = self.lang
			site= "%s.%s" % (lang,fam)
		if not site.endswith(".cat"):
			if site == "translatewiki": site+=".net"
			else:site += ".org"
		return site

	def abredge_site(self, site=None):
		if not site: site=self.make_site()

		lang = site.split(".")[0]
		fam = site.split(".")[1]
		fams={
			"wikipedia": "wiki",
			"wiktionary": "wikt",
			"wikibooks": "books",
			"wikinews": "news",
			"wikisource": "source",
			"wikiquote": "wikiquote"
		}
		if fam in fams:
			fam=fams[fam]
		return lang+fam

class Browser:
	def __init__(self):
		self._user_agent     = "Nemesian 1.0 Python API wikimedia. Coet@cawiki"
		self._content_type   = "application/x-www-form-urlencoded"
		self._accept         = "text/plain"

		self._user           = "Coet"
		self._userIsLoggedIn = False
		self._cookies        = ""
		self._site = Site().make_site()

	def site(self, lang=None, fam=None):
		self._site = Site().make_site(lang, fam)
		return self._site

	def connection(self, params, headers, mode="GET", path="/w/api.php"):
		if mode == "POST":
			conn = httplib.HTTPConnection(self._site)
			conn.request(mode, path, params, headers)
			response = conn.getresponse()
			data = response.read()
			info = response.getheaders()
		else:
			h = httplib.HTTP(self._site)
			path = "%s?%s" % (path, params)
			h.putrequest(mode, path)
			h.putheader('Host', self._site)
			h.putheader('User-agent', self._user_agent)
			h.endheaders()
			print "browser.py"
			print "\tsite:", self._site
			print "\tparams:", params
			print "\tpath:", path
			returncode, returnmsg, info = h.getreply()
			if returncode == 200:  #OK
				f = h.getfile()
				data = f.read()
			elif returncode == 302:
				for token in str(info).splitlines():
					parts=token.split(": ",1)
					print parts
					if parts[0].lower()=="location":
						url= urllib.unquote(parts[1])
						params = urlparse(url)
						params = params.query.split("&")
						params_d={}
						for i in params:
							k, v = i.split("=")
							params_d[k]=v
						print params_d
						data = self.get_page(params_d)
						break
			else:
				print "\n", " ERROR ".center(60,"!")
				print returncode, returnmsg
				print info
				data=""
		return data

	def set_headers(self, hdr=None):
		headers = {
			"User-Agent": self._user_agent,
			"Content-type": self._content_type,
			"Accept": self._accept,
		}
		if hdr: headers.update(hdr)
		return headers

	def set_params(self, params):
		return urllib.urlencode(params)

	def get_cookies(self):
		home = os.getcwd()
		logindata= os.path.join(home, "login-data")
		if not os.path.exists(logindata):
			os.makedirs(logindata)

		prefix= Site().abredge_site(self._site)
		file = "%s_%s.data" % (prefix, self._user)
		file = os.path.join(logindata,file)

		if os.path.exists(file):
			jsontext = open(file,"r").read()
			cookies = json.loads(jsontext)
			self._cookies = self.set_cookies(cookies)
			return
		else:
			print "no cookies for %s" % self._site
			return ""

	def set_cookies(self, data):
		prf=data["cookieprefix"]
		userName = "%sUserName" % prf
		userID = "%sUserID" % prf
		token = "%sToken" % prf
		sessionID = "%s_session"

		c={}
		c[userName] = data["lgusername"]
		c[userID] = data["lguserid"]
		c[token] = data["lgtoken"]
		c[sessionID] = data['sessionid']

		cookies = ["k=%s" % str(c[k]) for k in c]
		cookies = "; ".join(cookies)
		self._userIsLoggedIn = True
		return cookies

	def create_login_data(self, data):
		home = os.getcwd()
		logindata = os.path.join(home, "login-data")
		if not os.path.exists(logindata):
			os.makedirs(logindata)

		file = "%s_%s.data" % (data['cookieprefix'], data['lgusername'])
		file = os.path.join(logindata,file)

		if not os.path.exists(file):
			f = open(file,"w")
			json.dump(data, f, indent = 4)
			f.close()

	def get_api(self, params, headers=None):
		params["format"] = "json"
		mode = "POST" if params["action"] in post_actions else "GET"
		if params['action'] in post_actions[1:]:
			headers = {"Cookie": self._cookies.encode("utf-8")}
		params   = self.set_params(params)
		headers  = self.set_headers(headers)
		data     = self.connection(params, headers, mode)
		data     = json.loads(data)
		return data

	def get_page(self, params, headers=None, mode="GET", path="/w/index.php"):
		"""Get a page from a Wikimedia project""" 
		params = self.set_params(params)
		headers = self.set_headers(headers)
		data = self.connection(params, headers, mode, path)
		return data

	def get_url(self, url, headers=None, mode="GET"):
		headers = self.set_headers(headers)
		url= urllib.unquote(encode(url))
		url = urlparse(url)

		self._site=url.netloc
		path = url.path
		query = url.query.split("&")
		params={}
		for e in query:
			k, v = e.split("=")
			params[k]=v
		data = self.get_page(params, headers, mode, path)
		return data

	def get_query(self, url, params, headers=None, mode="GET"):
		headers = self.set_headers(headers)
		url = urllib.unquote(encode(url))
		url = urlparse(url)
		self._site = url.netloc
		path = url.path
		data = self.get_page(params, headers, mode, path)
		return data

	def login(self):
		user  = raw_input("user:")
		passw = ""
		while not passw:
			passw = getpass.getpass("password:")
		params = {"action": "login", "lgname": user, "lgpassword": passw}
		data = self.get_api(params)
		data = data['login']
		if data['result']=="Success":
			self._user = data['lgusername']
			self.create_login_data(data)
			self._cookies = self.set_cookies(data)
		elif data['result']=="NeedToken":
			params['lgtoken']=data['token']
			data = self.get_api(params)
			data = data['login']
			if data['result']=="Success":
				self._user = data['lgusername']
				self.create_login_data(data)
				self._cookies = self.set_cookies(data)
			else:
				print data
		else:
			print data
B = Browser()

def get_new_pages():
	import re, codecs
	timestamp=datetime.now()
	timestamp=timestamp-timedelta(hours=26)
	params={
		"title": "Special:Newpages",
		"offset": timestamp.strftime("%Y%m%d%H%M%S"),
		"dir": "prev",
		"hideredirs":1,
		"limit": 5000,
		"uselang":"en"
	}
	page = B.get_page(params).decode("utf-8")
	javascript = page.split('<script type="text/javascript">')[1].split("</script>")[0]
	content = page.split("<!-- start content -->")[1].split("<!-- end content -->")[0]
	f=codecs.open("page.log","w","utf-8")
	f.write(u"%s\r\n%s" % (javascript,content))
	f.close()
	tokens=re.compile(
		ur'<li[^>]*>(?P<date>[\d:]+, \d{1,2} \w+ \d{4})[^<]*'
		ur'<a href="[^"]+" title="[^"]+">(?P<title>[^<]+)</a> \(<a href="[^"]+" title="[^"]+">hist</a>\)[^\[]+'
		ur'\[(?P<length>[^ ]+) bytes\][^<]+'
		ur'<a href="[^"]+" (?:class=".*" )?title="[^"]+"[^>]*>(?P<user>.+)</a>[^(]+\(<a href="[^"]+" (?:class=".+" )?title="[^"]+">Talk</a>(?: \| <a href="[^"]+" title="[^"]+">contribs</a>)?\)</span>  '
		ur'<span class="summary">\((?:<a href=".*" class="mw-redirect" title=".*">←</a> )?(?P<comment>.+)\)</span> (?:<span class="mw-tag-markers">(?:\(<span class="mw-tag-marker .+"><a href="/wiki/Especial:Tags" title="Especial:Tags">.+</a>.+</span>\))?</span>)?</li>')
	pages = re.findall(ur'(<li[^>]*>.*</li>)', content)
	c=0
	f1=codecs.open("nomatch.txt","w","utf-8")
	f2=codecs.open("match.txt","w","utf-8")
	f3=codecs.open("tokens.log","w","utf-8")
	for page in pages:
		c+=1
		m = tokens.search(page)
		if m:
			print c, "%r" % m.group("title")
			f2.write(u"%s\r\n" % page)
			#d=dict(zip(("date","title", "length", "user", "summary"), m.groups()))
			d=m.groupdict()
			d['comment']=re.sub(r"<(?:sp)?an?[^>]*>([^<])+</(?:sp)?an?>", r"\1",d['comment'])
			f3.write(u"%s\r\n" % d)
		else:
			f1.write(u"%s\r\n" % page)
	f1.close()
	f2.close()
	f3.close()
	print "index.php",len(pages)

def get_allpages(next=None):
	params = {
		"action": "query",
		"list": "allpages",
		"aplimit": "max",
	}
	if next: params['apfrom']=next
	B.get_cookies()
	B.get_api(params)

def log_allpages():
	fname = "psq_allpages.log"
	f = codecs.open(fname, "w", "utf-8")
	next="!"
	x=0
	while next:
		q=get_allpages(next)
		print q
		pages=q['query']['allpages']
		next=q['query-continue']['allpages']['apfrom'] if q.has_key('query-continue') else None
		for page in pages:
			f.write(u"# [[%s]]" % page['title'])
		x+=len(pages)
		print x
	f.close()

def test():
	import codecs
	page = B.get_page({"title":"Usuari:Pasqual"})
	f=codecs.open("test3.log","w","utf-8")
	f.write(page.decode("utf-8"))
	f.close()
	print "Browser.py test() #274 OK"

if __name__ == "__main__":
	B.site("ca")
	B.login()
	B.get_cookies()
	#get_new_pages()
	#test()
	log_allpages()