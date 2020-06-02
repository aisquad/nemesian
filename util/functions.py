# -*- coding: utf-8 -*-
import bz2, codecs, json, platform as pf, pickle, os, sys, urllib, re
from datetime import datetime
from dateutil.relativedelta import relativedelta as deltatime
from sitematrix import *

_platform = pf.platform().split("-")[0].lower()
home = os.path.join(r"D:\Documents", "Python") if _platform=="windows" else os.path.join("/home", "pasqual")
common = os.path.join(home, "common")
logs = os.path.join(home, "logs")
pywiki = os.path.join(home, "pywikimedia" if _platform == "windows" else "pywikipedia")
pwb_own = os.path.join(pywiki, "user_scripts")
pwb_logs = os.path.join(pywiki, "user_scripts", "logs")
_all = (home, common, logs, pywiki, pwb_own, pwb_logs)
for folder in _all:
	sys.path.append(folder)
import query, wikipedia as wp

def simplify_chars(word):
	#simplifiquem els diacrítics per a l'ordre alfabètic
	word = word.lower()
	pairs=[(u"àáâäãăǎąåā", "a"),(u'æǣ', "ae"),
		   (u'ḃɓ', "b"),
		   (u'çćčćĉċ', "c"),
		   (u'đḍďḋ', "d"), (u'ð', "dh"),
		   (u'èéêëẽēę', "e"),
		   (u'ḟƒ', "f"),
		   (u'ĝġģğ', "g"),
		   (u'ĥħ', "h"),
		   (u'ìíîïīį', "i"), (u'ĳ', "ij"),
		   (u'ĵ', "j"),
		   (u'ķ',"k"),
		   (u'ŀļḷḹľł',"l"),
		   (u'ñńň', "n"),
		   (u'òóôöõøōǫ', "o"), (u'œ', "oe"),
		   (u'ṗ', "p"),
		   (u'ŗřṛṝ', "r"),
		   (u'şṡšŝ', "s"), (u'ß', "ss"),
		   (u'ţṫṭ', "t"), (u'Þ', "th"),
		   (u'ùúûüŭūų', "u"),
		   (u'ẁŵẅƿ', "w"),
		   (u'ýỳŷÿȳỹ', "y"),
		   (u'źžż', "z")]
	
	for pair in pairs:
		for char in pair[0]:
			word = word.replace(char, pair[1])
	word=word.replace(u"l·l","ll")
	word = re.sub("\W","!", word)
	return word

def sort_list(old_list):
	#ordena una llista
	simplifiedlist={}
	for word in old_list:
		simplifiedlist[simplify_chars(word)]=word
	new_list=[]
	for word in sorted(simplifiedlist.keys()):
		new_list.append(simplifiedlist[word])
	return new_list

def showTimeDiff(date1, date2):
	from datetime import datetime
	from dateutil.relativedelta import relativedelta as deltatime

	timedivs={"y":"any","m":"mes","d":"dia","H":"hora","M":"minut","S":"segon"}
	plural={"dia":"dies","hora":"hores","mes":"mesos"}
	def get_plural(div):
		return plural[timedivs[div]] if plural.has_key(timedivs[div]) else timedivs[div]+"s"
	#dates=reversed(sorted([date1, date2]))
	dates=[date1, date2]
	dates.sort()
	dates.reverse()
	diff=deltatime(dates[0],dates[1])
	diffs_txt=""
	items=[	("y", diff.years), ("m", diff.months), ("d", diff.days),
			("H", diff.hours), ("M", diff.minutes),("S", diff.seconds)]
	diffs=[]
	for item in items:
		diff=""
		if item[1]>1:
			diff="%s" % get_plural(item[0])
		elif item[1]==1:
			diff="%s" % timedivs[item[0]]
		if item[1]>0:
			diff="%i %s"  % (item[1],diff)
			diffs.append(diff)
	if len(diffs)>1:
		print diffs
		diffs_txt=", ".join(diffs[:-1])
		diffs_txt+=" i "+diffs[-1]
	elif len(diffs)==1:
		diffs_txt=diffs[0]
	return diffs_txt

def capitalize(word):
	if not isinstance(word, basestring): return
	if len(word)>1:
		word=word[0].upper()+word[1:]
	elif len(word)==1:
		word=word.upper()
	return word

