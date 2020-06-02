# -*- coding: utf8 -*-
# brackets.py

import os, re, time
from framework.irclib import irc_lower
from random import randint, choice

from util.functions import *

"""
Function attributes:
* load: boolean. Optional. If False the function will not load.
* name: string. Optional.
* priority: string. Optional. Three values are available: "high", "medium" or "low", default value: "medium".
* thread: boolean. Optional. If True, function will work by starting a thread.
* rule: string or regexp object. Requered.
* aliases: list of string or regexp objects. Optional.
* sentence: boolean. Optional. If True, pattern is searched on whole message, else pattern is a command, it begins
  the msg with a sign.
"""

def brackets(bot, irc, cur):
    """Wikilinks. It returns an url link from a wikilink. You can use [[X]] to redirect to a page or {{X}} to a template, it accepts lang codes and some prefixes. More: $more""" 
    links=re.finditer(ur"([\w\-:!]*(?:\{\{|\[\[)(?:[^\]}]+)(?:\}\}|\]\]))", cur.msg)
    mxm=0
    for m in links:
        if re.search("!(?:\[\[|\{\{)", m.group(1)): continue
        if mxm==3: break
        if m.group(1)=="{{fet}}":
            bot.reply(u"Quina gent més eficient!!!")
            continue
        url=WikiLink(m.group(1)).to_url()
        if url:
            bot.pubmsg(url)
        mxm+=1
brackets.rule=re.compile(r"(?:\{\{|\[\[)([^\]}]+)(?:\}\}|\]\])")
brackets.thread = True
brackets.fullmsg = True
