#-*- coding:utf8 -*-
"""
Function attributes:
* load: boolean. Optional. If False the function will not load.
* name: string. Optional.
* priority: string. Optional. Three values are available: "high", "medium" or "low",
  default value: "medium".
* thread: boolean. Optional. If True, function will work by starting a thread.
* rule: string or regexp object. Required.
* aliases: list of string or regexp objects. Optional.
* fullmsg: boolean. Optional. If True, pattern is searched on whole message, else
  pattern is a command, the message must begin with a sign.

* access
* evttypes: must be tuple
* skip_sentinel: skip _sentinel instance
* limit
* channels
* url
* showas
"""

import re
from util.functions import *
from util.browser import B as Browser

def clean_ts(string):
	return string.replace("T"," ")[:-4]
	
def contribs(bot, irc, cur):
	
	params = {
		"action": "query",
		"list": "users",
		"ususers": user,
		"usprop": "editcount"
	}
contribs.rule = "c"
	
def blocks(bot, irc, cur):
	args = cur.args.split("|")[0] if not cur.params else cur.params.arguments()
	params = {
		"action": "query",
		"list": "blocks",
	}
	if args:
		wl = WikiLink(args)
		user = wl.title()
		print "wikiusers.py blocks()", user
		if user.startswith("#"):
			params['bkids'] = user.split("|")[0][1:].strip()
		else:
			params['bkusers'] = quote(user.strip())
		Browser.site(wl.language(), wl.family())
	data = Browser.get_api(params)
	if cur.params['raw']:
		bot.reply(str(data).replace("\r","").replace("\n","").replace("\t",""))
	else:
		if data.has_key("query"):
			data = data['query']
			if data['blocks']:
				block = data['blocks'][0]
				id = block['id']
				by = block['by']
				user = block['user']
				since = clean_ts(block['timestamp'])
				till = clean_ts(block['expiry'])
				opts=[]
				allowusertalk = opts.append("allow user talk") if block.has_key('allowusertalk') else ""
				autoblock = opts.append("autoblock") if block.has_key('autoblock') else ""
				nocreate = opts.append("no create") if block.has_key('nocreate') else ""
				noemail = opts.append("no email") if block.has_key('noemail') else ""
				anononly = opts.append("anonimous only") if block.has_key('anononly') else ""
				opts = ", ".join(opts)
				reason = block['reason']
				bot.reply(
					"[#%s] %s blocked %s on %s till %s. Options: %s. Reason: %s",
					id, by, user, since, till, opts, reason
				)
			else:
				bot.reply("User has no block.")
		else:
			bot.reply("No such block.")
	return
blocks.rule=["blocks","bl"]
blocks.url = "http://$proj/w/api.php?format=jsonfm&action=query&list=blocks"

def globalblock(bot, irc, cur):
	""".globalblock <ip> - Check if <ip> is blocked globally on meta."""
	args = cur.args.split("|")[0] if not cur.params else cur.params.arguments()
	wl = WikiLink(args, "meta")
	user=wl.title()
	params = {
		"action": "query",
		"list": "globalblocks",
		"bgip": user
	}
	Browser.site("meta")
	data = Browser.get_api(params)
	bot.reply(str(data).replace("\r","").replace("\n","").replace("\t",""))
	return
	blocked= re.compile(r'<span style="color:blue;">&lt;block id=&quot;(?P<id>\d+)&quot; address=&quot;(?P<address>.*?)&quot; (?P<anon>anononly=&quot;&quot; )?(?:by=&quot;(?P<by>.*?)&quot; )(bywiki=&quot;(?P<bywiki>.*?)&quot; )(?:timestamp=&quot;(?P<since>.*?)&quot; )(?:expiry=&quot;(?P<expiry>.*?)&quot; )(?:reason=&quot;(?P<reason>.*?)&quot; )/&gt;</span>')
	blocked=re.search(blocked,txt)
	url="http://meta.wikimedia.org/w/index.php?title=Special:GlobalBlockList&ip=" + params
	#print blocked
	if blocked:
		blocked=blocked.groupdict()
		since=blocked['since']
		till=blocked['expiry']
		diff=relativedelta(apiTime(till)[1], apiTime(since)[1])
		since=since.replace("T"," ").replace("Z","")
		till=till.replace("T"," ").replace("Z","")
		msg+=u"$b#"+blocked['id']+"$N user: $l"+blocked['address']+"$N was blocked by $o"+blocked['by']+"$N since "+since+" until "+till
		fracts={"years": diff.years, "months": diff.months, "days": diff.days, "hours":diff.hours, "minutes":diff.minutes}
		ds=[]
		r=""
		for f in fracts:
			if fracts[f]==1: ds.append("%i %s" % (fracts[f],f[:-1]))
			elif fracts[f]>1:ds.append("%i %s" % (fracts[f],f))
		if len(ds)>1:
			r=", ".join(ds[:-1])
			r+=r+" and "+ds[-1]
		else:
			r=ds[0]
		msg+=u" (%s)" % (r)
		msg+=u' reason: "%s"' % blocked['reason']
		msg=colors(msg)
	else:
		msg+="No result for this user. %s" % url
		
	self.msg(origin.target, msg)
globalblock.rule = ['globalblock','gblock','global']
globalblock.thread = True
globalblock.url = "http://meta.wikimedia.org/w/api.php?action=query&list=globalblocks&bgip="

