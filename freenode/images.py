#!/usr/bin/env python
# -*- coding: utf8 -*-
# ping.py

import re
from util.globals import *

"""
Function attributes:
* load: boolean. Optional. If False the function will not load.
* name: string. Optional.
* priority: string. Optional. Three values are available: "high", "medium" or "low",
  default value: "medium".
* thread: boolean. Optional. If True, function will work by starting a thread.
* rule: string or regexp object. Required.
* aliases: list of string or regexp objects. Optional.
* sentence: boolean. Optional. If True, pattern is searched on whole message, else
  pattern is a command, the message must begin with a sign.
"""

def img(bot, irc, cur):
	site = cur.args
	bot.reply(site)
img.rule="img"
