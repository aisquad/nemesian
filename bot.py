#!/usr/bin/env python
import os, re, thread, time
from conf import cfg
from framework.irclib import ServerNotConnectedError
from framework.ircbot import SingleServerIRCBot
from util.functions import File, Path, Dicts

class Bot(SingleServerIRCBot):
	def __init__(self, irc_data, extended=None):
		SingleServerIRCBot.__init__(self, irc_data, extended)
		path = Path()
		root = path.preview(__file__)
		log_dir = path.join(root, "logs")
		self.accounts = Dicts("accounts", log_dir)
		self.channels_extended = Dicts("channels", log_dir)

	def on_welcome(self, conn, evt):
		self.init_time=time.time()
		self.thread_bots=Bots
		Bots.run()

	def on_privmsg(self, conn, evt):
		if self.label=="freenode":
			self.pubnotice("%s: %s" % (evt.nick,evt.msg))
		elif self.label=="wikimedia":
			FrBot.connection.privmsg(FrBot.connection.def_channels[0], "%s: %s OPTS: %s" % (evt.nick, evt.msg, evt.opts))

	def on_privnotice(self, conn, evt):
		if self.label=="freenode":
			if evt.agent == "services":
				msg=""
				if "This nickname is registered." in evt.msg:
					msg = evt.msg.split()
					msg.insert(2, "(%s)" % conn.get_nickname())
					msg=" ".join(msg)
				if not msg:msg=evt.msg
				self.ctrl_msg("<%s> %s" % (evt.nick, msg))

	def on_pubmsg(self, conn, evt):
		if self.label=="freenode":
			if evt.msg=="@users":
				conn.notice(evt.nick, self.channels[evt.channel].users())

			#conn.privmsg(evt.nick, evt.msg)
		elif self.label == "wikimedia":
			#FrBot.connection.privmsg(FrBot.connection.def_channels[0], "on_%s %s" % (evt._wm_change, evt.opts))
			pass

	def ctrl_msg(self, msg):
		conn = FrBot.connection
		evt = conn.event
		ctrl_chan=conn.def_channels[0]
		msg=self.translate(msg)
		conn.privmsg(ctrl_chan, msg)

	def reboot(self, msg="Ara torne :) ..."):
		for bot in Bots.args:
			print bot
			bot.disconnect(msg)
			bot.is_connected=False
		thread.interrupt_main()

class Servers:
	def __init__(self, *args):
		self.args=args

	def __call__(self, bot):
		for abot in self.args:
			if abot.label == bot:
				return abot

	def run(self):
		i=0
		for bot in self.args:
			i+=1
			if not hasattr(bot, "is_connected"):
				thread.start_new_thread(bot.start, ())
				bot.is_connected=True

try:
	FrBot = Bot(cfg.bot) #, {"localadress":"127.0.0.1", "localport":555666})
	WmBot = Bot(cfg.bot2)
	FrBot.is_connected=True
	Bots = Servers(FrBot, WmBot)
	FrBot.start()
except KeyboardInterrupt:
	pass
	for bot in Bots.args:
		if bot.is_connected:
			bot.die("O_O I hate Ctrl-C!!!")
except ServerNotConnectedError:
	for bot in Bots.args:
		bot.reconnect()
finally:
	pass