def ns(title):
	for i in NS:
		if title.find(i+":") == 0:
			return int(NS[i])
	return 0

class Chrono:
	#2010-12-04
	def __init__(self):
		self.alpha = datetime.now()
		self.omega = None
		print self.alpha.strftime("%Y-%m-%d %H:%M")

	def start(self):
		return self.alpha
	
	def end(self):
		return self.omega

	def reset():
		self.alpha = datetime.now()
		self.omega = None
		return self.alpha

	def ellapsed(self):
		t = deltatime(datetime.now(), self.alpha)
		return (t.years, t.months, t.days, t.hours, t.minutes, t.seconds, t.microseconds)

	def stop(self):
		if not self.omega: self.omega = datetime.now()
		t = deltatime(self.omega, self.alpha)
		return self.omega, (t.years, t.months, t.days, t.hours, t.minutes, t.seconds, t.microseconds)

	def show(self):
		now = datetime.now()
		t = deltatime(now, self.alpha)
		print "%i %i:%i:%i" % (t.days, t.hours, t.minutes, t.seconds)
		return now, (t.years, t.months, t.days, t.hours, t.minutes, t.seconds, t.microseconds)
	
def convert_bytes(bytes):
	#2010/12/07 00:51
	#http://snipperize.todayclose.com/snippet/py/Converting-Bytes-to-Tb/Gb/Mb/Kb--14257/
	bytes = float(bytes)
	if bytes >= 1099511627776:
		terabytes = bytes / 1099511627776
		size = '%.2f TB' % terabytes
	elif bytes >= 1073741824:
		gigabytes = bytes / 1073741824
		size = '%.2f GB' % gigabytes
	elif bytes >= 1048576:
		megabytes = bytes / 1048576
		size = '%.2f MB' % megabytes
	elif bytes >= 1024:
		kilobytes = bytes / 1024
		size = '%.2f KB' % kilobytes
	else:
		size = '%.2fB' % bytes
	return size

#IRC formats and colors
_abredged_colors={
	"B": u"\x02", #BOLD
	"N": u"\x0f", #NORMAL
	"R": u"\x16", #REVERSE
	"U": u"\x1f", #UNDERLINE

	"k": u"\x0301",  #BLACK
	"b": u"\x0312",  #BLUE
	"n": u"\x0305",  #BROWN
	"c": u"\x0302",  #CYAN
	"+b": u"\x0302", #DARKBLUE
	"+g": u"\x0314", #DARKGRAY
	"+e": u"\x0303", #DARKGREEN
	"e": u"\x0309",  #GREEN
	"g": u"\x0315",  #LIGHTGRAY
	"m": u"\x0313",  #MAGENTA
	"o": u"\x0307",  #OLIVE
	"p": u"\x0306",  #PURPLE
	"r": u"\x0304",  #RED
	"t": u"\x0310",  #TEAL
	"w": u"\x0300",  #WHITE
	"y": u"\x0308",  #YELLOW
}

def colors(txt):
	for clr in _abredged_colors:
		txt=txt.replace("&%s;" % clr, _abredged_colors[clr])
	return txt

def has_wildcard(mask, match):
	#check if string has IRC wildcards
	mask = mask.replace('?', '[\\w|\\W]').replace('*', '[\\w|\\W]+')
	regex = re.compile(mask, re.skip_sentinelCASE)
	if regex.match(match) == None: return False
	else: return True

def wildcard_to_regexp(string):
	#Wildcards used in IRC are "?" and "*".
	#Transalte they to a correct regular expression.
	string = string.replace("?",".").replace("*",".*")
	return string

def escape_for_regexp(string):
	#Standardize character as escape caracter in a regular expression
	for char in '^$[].|?+*{}()':
		string = string.replace(char, r'\%s' % char)
	return string

def decode(txt=""):
	ntxt=""
	try:
		ntxt=unicode(txt, 'utf-8')
	except UnicodeError:
		try:
			ntxt=unicode(txt, 'latin-1')
		except UnicodeError:
			try:
				ntxt = txt.decode('cp1252')
			except Exception:
				print "unknown coding."
	return ntxt

def encode(text, encoding="utf-8"):
	if isinstance(text, unicode):
		try: text = text.encode(encoding)
		except UnicodeEncodeError, e:
			pass
	return text

def quote(string):
	return urllib.quote(encode(string))

