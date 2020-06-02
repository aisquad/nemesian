# -*- coding: utf8 -*-
# numbers.py
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
from __future__ import division
import os, re, time
from framework.irclib import irc_lower
from random import randint, choice

from util.functions import *


def calc(bot, irc, cur):
	"""Calcute parameters. Use '(', ')', operators ('*', '/', '+', '-', '^' for power, ':' for modulo) and numbers, putting '=' at beginning of the line."""
	#print cur.params["%ARGS%"]
	c = cur.dict['string'].replace("^","**").replace(":","%").replace(u"·","*")
	if c.count("**")>1:
		bot.privnotice("overload expression")
		return
	c = eval(c)
	bot.reply(str(c))
calc.rule = re.compile(u"^(?:$trigger)?=(?P<string>[() +\-.*:%·/^\d]+)$")
calc.fullmsg = True
calc.access=["tester"]
