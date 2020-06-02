# -*- coding: utf8 -*-
# tests.py
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
* skip_sentinel: skip sentinel instance
* limit
* channels
* url
"""

import json, os, re, time
from datetime import datetime
from random import randint, choice

from dateutil.relativedelta import relativedelta as timedelta

from framework.irclib import irc_lower
from util.functions import *
from util.browser import B as Browser

def chrono(bot, irc, cur):
	print cur.args
	if not cur.args:
		label = bot.label
		t = bot.init_time
		diff = timedelta(datetime.now(), datetime.fromtimestamp(t))
		diff_str = "%i d, %.2i h, %.2i m, %.2i s." % (diff.days, diff.hours, diff.minutes, diff.seconds)
		bot.privnotice("I've join %s at %s (%s ago)", bot.label, datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"), diff_str)
	else:
		if cur.args == "wm":
			label= "wikimedia"
			tbot = bot.thread_bots(label)
			t=tbot.init_time
			diff = timedelta(datetime.now(), datetime.fromtimestamp(t))
			diff_str="%i d, %.2i h, %.2i m, %.2i s." % (diff.days, diff.hours, diff.minutes, diff.seconds)
			bot.privnotice("I've join %s at %s (%s ago)", label, datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"), diff_str)
chrono.rule="chrono"
chrono.limit = 10

def features_(bot, irc, cur):
	for k, v in irc._features.iteritems():
		msg = "%s: %s" %(k, v)
		bot.reply(msg)
		time.sleep(5)
features_.rule = ("features")

def error_(bot, irc, cur):
	msg+=""
error_.rule = "error"

def triggers_(bot, irc, cur):
	if not cur.opts:
		bot.reply(" ".join([x.replace("\\","") for x in irc.triggers[1:-1]]))
	elif cur.params['a']:
		triggers = list(irc.triggers)[1:-1]
		triggers.append(cur.opts['a'])
		irc.triggers = "[%s]" % escape_for_regexp("".join(triggers))
		bot.reply(" ".join([x for x in irc.triggers.replace("\\","")[1:-1]]))
	elif cur.params['r']:
		triggers = list(irc.triggers)[1:-1]
		if cur.opts['r'] in triggers: triggers.remove(cur.opts['r'])
		irc.triggers = "[%s]" % escape_for_regexp("".join(triggers))
		bot.reply(" ".join([x for x in irc.triggers.replace("\\","")[1:-1]]))
triggers_.rule = ["trig", "triggers"]
triggers_.access = ["tester","staff","botop"]

def parse_(bot, irc, cur):
	bot.reply("cur.params: %s, cur.args: %s", str(cur.params), cur.args)
	bot.reply("cur.items: %s", cur.items)
parse_.rule="parse"
parse_.limit=9
parse_.channels={"##bots-ca": "parseja", "##botzilla": "(?#re)quarteja"}

def sitematrix(bot, irc, cur):
	file = os.path.join(os.getcwd(),"sitematrix.log")
	if os.path.exists(file) and cur.args:
		jsontext = open(file,"r").read()
		codes = json.loads(jsontext)
		if cur.args:
			code = cur.args
			if code in codes:
				bot.reply(codes[code][0])
	else:
		params ={
			"action": "sitematrix",
		}
		sm = Browser.get_api(params)
		number = sm['sitematrix']['count']
		codes={}
		for id in sm['sitematrix']:
			if id.isdigit():
				code = sm['sitematrix'][id]['code']
				name = sm['sitematrix'][id]['name']
				families = sm['sitematrix'][id]['site']
				fam=[]
				for family in families:
					fam.append(family['code'])
				codes[code]=(name, fam)
			if id=="specials":
				for proj in sm['sitematrix'][id]:
					code = proj['code']
					domain = proj['url'][7:]
					codes[code]=(domain,["special"])
		f = open(file,"w")
		json.dump(codes, f, indent=4, encoding="utf-8")
		f.close()
		if cur.args:
			code = cur.args
			if code in codes:
				bot.reply(codes[code][0])

		bot.reply("%s :  %s" %( url,number))
sitematrix.rule="sitematrix"
sitematrix.url="http://meta.wikimedia.org/w/api.php?format=jsonfm&action=sitematrix"