def find_user(user, users):
	for nick in users:
		user = re.search(r"(%s[^ ]+)" % user, nick, re.I)
		if user:
			user=user.group(1)
			return user
	return ""

def _trans(file, string):
	try:
		exec("from lang import %s" % file)
		variables=vars(eval(file))
		for var in variables.keys():
			if var.startswith("__"): continue
			if variables[var].has_key(string):
					return variables[var][string]
	except:
		print "functions.py exception passed"
	return string

def join_list(l):
	if isinstance(l, (list, tuple)):
		if len(l)>1:
			rtn="%s %s %s" % (", ".join(l[:-1]), _trans("ca", "and"), l[-1])
		else:
			rtn = l[0]
		return rtn

def join_userlist(li, lg="en"):
	if isinstance(li, (list, tuple)):
		if len(li)>1:
			li=[colors(u"&b;%s·%s&N;" % (user[0], user[1:])) for user in li]
			rtn="%s %s %s" % (", ".join(li[:-1]), _trans(lg, "and"), li[-1])
		else:
			rtn = colors(u"&b;%s·%s&N;" % (li[0][0], li[0][1:]))
		return rtn

class WikiLink:
	def __init__(self, string, lang="en", fam ="w"):
		self.string = string
		self._lang = lang
		self._fam = fam
		self._site = ""
		self.get_site(lang, fam)
		self.slice()

	def normalize_url(self, url):
		m = re.search(u"(http://[^.]+\.([^.]+)\.org/wiki/)(.+)", url)
		if not m: return url
		path  = m.group(1)
		fam  = m.group(2)
		title = m.group(3)
		ns=""
		elements=title.split(":", 1)
		ns_test = elements[0].replace("_"," ").lower()
		if ns_test in namespaces:
			ns = elements[0]
			ns = re.sub("(?i)mediawiki", "MediaWiki", ns, 1)
			ns = ns+":"
			title=elements[1]
		if fam != "wiktionary":
			title = title[0].upper() + title[1:]
		return path+ns+title

	def normalize_title(self, string):
		ns=""
		ns_test = string.replace("_"," ").lower()
		if ns_test in namespaces:
			string = re.sub("(?i)mediawiki", "MediaWiki", string, 1)
		if self.family() != "wiktionary":
			string = string[0].upper() + string[1:]
		return string

	def get_site(self, lang=None, fam=None):
		if lang and lang in projects:
			site=projects[families[lang]]
		elif fam and fam in projects:
			site=projects[families[fam]]
		else:
			if not fam: fam = families[self._fam]
			if not lang: lang = self._lang
			site= "%s.%s" % (lang,fam)
		if not site.endswith(".cat"):
			if site == "translatewiki":
				site+=".net"
			else:
				site += ".org"
		self._lang, self._fam, d = re.search("(?:(.*)\.)??([^.]+?)\.(org|net|cat)", site).groups()
		self._site = site
		return site
		
	def slice(self):
		prefixes=r"[dchjlnr]"
		regexps={
			"l": re.compile(ur"(?P<pref>%s?)\[\[(?P<link>[^\|{}[\]]+)(?:\|[^{}[\]]+)?\]\]" % prefixes),
			"u": re.compile(ur"(?P<codes>[^[{]+?:)?(?P<user>[^:]+?[^\]}])?$"),
			"t": re.compile(ur"(?P<pref>([\w\-:]+|%s)*?)(?P<begin>\{\{\{?)(?P<link>[^\{\}\|]+?)(?:\|(?P<params>[^\}]+?))?(?P<end>\}\}\}?)" % prefixes)
		}
		for regexp in regexps:
			m=regexps[regexp].search(self.string)
			if m:
				m=m.groupdict()
				break
		isTemplate = regexp == "t"

		if m and isTemplate and len(m['begin'])+len(m['end'])!=4:
			return None
	
		if m and regexp in ("l","t"):
			if m['link']:
				pref=m['pref']
				link=m['link']
	
				if link.startswith(":"): link=link[1:]
				title=""
				params=""
				if isTemplate:
					el="DEFAULTSORT:"
					if el in link: link=link.replace(el,"")
					title=m['link']
					params=m['params']
	
				if not isTemplate or isTemplate and not params:
					#%26 &; %3D =
					query= "?"+quote(link.split("?")[1]) if "?" in link else ""
					query = query.replace("%26","&").replace("%3D","=")
					section="#"+quote(link.split("#")[1]).replace("%",".") if "#" in link else ""
				else:
					query = "?"+params.split("?")[1] if "?" in params else ""
					section ="#"+quote(params.split("#")[1]).replace("%",".") if "#" in params else ""
					params=params.split("#")[0]
					params=params.split("?")[0]
				link=link.split("?")[0]
				link=link.split("#")[0]
	
				ns=""
				site=""
				fam = ""
				lang = ""
	
				#Get site (if it is not template) and namespace.
				loop=link.split(":")[:-1]
				for x in loop:
					x_lwr=x.lower()
					if not isTemplate:
						if x_lwr in languages:
							lang = x
							link = link.replace("%s:" % x, "")
						if x_lwr in families:
							fam = families[x_lwr]
							link = link.replace("%s:" % x, "")
							if x[0].isupper():
									ns="Project"
					if x_lwr in namespaces:
						nice_ns=x[0].upper()+x[1:].lower()
						ns = nice_ns
						link = link.replace("%s:" % x, "")
	
				#Get site if it is a template and it has prefixes.
				if isTemplate:
					prefs=pref.split(":")
					loop=pref.split(":")
					for pref in loop:
						if pref in languages:
							lang = pref
							link = link.replace("%s:" % lang, "")
						if pref in families:
							fam = families[pref]
							link = link.replace("%s:" % fam, "")
				site = self.get_site(lang, fam)	

				#Add namespace.
				namespace=""
				if ns and not isTemplate:
					namespace = quote(ns)
				elif isTemplate:
					if title:
						if title.lower() in ("u","ud","ut"):
							namespace = "User:" if title == "u" else "User_talk:"
							link = params
						else:
							namespace = "Template:"
					else:
						namespace = "Template:"
				if namespace and not namespace.endswith(":"): namespace += ":"

				#Complete the request.
				if pref:
					if pref == "c" and isTemplate: #_c_ontributions
						namespace = re.sub("[Uu]ser(?:_[Tt]alk)?:","Special:Contributions/",namespace)
					elif pref=="d": #_d_iffonly
						query= "?diff=cur&oldid=prev&diffonly=true"
					elif pref=="e": #r_e_nder and diffonly
						query= "?action=render&diff=cur&oldid=prev&diffonly=true"
					elif pref=="h":  #_h_istory
						query= "?action=history"
					elif pref == "j": #_j_avascript
						query= "?action=raw&ctype=text/javascript"
					elif pref=="l": #_l_astest diff
						query= "?diff=cur&oldid=prev"
					elif pref=="n": #_n_o redirect
						query= "?redirect=no"
					elif pref=="r": #_r_ender
						query= "?action=render"
				self._title = self.normalize_title(quote(link))
				link = self._title + query

			return (site, namespace, self._title, section)

		elif m and regexp == "u":
			lang=""
			fam=""
			ns=""
			
			#print "functions.py WL.slice\n\tmUser", m['user'], m['user'][:-1], m['user'].endswith(":"), m['user'][:-1] in languages.keys() + projects.keys()
			if m['user'] and m['user'].endswith(":") and m['user'][:-1] in languages.keys() + projects.keys():
				m['codes'] += m['user']
				m['user'] = ""
			print "\t", m['user']
			if m['codes'] and ":" in m['codes']:
				loop=list(m['codes'].split(":"))
				for x in loop:
					x_lwr=x.lower()
					if x_lwr in languages:
						lang = x
					if x_lwr in families:
						fam = families[x_lwr]
						if x[0].isupper():
								ns="Project"
					if x_lwr in namespaces:
						nice_ns=x[0].upper()+x[1:].lower()
						ns = nice_ns
			self._site = self.get_site(lang, fam)
			self._title = self.normalize_title(m['user']) if m['user'] else ""
			
			return (self._site, "User:", self._title, "")

	def to_url(self):
		if self._site:
			url = "http://%s/wiki/%s%s%s" % self.slice()
			url = self.normalize_url(url)
			return url
	
	def family(self):
		return self._fam
	
	def language(self):
		return self._lang
	
	def title(self):
		return self._title
	
	def site(self):
		return self._site