def luxo(bot, irc, cur):
	"""
	<div class="mw-contributions-footer">
	<hr />
	<small>721 projectes analitzats. Hi ha 281 contribucions en 6 projectes.<br></small>
	&blocks=true&lang=ca&showclosed=false&recentonly=false&fullblocklog=true
	"""
	user = encode(cur.args)
	params = {
		"blocks": "true",
		"showclosed": "false",
		"recentonly": "false",
		"fullblocklog": "false",
		"lang": "en",
		"user": user
	}
	url = luxo.url % quote(user)
	bot.reply(url)
	data = Browser.get_query(url, params)
	conclusion = re.search("<small>(?P<sc>\d+) projects scanned. (?P<ct>\d+) contributions found in (?P<pr>\d+) projects.<br></small>",data)
	if conclusion:
		conclusion = bot.translate("Projects scanned: %s, %s contributions in %s projects. ") % (conclusion.group('sc'), conclusion.group('ct'), conclusion.group('pr'))
	else: conclusion = ""
	blocks = re.finditer(
		'<div style=\'border-style:outset;border-color:red;border-width:thick;background-color:#FFDFDC;\'>'
		'<h4>Blocks</h4><ul><li>(?P<ts>\d{4}-\d\d-\d\dT(?:\d\d:){3}) '
		'<a href="http://(?P<proj>.+?)\.org/w/index\.php\?title=User:[^"]+">'
		'(?P<admin>[^<^]+)</a> .+?'
		'expiry time: (?P<expire>[^(]+?)\(.+?\)</li></ul></div>',
		data
	)
	expire_blocks = []
	for block in blocks:
		#print block.groups()
		expire_blocks.append([block.group('proj'),block.group('expire')])
	str_blocks = ", ".join(["on %s for: %s" %( x[0], x[1]) for x in expire_blocks])
	b = bot.translate("Blocks: %i. ") % (len(expire_blocks)) if expire_blocks else bot.translate("No blocks found. ")
	blocks = "%sBlocked %s" % (b, str_blocks) if expire_blocks else ""
	bot.reply("%s%s", conclusion, blocks)
luxo.rule = 'luxo'
luxo.url = 'http://toolserver.org/~luxo/contributions/contributions.php?user='

def sul(bot, irc, cur):
	url = "%s%s" % (sul.url,cur.args)
	content = Browser.get_url(url)
	if cur.args:
		if "::" in cur.args: cur.args=cur.args.replace("::","")
		re_acc = re.compile(
			r"<tr>\s*?<td>\s*?<div style='float: left'><a href=\"http://"
			r"(?:(?P<lang>[^\.]+?)\.(?:(?P<lab>[^\.]+?)\.)?)?(?P<fam>[^\.]+?)\.org/w/index\.php\?title=User:(?P<usr>[^\"]*?)\">(?P<db>[^<]*?)</a></div>\s*?"
			r"<div style='float: right'>\(<a href=\"[^\"]*?\">c</a>\)</td></div>\s*?</td>\s*?<td>(?P<proj>[^<]*?)</td>\s*?"
			r"<td>(?P<ec>\d+)</td>\s*?<td><span style='display: none'>(?P<ts>\d*?)</span>(?P<reg>[^<]*?)</td>\s*?"
			r"<td><span style='display: none'>\d+</span>(?P<flags>[^<]*?)</td>\s*?<td>(?P<blocked>[^<]*?)</td>\s*?"
			r"<td>(?P<SUL>[^<]*?)</td>\s*?</tr>\s*?",
			re.S | re.M
		)		
		u = quote(cur.args)
		txt = Browser.get_url(url)
		accounts=re.finditer(re_acc, txt)
		unatt=0
		merged=0
		auto=0
		homewiki=0
		homewikiname=""
		flags=""
		nocontribs=0
		blocked=[]
		accountslength=0
		for acc in accounts:
			accountslength+=1
			acc=acc.groupdict()
			if acc['SUL'] == "unattached": unatt+=1
			elif acc['SUL'] == "merged by user": merged+=1
			#elif acc['SUL'] == "automatically created on login": auto+=1
			elif acc['SUL'] == "autocreated ": auto+=1
			elif acc['SUL'] == "home wiki":
				homewiki+=1
				homewikiname= acc['db']
				flags=", flags: %s" % acc['flags'] if acc['flags'] else ". "
			if acc['ec']=="0":
				nocontribs+=1
			if acc['blocked']!="No":
				blocked.append(acc['db'])
		totaleditcount=re.search("<p>Total editcount: <b>(\d+)</b>", txt)
		totaleditcount = "Total editcount: %s. " % totaleditcount.group(1) if totaleditcount and int(totaleditcount.group(1)) else ""
		nocontribs="%i projects without edits" % nocontribs if nocontribs else ""
		hw_test = re.search("<p><b>Home wiki:</b> \?\?\?</p>", txt)
		if not homewikiname and hw_test: homewikiname = "???"
		noSUL = re.search("<p><b>SUL account doesn't exist</b></p>", txt)
		blocked="Blocked on %i wikis: %s" % (len(blocked),", ".join(blocked)) if blocked else ""
		statusSummary = " (%i home; %i automatically; %i merged; %i unattached). Homewiki: %s%s. " % (homewiki, auto, merged, unatt, homewikiname, flags) \
				if not noSUL else ". SUL account doesn't exist"

		bot.reply("%i accounts matched%s%s%s%s. %s" % (accountslength, statusSummary, totaleditcount, nocontribs, blocked, url))
sul.rule="sul"
sul.url = "http://toolserver.org/~vvv/sulutil.php?user="
