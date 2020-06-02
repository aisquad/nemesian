# Copyright (C) 1999--2002  Joel Rosdahl
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inself., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
#
# Joel Rosdahl <joel@rosdahl.net>
#
# $Id: ircbot.py,v 1.23 2008/09/11 07:38:30 keltus Exp $

"""ircbot -- Simple IRC bot library.

This module contains a single-server IRC bot class that can be used to
write simpler bots.
"""

import os, random, re, sys, time
from UserDict import UserDict

from irclib import ServerConnectionError
from irclib import SimpleIRCClient, irc_lower, parse_channel_modes, is_channel

from util.functions import Load, _trans, Dicts
from lang import replies

class SingleServerIRCBot(SimpleIRCClient):
	"""A single-server IRC bot class.

	The bot tries to reconnect if it is disconnected.

	The bot keeps track of the channels it has joined, the other
	clients that are present in the channels and which of those that
	have operator or voice modes.  The "database" is kept in the
	self.channels attribute, which is an IRCDict of Channels.
	"""
	def __init__(self, irc_data, extended=None, reconnection_interval=60):
		"""Constructor for SingleServerIRCBot objects.

		Arguments:

			server_list -- A list of tuples (server, port) that
						   defines which servers the bot should try to
						   connect to.

			nickname -- The bot's nickname.

			realname -- The bot's realname.

			reconnection_interval -- How long the bot should wait
									 before trying to reconnect.

			dcc_connections -- A list of initiated/accepted DCC
			connections.
		"""

		SimpleIRCClient.__init__(self)
		self.channels = IRCDict()
		self.irc_data = irc_data
		self.extended = extended

		reconnection_interval = irc_data['reconnection_interval']
		if not reconnection_interval or reconnection_interval < 0:
			reconnection_interval = 2**31
		self.reconnection_interval = reconnection_interval
		self.label = irc_data['label']
		self.folders = irc_data['folders']
		self.triggers = irc_data['triggers']
		self.otherbots = irc_data['otherbots']

		for i in ["disconnect", "join", "kick", "mode",
				  "namreply", "nick", "nicknameinuse",
				  "part", "quit", "welcome", "320",
				  "endofwhois", "nosuchnick"]:
			self.connection.add_global_handler(
				i,
				getattr(self, "_on_" + i),
				-10
			)
		self.commands = {}
		self.replies = replies
		self.nicks = {}

	def _connected_checker(self):
		"""[Internal]"""
		if not self.is_connected():
			self.execute_delayed(
				self.reconnection_interval,
				self._connected_checker
			)
			self.jump_server()

	def _connect(self):
		"""[Internal]"""
		try:
			self.connect(self.irc_data, self.extended)
			for folder in self.irc_data['folders']:
				print "loading from %s folder" % folder
				self.load = Load(folder)
				if not self.commands:
					self.commands.update(self.load.commands)
				else:
					for priority in self.commands:
						self.commands[priority].update(self.load.commands[priority])
		except ServerConnectionError:
			pass

	def _on_disconnect(self, conn, evt):
		"""[Internal]"""
		self.channels = IRCDict()
		self.connection.execute_delayed(self.reconnection_interval,
										self._connected_checker)

	def _whoare(self, conn, evt):
		print "\n\n\t", self.connected, "\n\n\n"
		for nick in self.connected:
			c.whois([nick])

	def _on_320(self, conn, evt):
		#response from a whois
		args=e.arguments()
		nick=args[0]
		msg=args[1]
		if "is signed on as account" in msg:
			account=msg.split(" ")[-1]
			self.nicks[nick]=account
		elif "is identified to services" in msg:
			self.nicks[nick]=True

	def _on_endofwhois(self, conn, evt):
		nick = e._arguments[0]
		if not self.nicks.has_key(nick): self.nicks[nick]=""

	def _on_nosuchnick(self, conn, evt):
		msg=e._arguments[1]
		nick=""
		if self.nicks.has_key(nick): self.nicks.pop(nick)
		c.privmsg(self.vchan, msg)

	def _on_join(self, conn, evt):
		"""[Internal]"""
		ch = evt.msg
		nick = evt.nick
		if nick == conn.get_nickname():
			self.channels[ch] = Channel()
		self.channels[ch].add_user(nick)
		
		if nick == conn.get_nickname():
			if self.channels_extended.has_key(ch):
				self.channels[ch].lang = self.channels_extended[ch]['lang']
				self.channels[ch].proj = self.channels_extended[ch]['proj']
				self.channels[ch].reply = self.channels_extended[ch]['reply']
				self.channels[ch].report = self.channels_extended[ch]['report']
			if not hasattr(self.channels[ch], 'lang'):
				self.channels[ch].lang = "en"
			if not hasattr(self.channels[ch], 'proj'):
				self.channels[ch].proj = "meta.wikimedia.org"
			if not hasattr(self.channels[ch], 'reply'):
				self.channels[ch].reply = True
			if not hasattr(self.channels[ch], 'report'):
				self.channels[ch].report = False

	def _on_kick(self, conn, evt):
		"""[Internal]"""
		nick = evt.msg
		channel = evt._params[0]

		if nick == conn.get_nickname():
			del self.channels[channel]
		else:
			self.channels[channel].remove_user(nick)

	def _on_nicknameinuse(self, conn, evt):
		conn.nick(conn.get_nickname() + "_")
		conn.privmsg("NickServ",'GHOST %s %s' % (conn.get_nickname(), conn.u_password))
		conn.nick("%s +iw" % conn.nickname)
		conn.privmsg("NickServ", 'IDENTIFY %s' % conn.u_password)

	def _on_mode(self, conn, evt):
		"""[Internal]"""
		modes = parse_channel_modes(" ".join(evt._params[1:]))
		t = evt._params[0]
		if is_channel(t):
			ch = self.channels[t]
			for mode in modes:
				if mode[0] == "+":
					f = ch.set_mode
				else:
					f = ch.clear_mode
				f(mode[1], mode[2])
		else:
			# Mode on self... XXX
			pass

	def _on_namreply(self, conn, evt):
		"""[Internal]"""
		# evt._params[1] := "@" for secret channels,
		#                  "*" for private channels,
		#                  "=" for others (public channels)
		# evt._params[2] := channel
		# evt.msg       := nick list

		ch = evt._params[2]
		for nick in evt.msg.split():
			if nick[0] == "@":
				nick = nick[1:]
				self.channels[ch].set_mode("o", nick)
			elif nick[0] == "+":
				nick = nick[1:]
				self.channels[ch].set_mode("v", nick)
			else:
				self.channels[ch].add_user(nick)

	def _on_nick(self, conn, evt):
		"""[Internal]"""
		before = evt.nick
		after = evt.msg
		for ch in self.channels.values():
			if ch.has_user(before):
				ch.change_nick(before, after)
			if conn.igns.has_key(before):
				conn.igns[after]=conn.igns.pop(before)

	def _on_part(self, conn, evt):
		"""[Internal]"""
		nick = evt.nick
		channel = evt._params[0]

		if nick == conn.get_nickname():
			del self.channels[channel]
		else:
			self.channels[channel].remove_user(nick)

	def _on_quit(self, conn, evt):
		"""[Internal]"""
		nick = evt.nick
		for ch in self.channels.values():
			if ch.has_user(nick):
				ch.remove_user(nick)

	def _on_welcome(self, conn, evt):
		if self.label == "freenode":
			conn.privmsg("NickServ",'GHOST %s %s' % (conn.get_nickname(), conn.u_password))
			conn.nick("%s +iw" % conn.nickname)
			conn.privmsg("NickServ",'IDENTIFY %s' % conn.u_password)
		for ch in conn.def_channels:
			conn.join(ch)
		print "connected on %s" % conn.get_server_name()

	def on_ctcp(self, conn, evt):
		"""Default handler for ctcp events.

		Replies to VERSION and PING requests and relays DCC requests
		to the on_dccchat method.
		"""
		if evt.ctcp == "version" and evt.agent == "utility-bot":
			conn.ctcp_reply(evt.nick,
						 "VERSION %s" % self.get_version())
		elif evt.ctcp == "ping":
			if len(evt.msg) > 1:
				conn.ctcp_reply(evt.nick, "PING %s" % evt.msg)
		elif evt.ctcp == "dcc" and evt.msg.split(" ", 1)[0] == "chat":
			conn.on_dccchat(c, e)

	def on_dccchat(self, conn, evt):
		pass

	def get_version(self):
		"""Returns the bot version.

		Used when answering a CTCP VERSION request.
		"""
		return "ircbot.py by Joel Rosdahl <joel@rosdahl.net> modified by Igor REMOLAR <igor.remolar@gmail.com>"

	def jump_server(self, msg="Changing servers"):
		"""Connect to a new server, possibly disconnecting from the current.

		The bot will skip to next server in the server_list each time
		jump_server is called.
		"""
		if self.connection.is_connected():
			self.connection.disconnect(msg)

		#I can't understand this! --Pasqual 2010.03.11 03:25:47
		#self.server_list.append(self.server_list.pop(0))
		self._connect()

	def start(self):
		"""Start the bot."""
		self._connect()
		SimpleIRCClient.start(self)

	# -----------------------------------
	# ------- more usual commands -------
	# other commands require conn.x(*args)

	def die(self, msg="Does anything run wrong?"):
		"""Let the bot die.

		Arguments:

			msg -- Quit message.
		"""

		self.connection.disconnect(msg)
		sys.exit(0)

	def disconnect(self, msg="I'll be back!"):
		"""Disconnect the bot.

		The bot will try to reconnect after a while.

		Arguments:

			msg -- Quit message.
		"""
		self.connection.disconnect(msg)

	def pubaction(self, msg, *args):
		"""Send an action message to the current channel"""
		conn = self.connection
		evt = conn.event
		msg=self.translate(msg)
		if not "$nick" in evt.highlight: msg="%s%s" % (evt.highlight, msg)
		if args:
			conn.action(evt.channel, msg % args)
		else:
			conn.action(evt.channel, msg)

	def pubmsg(self, msg, *args):
		"""Send a message to the current channel"""
		conn = self.connection
		evt = conn.event
		msg=self.translate(msg)
		if not "$nick" in evt.highlight: msg="%s%s" % (evt.highlight, msg)
		if args:
			conn.privmsg(evt.channel, msg % args)
		else:
			conn.privmsg(evt.channel, msg)

	def pubnotice(self, msg, *args):
		"""Send a notice to the current channel"""
		conn = self.connection
		evt = conn.event
		msg=self.translate(msg)
		if args:
			conn.notice(evt.channel, msg % args)
		else:
			conn.notice(evt.channel, msg)

	def privaction(self, msg, *args):
		"""Send a private action message to the current nick"""
		conn = self.connection
		evt = conn.event
		msg=self.translate(msg)
		if args:
			conn.action(evt.nick, msg % args)
		else:
			conn.action(evt.nick, msg)

	def privmsg(self, msg, *args):
		"""Send a private message to the current nick"""
		conn = self.connection
		evt = conn.event
		msg=self.translate(msg)
		if args:
			conn.privmsg(evt.nick, msg % args)
		else:
			conn.privmsg(evt.nick, msg)

	def privnotice(self, msg, *args):
		"""Send a private notice to the current nick"""
		conn = self.connection
		evt = conn.event
		msg=self.translate(msg)
		if args:
			conn.notice(evt.nick, msg % args)
		else:
			conn.notice(evt.nick, msg)

	def reply(self, msg, *args):
		"""Send a message to someone/some channel using the same event type"""
		conn = self.connection
		evt = conn.event
		m = re.search("(pub|priv)(msg|notice|action)", evt.type)
		msg=self.translate(msg)
		if m:
			reply_obj="".join(m.groups())
			getattr(self, reply_obj)(msg, *args)
		else:
			if args:
				conn.privmsg(conn.def_channels[0], msg % (args))
			else:
				conn.privmsg(conn.def_channels[0], msg)
	
	def write(self, msg, *args):
		"""Send a message to someone/some channel using the same event type simulating a typewriting delay"""
		conn = self.connection
		evt = conn.event
		m = re.search("(pub|priv)(msg|notice|action)", evt.type)
		msg=self.translate(msg)
		if args:
			msg = msg % args
		typetime = float(len(msg))/5
		time.sleep(typetime)
		#msg="%s [%0.3f]" % (msg,typetime)
		if m:
			reply_obj="".join(m.groups())
			getattr(self, reply_obj)(msg)
		else:
			conn.privmsg(conn.def_channels[0], msg)

	def write_to(self, type, receptor, msg):
		"""Send a message/action/notice to someone/some channel"""
		conn = self.connection
		evt = conn.event
		msg=self.translate(msg)
		typetime = float(len(msg))/5
		#time.sleep(typetime)
		#msg="%s [%0.3f]" % (msg,typetime)
		type(receptor, msg)

	def choose_reply(self, prob, items, *args):
		dice = random.randint(0,100)
		if dice > prob:
			return
		dice = random.randint(0,len(items)-1)
		for tokens in items[dice]:
			time.sleep(tokens[2])
			if "%s" in tokens[1]:
				args = args[:tokens[1].count("%s")]
				if tokens[0]=='M': #Message
					self.pubmsg(tokens[1], args)
				elif tokens[0]=='A': #Action (/me)
					self.pubaction(tokens[1], args)
				elif tokens[0]=='N': #Notice
					self.pubnotice(tokens[1], args)
				elif tokens[0]=='m': #Message
					self.privmsg(tokens[1], args)
				elif tokens[0]=='a': #Action (/me)
					self.privaction(tokens[1], args)
				elif tokens[0]=='n': #Notice
					self.privnotice(tokens[1], args)
			else:
				if tokens[0]=='M':
					self.pubmsg(tokens[1])
				elif tokens[0]=='A':
					self.pubaction(tokens[1])
				elif tokens[0]=='N':
					self.pubnotice(tokens[1])	
				elif tokens[0]=='m':
					self.privmsg(tokens[1])
				elif tokens[0]=='a':
					self.privaction(tokens[1])
				elif tokens[0]=='n':
					self.privnotice(tokens[1])	
			time.sleep(tokens[3])

	def send_error(self):
		try:
			import traceback
			trace = traceback.format_exc()
			print trace
			lines = list(reversed(trace.splitlines()))

			report = [""]
			for line in lines:
				line = line.strip()
				f = re.search(r'File ".*[/\\](.+\.py.*)$', line)
				if f:
					report.append('"'+f.group(1))
					break
				else: report.append(line)
			else: report.append(self.translate('unknown source'))
			report.reverse()
			report="&B;%s&N;; &r;%s&N;; &b;%s&N;" % (report[0],report[1],report[2])
			self.ctrl_msg(report)
			#report=re.sub(r"\\x0[23]\d{0,2}", "",  ("%r" % report)[1:-1])
			#debug.write("=== %s ===\r\n%s\r\n" % (time.strftime("%d-%m-%y %H:%M"), report))
			#debug.flush()
		except: self.ctrl_msg("Got an error.")

	def translate(self, string):
		conn = self.connection
		lang =  self.channels[conn.event.channel].lang if conn.event.channel else "ca" #self.accounts[conn.event.nick]['lang']
		if conn.event.channel and "$proj" in string:
			string=string.replace("$proj", self.channels[conn.event.channel].proj) 
		return _trans(lang, string)