class Load:
	"""
	Load modules from a specified folder, and register its instances into a dictionary
	"""
	def __init__(self, folder):
		self.variables={}
		self.commands = {'high': {}, 'medium': {}, 'low': {}}
		self.folder=folder
		self._initialize()

	def _initialize(self):
		self.modules = []
		moduledir = os.path.join(os.getcwd(), self.folder)
		for filename in sorted(os.listdir(moduledir)):
			if filename.endswith('.py') and not filename.startswith('_'):
				name, ext = os.path.splitext(os.path.basename(filename))
				try: module = getattr(__import__("%s.%s" % (self.folder, name)), name)
				except Exception, e:
					print >> sys.stderr, "Error loading %s: %s" % (name, e)
				else:
					if hasattr(module, 'load'):
						#if module has the variable 'load' as False, don't load this one. (See "hasattr(method, 'load')")
						if not module.load: continue
					if hasattr(module, 'initialize'):
						module.initialize(self)
					self._register(vars(module))
					self.modules.append(name)
		if self.modules:
			print >> sys.stderr, 'Registered modules:', ', '.join(self.modules)
			pass
		self._bindrules()

	def _register(self, variables):
		for name, obj in variables.iteritems():
			self.variables[name] = obj

	def _bindrules(self):
		all=[]
		for name, method in self.variables.iteritems():
			if hasattr(method, 'rule'):
				if hasattr(method, 'load') and not method.load: continue
				if not hasattr(method, 'name'):
					method.name = method.__name__
				if not hasattr(method, 'priority'):
					method.priority = 'medium'
				if not hasattr(method, "evttypes"):
					method.evttypes=("msg", "notice", "action")
				elif isinstance(method.evttypes, basestring):
					method.evttypes=(method.evttypes,)
				if not hasattr(method, 'thread'):
					method.thread = False
				if not isinstance(method.rule, list):
					method.rule = [method.rule]
				if not hasattr(method, 'aliases'):
					method.aliases = []
				if not hasattr(method, 'fullmsg'):
					method.fullmsg = False
				if not hasattr(method, 'limit'):
					method.limit = 3
				if not hasattr(method, 'access'):
					method.access=["*"]
				elif not isinstance(method.access, list):
					method.access=[method.access]
				if not hasattr(method, 'skip_sentinel'):
					method.skip_sentinel=False
				if not hasattr(method, 'channels'):
					method.channels={}
				if isinstance(method.__doc__, basestring):
					method.help = method.__doc__
				else:
					method.help = "no such help."
				#fix config forgettings
				if "*" in method.evttypes:
					method.evttypes=("*",)
					method.rule=False
					method.skip_sentinel=True
				self.commands[method.priority][method.name]=method
				all.append(method.name)
		print "\t", ", ".join(all)

