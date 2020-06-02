# -*- coding: utf8 -*-
# report.py

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

def join(bot, irc, cur):
	if cur.nick != irc.get_nickname():
		bot.ctrl_msg("%s has joined %s" % (cur.nick, cur.channel))
join.rule="join"
join.evttypes=("join",)

def leave(bot, irc, cur):
	if cur.nick != irc.get_nickname():
		bot.ctrl_msg("%s has leaved %s: %s" % (cur.nick, cur.channel or bot.label, cur.msg))
leave.rule=["part","quit","disconnect"]
leave.evttypes=("part","quit","disconnect")
leave.skip_sentinel=True
