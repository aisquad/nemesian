# -*- coding: utf8 -*-
# humanlike.py
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

def type_(bot, irc, cur):
	print cur.args
	bot.write(cur.args)
type_.rule = "type"
type_.access= ["staff"]

def send_to_(bot, irc, cur):
	tokens = cur.args.split(" ")
	type="";receptor=""

	if tokens[0].startswith(":") and tokens[0][1] in "an":
		type = tokens[0]

	if type:
		if type == ":a": type = irc.action
		elif type == ":n": type = irc.notice
	else:
		receptor = tokens[0]
		msg = " ".join(tokens[1:])
		type = irc.privmsg
	
	if not receptor:
		receptor = tokens[1]
		msg = " ".join(tokens[2:])

	if not receptor.startswith("@") and not receptor.startswith("#"):
		receptor = def_chan
		msg = " ".join(tokens)
	elif receptor.startswith("@"):
		receptor=receptor[1:]
	
	bot.write_to(type, receptor, msg)
send_to_.rule = [":","sendto"]
send_to_.limit = 15
send_to_.access= ["staff"]

def_chan =""
def default_chan_(bot, irc, cur):
	global def_chan
	def_chan = cur.args
default_chan_.rule = "defchan"
default_chan_.access= ["staff"]