class Path:
	def __init__(self):
		pass
	
	def append(self, path):
		"""append any folder"""
		sys.path.append(path)
	
	def join(self, *args):
		return os.path.join(*args)
	
	def preview(self, path):
		return os.path.split(path)[0]
		
	def basename(self, filename):
		return os.path.basename(filename)
		
	def extension(self, filename):
		return os.path.splitext(self.basename(filename))[1]
		
	def name(self, filename):
		return os.path.splitext(self.basename(filename))[0]
		
	def split(self, path):
		filename = self.basename(path)
		dirname = os.path.dirname(path)
		path = [home]
		path += dirname.replace(home+os.sep, "").split(os.sep)
		return path, self.name(filename), self.extension(filename)
	
	def files(self, path):
		return os.listdir(path)

class Obj:
	def __init__(self, path, encoding):
		self.ext = Path().extension(path)
		self.path = path
		self.encoding = encoding
		self.stream = None
		
	def exists(self):
		return os.path.exists(self.path)

	#file modes
	def read(self):
		if self.ext == ".bin":
			self.stream = bz2.BZ2File(self.path, "r")
			return self.stream
		else:
			self.stream = codecs.open(self.path, "r", self.encoding)
			return self.stream
	
	def write(self):
		if self.ext == ".bin":
			self.stream = bz2.BZ2File(self.path, "w")
			return self.stream
		else:
			self.stream = codecs.open(self.path, "w", self.encoding)
			return self.stream
		
	def append(self):
		if self.ext == ".bin":
			self.stream = bz2.BZ2File(self.path, "w")
			return self.stream
		else:
			self.stream = codecs.open(self.path, "a", self.encoding)
			return self.stream

	#file methods	
	def get(self):
		if self.exists():
			if self.stream and self.stream.mode == "rb":
				if self.ext == ".bin":
					data = pickle.load(self.read())
				elif self.ext == ".log":
					try:
						data = json.load(self.read(), self.encoding)
					except ValueError:
						data = self.stream.read()
				else:
					data = self.stream.read()
				return data
			else:
				self.read()
				return self.get()
		else:
			if self.ext in (".bin", ".log"):
				data = {}
			else:
				data = ""
			self.put(data)
			return data
			
	def put(self, data, clean=False):
		if clean:
			self.write()
		elif not clean and self.exists():
			if self.ext in (".bin", ".log"):
				old_data = self.get()
				if isinstance(old_data, basestring):
					data = u"%s\r\n%s" % (old_data, data)
					self.append()
				elif isinstance(old_data, dict):
					old_data.update(data)
					data = old_data.copy()
			else:
				data = u"\r\n%s" % (data)
				self.append()
		elif not self.exists():
			self.write()
		if self.ext == ".bin":
			pickle.dump(data, self.write(),protocol=pickle.HIGHEST_PROTOCOL)
		elif self.ext == ".log":
			if isinstance(data, dict):
				json.dump(data, self.write(), encoding=self.encoding, indent=4)
			else:
				self.stream.write(data)
		else:
			self.stream.write(data)
		if self.ext != ".bin": self.stream.flush()
		else: self.stream.close()
	
	def size(self):
		return os.path.getsize(self.path)
	
	def mtime(self):
		return datetime.fromtimestamp(os.path.getmtime(self.path)).strftime("%Y-%m-%d %H:%M:%S") #last modified
		
	def atime(self):
		return datetime.fromtimestamp(os.path.getatime(self.path)).strftime("%Y-%m-%d %H:%M:%S") #last access
		
	def ctime(self):
		return datetime.fromtimestamp(os.path.getctime(self.path)).strftime("%Y-%m-%d %H:%M:%S") #last change
	