class IRCDict:
	"""A dictionary suitable for storing IRC-related things.

	Dictionary keys a and b are considered equal if and only if
	irc_lower(a) == irc_lower(b)

	Otherwise, it should behave exactly as a normal dictionary.
	"""

	def __init__(self, dict=None):
		self.data = {}
		self.canon_keys = {}  # Canonical keys
		if dict is not None:
			self.update(dict)

	def __repr__(self):
		return repr(self.data)

	def __cmp__(self, dict):
		if isinstance(dict, IRCDict):
			return cmp(self.data, dict.data)
		else:
			return cmp(self.data, dict)

	def __len__(self):
		return len(self.data)

	def __getitem__(self, key):
		return self.data[self.canon_keys[irc_lower(key)]]

	def __setitem__(self, key, item):
		if key in self:
			del self[key]
		self.data[key] = item
		self.canon_keys[irc_lower(key)] = key

	def __delitem__(self, key):
		ck = irc_lower(key)
		del self.data[self.canon_keys[ck]]
		del self.canon_keys[ck]

	def __iter__(self):
		return iter(self.data)

	def __contains__(self, key):
		return self.has_key(key)

	def clear(self):
		self.data.clear()
		self.canon_keys.clear()

	def copy(self):
		if self.__class__ is UserDict:
			return UserDict(self.data)
		import copy
		return copy.copy(self)

	def keys(self):
		return self.data.keys()

	def items(self):
		return self.data.items()

	def values(self):
		return self.data.values()

	def has_key(self, key):
		return irc_lower(key) in self.canon_keys

	def update(self, dict):
		for k, v in dict.items():
			self.data[k] = v

	def get(self, key, failobj=None):
		return self.data.get(key, failobj)


