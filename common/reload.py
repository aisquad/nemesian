# -*- coding: utf8 -*-
# reload.py
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
* evttypes
* ignore
* limit
* channels
* url
"""

import os, re, time
from framework.irclib import irc_lower
from random import randint, choice

from util.functions import *

def reboot_(bot, irc, cur):
	msg = u"Ara torne :) ..."
	from_ = cur.channel or irc.label
	msg=cur.dict["msg"] if hasattr(cur, "dict") and cur.dict.get("msg") else "%s m'ho ha demanat des de %s" % (cur.nick, from_)
	bot.reboot(msg)
reboot_.rule = re.compile(r"^(?:(?:$both)?reboot)!?(?: (?P<msg>.*))?$")
reboot_.fullmsg = True

def reload_(bot, irc, cur):
	if not isinstance(cur.params['lang'], bool):
		t=time.time()
		import lang
		if isinstance(cur.params['lang'], unicode):
			exec("reload(lang.%s)" % cur.params['lang'])
			t=time.time()-t
			bot.reply("reloaded lang.%s in %0.3f ms" % (cur.params['lang'], t))
		elif isinstance(cur.params['lang'], list):
			for l in cur.params['lang']:
				try:
					exec("reload(lang.%s)" % l)
				except AttributeError:
					bot.privnotice("module %s not found", l)
			t=time.time()-t
			langs=", ".join(cur.params['lang'])
			bot.privnotice("reloaded %s langs in %.4f ms", langs, t)
		if not cur.params.arguments(): return
	
	if cur.params['replies']:
		module=File("replies.py", "lang").load()
		self.replies = module

	if cur.args == "bot":
		import bot
		exec("reload(bot)")
		return
	short_names={
		"fr": "freenode",
		"wm": "wikimedia",
		"cm": "common"
	}

	if "." in cur.args:
		folder, name = cur.args.split(".")
		folder=short_names[folder] if folder in short_names else bot.folders[0]
	else:
		folder = bot.folders[0]
		name = cur.args
	print cur.args, name, folder

	modules = os.path.join(os.getcwd(), folder)
	if not name:
		bot.privnotice("module name expected")
		return
	elif name+".py" not in os.listdir(modules):
		bot.privnotice("unknown module")
		return
	module = getattr(__import__("%s.%s" % (folder, name)), name)
	reload(module)
	bot.load._register(vars(module))
	bot.load._bindrules()
	for priority in bot.commands:
		bot.commands[priority].update(bot.load.commands[priority])

	if hasattr(module, '__file__'):
		mtime = os.path.getmtime(module.__file__)
		modified = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(mtime))
	else: modified = 'unknown'
	msg = bot.translate('%r (version: %s)')
	msg = msg % (module, modified)
	bot.reply(msg)
reload_.rule = "reload"
reload_.limit=10