class File:
	def __init__(self, name, path=None, encoding=None):
		"""\
		types: "b": binary, "d": data, "t": text, "p": python script
		modes: "a(ppend)", "w(rite)"
		"""
		self.name = Path().name(name)
		self.ext = Path().extension(name) or ".txt"
		self.path = path or Path().join(home, "logs")
		self.basename = "%s%s" % (self.name, self.ext)
		self.full_path = "%s%s%s" % (self.path, os.sep, self.basename)
		self.encoding = encoding or "utf8"
		self.obj = Obj(self.full_path, self.encoding)
	
	def load(self):
		if self.ext != ".py": return {}
		print self.path, self.name
		self.name = Path().name(self.name)
		stream, path, descr = imp.find_module(self.name, [self.path])
		return imp.load_module(self.name, stream, path, descr)
		
	def get(self):
		return self.obj.get()
	
	def put(self, data, clean=False):
		self.obj.put(data, clean)

	def close(self):
		self.obj.stream.close()
		
	def exists(self):
		return self.obj.exists()
	
	def size(self):
		return self.obj.size()
	
	def modified(self):
		return self.obj.mtime()
		
	def created(self):
		return self.obj.ctime()
	
	def accessed(self):
		return self.obj.atime()
	
	def filename(self):
		return self.basename

class Dicts:
	def __init__(self, log, dir=None):
		self._logname = "%s.bin" % log
		self._dir = dir
		self._log = File(self._logname, self._dir).get()

	def __call__(self):
		return self._log

	def __delitem__(self, key):
		del self._log[key]    

	def __getitem__(self, key):
		return self._log.get(key)

	def __setitem__(self, key, value):
		self._log[key] = value

	def length(self):
		return len(self._log)

	def get(self, key, failvalue=None):
		return self._log.get(key, failvalue)

	def update(self, key, value):
		self._log[key]=value
		self.save()

	def delete(self, value={}):
		self._log=value
		self.save()

	def keys(self):
		return self._log.keys()

	def items(self):
		return self._log.items()
	
	def iteritems(self):
		return self._log.iteritems()

	def values(self):
		return self._log.values()

	def has_key(self, key):
		return self._log.has_key(key)

	def copy(self):
		return self._log.copy()

	def name(self):
		return self._logname

	def read(self):
		return self._log

	def save(self):
		File(self._logname, self._dir).put(self._log)