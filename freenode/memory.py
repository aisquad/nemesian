#!/usr/bin/env python
# -*- coding: utf8 -*-
# replace.py

import re
from difflib import get_close_matches
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

def substitute_(bot, irc, cur):
	old=cur.dict["old"]
	new=cur.dict["new"]
	if bot.notes.has_key(cur.nick) and bot.notes[cur.nick].has_key(cur.channel):
		for msg in reversed(bot.notes[cur.nick][cur.channel]):
			if old in msg:
				repeat=cur.dict['repeat']
				max=msg.count(repeat)
				if not repeat or repeat=="*":
					msg=msg.replace(old, new)
				elif cur.dict['repeat'].isdigit():
					repeat=int(repeat)
					if repeat>max:repeat=max
					msg=msg.replace(old, new, int(repeat))

				bot.reply(u"$nick meant: %s", msg)
				break
substitute_.rule=re.compile("^s/(?P<old>[^/]+)/(?P<new>[^/]+)/(?P<repeat>(?:\d+|\*)?)$")
substitute_.fullmsg=True
substitute_.limit=2

def mistake_(bot, irc, cur):
	if bot.notes.has_key(cur.nick) and bot.notes[cur.nick].has_key(cur.channel):
		for msg in reversed(bot.notes[cur.nick][cur.channel][:-1]):
			result = get_close_matches(cur.dict['good'].lower(), msg.split(" "), n=10)
			if result:
				msg = msg.replace(result[0], cur.dict['good'].strip("*"))
				bot.reply("$nick meant: %s", msg)
				break
mistake_.rule=re.compile("^(?P<good>\*[^ ]+|[^ ]+\*)$")
mistake_.fullmsg=True

def memory(bot, irc, cur):
	if not hasattr(bot, "notes"):
		bot.notes={}
	if cur.type=="pubmsg":
		if bot.notes.has_key(cur.nick):
			if not cur.msg.startswith("s/") and not cur.msg.startswith(irc.triggers[1:-1].replace("\\","")) and not cur.msg.startswith(irc.get_nickname()):
				if bot.notes[cur.nick].has_key(cur.channel):
					bot.notes[cur.nick][cur.channel].append(cur.msg)
				else:
					bot.notes[cur.nick]={cur.channel:[cur.msg]}
			if bot.notes[cur.nick].has_key(cur.channel):
				if len(bot.notes[cur.nick][cur.channel]) > 5: bot.notes[cur.nick][cur.channel]=bot.notes[cur.nick][cur.channel][1:]
		else:
			bot.notes[cur.nick]={cur.channel:[cur.msg]}
	elif cur.type in ("quit", "disconnect", "part"):
		bot.reply("%s has %s %s", cur.nick, cur.type, cur.channel or bot.label)
		if cur.nick in bot.notes:
			del bot.notes[cur.nick]
memory.rule=False
memory.evttypes="*"
memory.priority="high"
memory.skip_sentinel=True