class Channel:
	"""A class for keeping information about an IRC channel.

	This class can be improved a lot.
	"""

	def __init__(self):
		# changed: only one dict is necessary, I changed:
		#   self.userdict[nick] = 1 to self.userdict[nick] = "u" for a user
		#   self.userdict[nick] = 1 to self.userdict[nick] = "o" for an oper
		#   self.userdict[nick] = 1 to self.userdict[nick] = "v" for a voiced

		self.userdict = IRCDict()
		self.modes = {}

	def users(self):
		"""Returns an unsorted list of the channel's users."""
		return self.userdict.keys()

	def opers(self):
		"""Returns an unsorted list of the channel's operators."""
		opers = []
		for user in self.userdict.keys():
			if self.userdict[user] == "o":
				opers.append(user)
		return opers

	def voiced(self):
		"""Returns an unsorted list of the persons that have voice
		mode set in the channel."""
		voiced = []
		for user in self.userdict.keys():
			if self.userdict[user] == "v":
				voiced.append(user)
		return voiced

	def has_user(self, nick):
		"""Check whether the channel has a user."""
		return nick in self.userdict

	def is_oper(self, nick):
		"""Check whether a user has operator status in the channel."""
		return self.userdict.get(nick, "") == "o"

	def is_voiced(self, nick):
		"""Check whether a user has voice mode set in the channel."""
		return self.userdict.get(nick, "") == "v"

	def add_user(self, nick):
		self.userdict[nick] = "u"

	def remove_user(self, nick):
		if nick in self.userdict:
			del self.userdict[nick]

	def change_nick(self, before, after):
		self.userdict[after] = self.userdict[before]
		# fixed: if user only swap case, dont delete her/him
		# else user will disappear from dict.
		# --Pasqual 2010.03.11 03:03:03 CEST
		if irc_lower(after) != irc_lower(before):
			del self.userdict[before]

	def set_mode(self, mode, value=None):
		"""Set mode on the channel.

		Arguments:

			mode -- The mode (a single-character string).

			value -- Value
		"""
		if mode in ("o", "v"):
			self.userdict[value] = mode
		else:
			self.modes[mode] = value

	def clear_mode(self, mode, value=None):
		"""Clear mode on the channel.

		Arguments:

			mode -- The mode (a single-character string).

			value -- Value
		"""
		try:
			if mode in ("o", "v"):
				del self.userdict[value]
			else:
				del self.modes[mode]
		except KeyError:
			pass

	def has_mode(self, mode):
		return mode in self.modes

	def is_moderated(self):
		return self.has_mode("m")

	def is_secret(self):
		return self.has_mode("s")

	def is_protected(self):
		return self.has_mode("p")

	def has_topic_lock(self):
		return self.has_mode("t")

	def is_invite_only(self):
		return self.has_mode("i")

	def has_allow_external_messages(self):
		return self.has_mode("n")

	def has_limit(self):
		return self.has_mode("l")

	def limit(self):
		if self.has_limit():
			return self.modes[l]
		else:
			return None

	def has_key(self):
		return self.has_mode("k")

	def key(self):
		if self.has_key():
			return self.modes["k"]
		else:
			return None
