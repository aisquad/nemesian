# -*- coding: utf8 -*-
# ping.py
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
* evttypes: 
* skip_sentinel: skip sentinel instance
* limit
* channels
* url
"""

import re
from util.functions import *

def ping(bot, irc, cur):
	if cur.dict["cmd"]:
		ping = cur.dict["cmd"]
		ping=ping.replace("i","o")
		ping=ping.replace("I","O")
		ping=ping.replace("1","0")
		if not cur.highlight:
			ping="$nick: %s" % (ping)
		bot.pubmsg(ping)
ping.rule = re.compile("^($both)?(?P<cmd>p[i1]ng!?)$")
ping.fullmsg = True
ping.limit=10