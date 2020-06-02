# -*- coding: utf8 -*-
# help.py
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

import json, os, re, time, types
from random import randint, choice
from datetime import datetime

from dateutil.relativedelta import relativedelta as timedelta

from framework.irclib import irc_lower
from util.functions import *
from util.browser import B as Browser

#TODO
#afegir fn.channels[cur.channel]
def commands(bot, irc, cur):
	cmds=[]
	for priority in bot.commands:
		for func in bot.commands[priority]:
			fn = bot.commands[priority][func]
			if fn.evttypes != ("msg", "notice", "action"):
				continue
			elif fn.name.endswith("_"):
				continue
			elif hasattr(fn, "showas"):
				cmds.append(fn.showas)
			elif isinstance(fn.rule[0], basestring):
						cmds.append(fn.rule[0])
			else:
						cmds.append(fn.name)
	cmds = ", ".join(cmds).split(", ")
	msg = ", ".join(sorted(cmds))
	conj = bot.translate("and")
	msg += " %s %s" % (conj, cmds[-1])
	bot.reply("available commands: %s", msg)
commands.rule = "commands"
commands.channels = {"##bots-ca": "ordres"}

def help(bot, irc, cur):
	print ".help", cur.args
	if cur.args:
		for p in bot.commands:
			for f in bot.commands[p]:
				fn = bot.commands[p][f]
				if isinstance(fn.rule, bool): fn.rule = [fn.rule] #todo: fix this bug!!!
				for s in fn.rule+fn.aliases+[fn.name]:
					if isinstance(s, basestring):
						if s == cur.args:
							bot.reply(fn.help)
							return
						elif hasattr(fn, "showas") and cur.args in fn.showas.split(","):
							bot.reply(fn.help)
							return
	else:
		link = bot.translate("help link")
		bot.reply("See %s", link)
help.rule = "help"
help.limit = 10

