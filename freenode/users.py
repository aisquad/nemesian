# -*- coding: utf8 -*-
# users.py

import re
from util.functions import *

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

def users(bot, irc, cur):
	"""Show users of a given channel. Syntax: .users #channel"""
	cmd = cur.dict['cmd']
	ch = cur.dict['chan'] or cur.channel or irc.def_channels[0]
	try:
		if cmd == "users":
			users = bot.channels[ch].users()
		elif cmd == "opers":
			users = bot.channels[ch].opers()
		elif cmd == "voiced":
			users = bot.channels[ch].voiced()
		msg = join_userlist(users, bot.channels[ch].lang)
	except KeyError:
		msg = "I'm not in this channel."
	except IndexError:
		msg = "There is no %s in this channel." % cmd
	bot.reply(msg)
users.rule = re.compile("^($both)(?P<cmd>(?:(?:us|op)ers|voiced))(?: (?P<chan>.+))?$")
users.showas = "users, opers, voiced"
users.fullmsg = True