# -*- coding: utf8 -*-
# tests.py

import json, os, re, time
from datetime import datetime
from random import randint, choice

from dateutil.relativedelta import relativedelta as timedelta

from framework.irclib import irc_lower
from util.functions import *
from util.browser import B as Browser

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

def join_chan_(bot, irc, cur):
	def check_chan(chan):
		if bot.channels.has_key(chan):
			bot.reply("I'm already in this channel")
			return True
		return False

	if " " in cur.args:
		chan = cur.args.split(" ",1)[0]
		msg = cur.args.split(" ",1)[1]
		if check_chan(chan): return
		irc.join(chan)
		time.sleep(3)
		irc.privmsg(chan, msg)
	else:
		if check_chan(cur.args): return
		irc.join(cur.args)
join_chan_.rule=["j", "join"]
join_chan_.access=["staff"]

def part_chan_(bot, irc, cur):
	def check_chan(chan):
		if not bot.channels.has_key(chan):
			bot.reply("I'm not in this channel")
			return False
		return True
		
	if " " in cur.args:
		chan, msg = cur.args.split(" ",1)
		if not check_chan(chan): return
		irc.part(chan, msg)
	else:
		if not check_chan(cur.args): return
		irc.part(cur.args)
part_chan_.rule=["p", "part"]
part_chan_.access=["staff"]