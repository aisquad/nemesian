#-*- coding:utf8 -*-
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
* skip_sentinel: skip _sentinel instance
* limit
* channels
* url
* showas
"""

import re
from util.functions import *
from util.browser import B as Browser

def channels(bot, irc, cur):
	print cur.params
	chan = cur.params['chan']
	if not cur.params['del'] and cur.params['chan']:
		bot.channels_extended.update(
			chan, {
					'lang': cur.params['lang'],
					'proj': cur.params['proj'],
					'reply': cur.params['reply'],
					'report': cur.params['report']
				}
		)
		bot.channels_extended.save()
		bot.channels[chan].lang = cur.params['lang']
		bot.channels[chan].proj = cur.params['proj']
		bot.channels[chan].reply = cur.params['reply']
		bot.channels[chan].report = cur.params['report']
	elif cur.params['del']:
		for chan, props in bot.channels_extended.iteritems():
			print chan, props
		bot.reply("chan: %s deleted.", chan)
channels.rule="channels"

def properties(bot, irc, cur):
	chan = cur.args
	if chan in bot.channels_extended.keys():
		chan_props = bot.channels_extended[chan]
		bot.reply("lang: %s, proj: %s, reply: %s, report: %s", chan_props['lang'], chan_props['proj'], chan_props['reply'], chan_props['report'])
	else:
		bot.reply("No such channel.")
properties.rule = "props"

def accounts(bot, irc, cur):
	account = cur.params['user'] or cur.params['u']
	lang = cur.params['lang'] or cur.params['l']
	access = cur.params['access'] or cur.params['a']
	wikiuser = cur.params['wiki'] or cur.params['w']
	project = cur.params['proj'] or cur.params['p']
	bot.accounts.update(
		account, {
			'lang': lang,
			'access': access,
			'wiki': wikiuser,
			'project': project
		}
	)
	bot.accounts.save()
accounts.rule = "acc"

	