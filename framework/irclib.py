#-*- coding:utf8 -*-
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
#
# keltus <keltus@users.sourceforge.net>
#
# $Id: irclib.py,v 1.47 2008/09/25 22:00:59 keltus Exp $
#
# This is a version with some fixes and implementations to use the
# bot on freenode and wikimedia networks.
# $Id: irclib.py,v 2.0 2010/03/11 00:28:07 Pasqual@cawiki $

"""irclib -- Internet Relay Chat (IRC) protocol client library.

This library is intended to encapsulate the IRC protocol at a quite
low level.  It provides an event-driven IRC client framework.  It has
a fairly thorough support for the basic IRC protocol, CTCP, DCC chat,
but DCC file transfers is not yet supported.

In order to understand how to make an IRC client, I'm afraid you more
or less must understand the IRC specifications.  They are available
here: [IRC specifications].

The main features of the IRC client framework are:

    * Abstraction of the IRC protocol.
    * Handles multiple simultaneous IRC server connections.
    * Handles server PONGing transparently.
    * Messages to the IRC server are done by calling methods on an IRC
      connection object.
    * Messages from an IRC server triggers events, which can be caught
      by event handlers.
    * Reading from and writing to IRC server sockets are normally done
      by an internal select() loop, but the select()ing may be done by
      an external main loop.
    * Functions can be registered to execute at specified times by the
      event-loop.
    * Decodes CTCP tagging correctly (hopefully); I haven't seen any
      other IRC client implementation that handles the CTCP
      specification subtilties.
    * A kind of simple, single-server, object-oriented IRC client class
      that dispatches events to instance methods is included.

Current limitations:

    * The IRC protocol shines through the abstraction a bit too much.
    * Data is not written asynchronously to the server, i.e. the write()
      may block if the TCP buffers are stuffed.
    * There are no support for DCC file transfers.
    * The author haven't even read RFC 2810, 2811, 2812 and 2813.
    * Like most projects, documentation is lacking...

.. [IRC specifications] http://www.irchelp.org/irchelp/rfc/
"""

import bisect, random, re, select, socket, string, sys, thread, time, types
from datetime import datetime
from util.easy_params import GetParams
from util.recent_changes import rc_events
from util.functions import colors, decode, encode, escape_for_regexp, wildcard_to_regexp

_version = 0, 2, 0
_debug = 0
_debug_rcv_msg = 0
_debug_details = 0
_debug_send_msg = 0

# TODO
# ----
# (maybe) thread safety
# (maybe) color parser convenience functions
# documentation (including all event types)
# (maybe) add awareness of different types of ircds
# send data asynchronously to the server (and DCC connections)
# (maybe) automatically close unused, passive DCC connections after a while

# NOTES
# -----
# connection.quit() only sends QUIT to the server.
# ERROR from the server triggers the error event and the disconnect event.
# dropping of the connection triggers the disconnect event.

class IRCError(Exception):
	"""Represents an IRC exception."""
	pass


class IRC:
	"""Class that handles one or several IRC server connections.

	When an IRC object has been instantiated, it can be used to create
	Connection objects that represent the IRC connections.  The
	responsibility of the IRC object is to provide an event-driven
	framework for the connections and to keep the connections alive.
	It runs a select loop to poll each connection's TCP socket and
	hands over the sockets with incoming data for processing by the
	corresponding connection.

	The methods of most interest for an IRC client writer are server,
	add_global_handler, remove_global_handler, execute_at,
	execute_delayed, process_once and process_forever.

	Here is an example:

		import irclib
		irc = irclib.IRC()
		server = irc.server()
		server.connect(\"irc.some.where\", 6667, \"my_nickname\")
		server.privmsg(\"a_nickname\", \"Hi there!\")
		irc.process_forever()

	This will connect to the IRC server irc.some.where on port 6667
	using the nickname my_nickname and send the message \"Hi there!\"
	to the nickname a_nickname.
	"""

	def __init__(self, fn_to_add_socket=None, fn_to_remove_socket=None, fn_to_add_timeout=None):
		"""Constructor for IRC objects.

		Optional arguments are fn_to_add_socket, fn_to_remove_socket
		and fn_to_add_timeout.  The first two specify functions that
		will be called with a socket object as argument when the IRC
		object wants to be notified (or stop being notified) of data
		coming on a new socket.  When new data arrives, the method
		process_data should be called.  Similarly, fn_to_add_timeout
		is called with a number of seconds (a floating point number)
		as first argument when the IRC object wants to receive a
		notification (by calling the process_timeout method).  So, if
		e.g. the argument is 42.17, the object wants the
		process_timeout method to be called after 42 seconds and 170
		milliseconds.

		The three arguments mainly exist to be able to use an external
		main loop (for example Tkinter's or PyGTK's main app loop)
		instead of calling the process_forever method.

		An alternative is to just call ServerConnection.process_once()
		once in a while.
		"""

		if fn_to_add_socket and fn_to_remove_socket:
			self.fn_to_add_socket = fn_to_add_socket
			self.fn_to_remove_socket = fn_to_remove_socket
		else:
			self.fn_to_add_socket = None
			self.fn_to_remove_socket = None

		self.fn_to_add_timeout = fn_to_add_timeout
		self.connections = []
		self.handlers = {}
		self.delayed_commands = [] # list of tuples in the format (time, function, arguments)

		self.add_global_handler("ping", _ping_ponger, -42)

	def server(self):
		"""Creates and returns a ServerConnection object."""

		c = ServerConnection(self)
		self.connections.append(c)
		return c

	def process_data(self, sockets):
		"""Called when there is more data to read on connection sockets.

		Arguments:

			sockets -- A list of socket objects.

		See documentation for IRC.__init__.
		"""
		for s in sockets:
			for c in self.connections:
				if s == c._get_socket():
					c.process_data()

	def process_timeout(self):
		"""Called when a timeout notification is due.

		See documentation for IRC.__init__.
		"""
		t = time.time()
		while self.delayed_commands:
			if t >= self.delayed_commands[0][0]:
				self.delayed_commands[0][1](*self.delayed_commands[0][2])
				del self.delayed_commands[0]
			else:
				break

	def process_once(self, timeout=0):
		"""Process data from connections once.

		Arguments:

			timeout -- How long the select() call should wait if no
					   data is available.

		This method should be called periodically to check and process
		incoming data, if there are any.  If that seems boring, look
		at the process_forever method.
		"""
		sockets = map(lambda x: x._get_socket(), self.connections)
		sockets = filter(lambda x: x != None, sockets)
		if sockets:
			(i, o, e) = select.select(sockets, [], [], timeout)
			self.process_data(i)
		else:
			time.sleep(timeout)
		self.process_timeout()

	def process_forever(self, timeout=0.2):
		"""Run an infinite loop, processing data from connections.

		This method repeatedly calls process_once.

		Arguments:

			timeout -- Parameter to pass to process_once.
		"""
		while 1:
			self.process_once(timeout)

	def disconnect_all(self, message=""):
		"""Disconnects all connections."""
		for c in self.connections:
			c.disconnect(message)

	def add_global_handler(self, event, handler, priority=0):
		"""Adds a global handler function for a specific event type.

		Arguments:

			event -- Event type (a string).  Check the values of the
			numeric_events dictionary in irclib.py for possible event
			types.

			handler -- Callback function.

			priority -- A number (the lower number, the higher priority).

		The handler function is called whenever the specified event is
		triggered in any of the connections.  See documentation for
		the Event class.

		The handler functions are called in priority order (lowest
		number is highest priority).  If a handler function returns
		\"NO MORE\", no more handlers will be called.
		"""
		if not event in self.handlers:
			self.handlers[event] = []
		bisect.insort(self.handlers[event], ((priority, handler)))

	def remove_global_handler(self, event, handler):
		"""Removes a global handler function.

		Arguments:

			event -- Event type (a string).

			handler -- Callback function.

		Returns 1 on success, otherwise 0.
		"""
		if not event in self.handlers:
			return 0
		for h in self.handlers[event]:
			if handler == h[1]:
				self.handlers[event].remove(h)
		return 1

	def execute_at(self, at, function, arguments=()):
		"""Execute a function at a specified time.

		Arguments:

			at -- Execute at this time (standard \"time_t\" time).

			function -- Function to call.

			arguments -- Arguments to give the function.
		"""
		self.execute_delayed(at-time.time(), function, arguments)

	def execute_delayed(self, delay, function, arguments=()):
		"""Execute a function after a specified time.

		Arguments:

			delay -- How many seconds to wait.

			function -- Function to call.

			arguments -- Arguments to give the function.
		"""
		bisect.insort(self.delayed_commands, (delay+time.time(), function, arguments))
		if self.fn_to_add_timeout:
			self.fn_to_add_timeout(delay)

	def dcc(self, dcctype="chat"):
		"""Creates and returns a DCCConnection object.

		Arguments:

			dcctype -- "chat" for DCC CHAT connections or "raw" for
					   DCC SEND (or other DCC types). If "chat",
					   incoming data will be split in newline-separated
					   chunks. If "raw", incoming data is not touched.
		"""
		c = DCCConnection(self, dcctype)
		self.connections.append(c)
		return c

	def _handle_event(self, connection, event):
		"""[Internal]"""
		h = self.handlers
		for handler in h.get("all_events", []) + h.get(event.type, []):
			if handler[1](connection, event) == "NO MORE":
				return

	def _remove_connection(self, connection):
		"""[Internal]"""
		self.connections.remove(connection)
		if self.fn_to_remove_socket:
			self.fn_to_remove_socket(connection._get_socket())


class Connection:
	"""Base class for IRC connections.

	Must be overridden.
	"""
	def __init__(self, irclibobj):
		self.irclibobj = irclibobj

	def _get_socket():
		raise IRCError, "Not overridden"

	##############################
	### Convenience wrappers.

	def execute_at(self, at, function, arguments=()):
		self.irclibobj.execute_at(at, function, arguments)

	def execute_delayed(self, delay, function, arguments=()):
		self.irclibobj.execute_delayed(delay, function, arguments)


class ServerConnectionError(IRCError):
	pass

class ServerNotConnectedError(ServerConnectionError):
	pass

line_re = re.compile("^(?:(?P<prefix>[^ ]+) +)?(?P<command>[^: ]+)(?: *(?P<argument>.+))?")
ctcp_re = re.compile("^\001.+\001$")
line_sep_re = re.compile("\r?\n")
class ServerConnection(Connection):
	"""This class represents an IRC server connection.

	ServerConnection objects are instantiated by calling the server
	method on an IRC object.
	"""

	def __init__(self, irclibobj):
		Connection.__init__(self, irclibobj)
		self.connected = 0  # Not connected yet.
		self.socket = None
		self.ssl = None
		
		self._features = {
			'CHANNELLEN': 200,
			'CHANTYPES': tuple('#&'),
			'MODES': 3,
			'NICKLEN': 9,
			'PREFIX': '(ov)@+'
		}

		#filter: prevent excess flood
		self.verbosity = {"lastmsg": time.time(), "acculen": 0}

		#sentinel: prevent attacks and abuses
		self.requests = {} #{nick: {last_cmd: (last_time, times)}}
		self.igns = {} #{nick: (last_time, ignored_time_penalty)}

		#initial values
		self.event = None

	def connect(self, irc_data, extended=None):
		"""Connect/reconnect to a server.

		Arguments:

			server -- Server name.

			port -- Port number.

			nickname -- The nickname.

			password -- Password (if any).

			username -- The username.

			ircname -- The IRC name ("realname").

			localaddress -- Bind the connection to a specific local IP address.

			localport -- Bind the connection to a specific local port.

			ssl -- Enable support for ssl.

			ipv6 -- Enable support for ipv6.

		This function can be called to reconnect a closed connection.

		Returns the ServerConnection object.
		"""
		if self.connected:
			self.disconnect("Changing servers")

		#initializing data
		self.help_link = irc_data['help_url']
		i_server = irc_data['server']
		i_channels = irc_data['channels']
		i_user = irc_data['user']
		if not extended:
			self.localaddress = ""; self.localport = 0; self.ssl = False; self.ipv6 = False
		else:
			self.localaddress = extended.get('localaddress', "")
			self.localport = extended.get('localport', 0)
			self.ssl = extended.get('ssl', False)
			self.ipv6 = extended.get('ipv6', False)

		#server data
		self.real_server_name = ""
		self.server = i_server['host']
		self.port = i_server['port']
		self.s_password = i_server.get('password', None)
		self.localhost = socket.gethostname()
		self.def_channels=i_channels

		#user data
		self.real_nickname = i_user['nickname']
		self.nickname = i_user['nickname']
		self.username = i_user.get('username', self.nickname)
		self.ircname = i_user.get('ircname', self.nickname)
		self.u_password = i_user.get('password', "")

		self.owner = irc_data['owner']

		if self.ipv6:
			self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		else:
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.socket.bind((self.localaddress, self.localport))
			self.socket.connect((self.server, self.port))
			if self.ssl:
				self.ssl = socket.ssl(self.socket)
		except socket.error, x:
			self.socket.close()
			self.socket = None
			raise ServerConnectionError, "Couldn't connect to socket: %s" % x
		self.connected = 1
		self.previous_buffer = ""
		self.handlers = {}

		# Log on...
		if self.s_password:
			self.pass_(self.s_password)
		self.nick(self.nickname)
		self.user(self.username, self.ircname)

		self.previous_buffer = ""
		self.label = irc_data['label']
		self.triggers = irc_data['triggers']
		
		return self

	def close(self):
		"""Close the connection.

		This method closes the connection permanently; after it has
		been called, the object is unusable.
		"""

		self.disconnect("Closing object")
		self.irclibobj._remove_connection(self)

	def _get_socket(self):
		"""[Internal]"""
		return self.socket

	def get_server_name(self):
		"""Get the (real) server name.

		This method returns the (real) server name, or, more
		specifically, what the server calls itself.
		"""

		if self.real_server_name:
			return self.real_server_name
		else:
			return ""

	def get_nickname(self):
		"""Get the (real) nick name.

		This method returns the (real) nickname.  The library keeps
		track of nick changes, so it might not be the nick name that
		was passed to the connect() method.  """

		return self.real_nickname
	
	def get_help_link(self):
		return self.help_link

	def _parse_featurelist(self, line):
		"""
		based on Twister, but I have modified the regexp, and so the results.
		"""
		features=re.finditer("(?P<key>[A-Z]+)(?:=(?P<value>[^ ]+))?", line)
		for items in features:
			key, value = items.groups()
			parameters = value.split(",") if value and "," in value else value if value else True
			self._features[key]=parameters

	def process_data(self):
		try:
			if self.ssl:
				new_data = self.ssl.read(2**14)
			else:
				new_data = self.socket.recv(2**14)
		except socket.error, x:
			# The server hung up.
			self.disconnect("Connection reset by peer")
			return
		if not new_data:
			# Read nothing: connection must be down.
			self.disconnect("Connection reset by peer")
			return

		lines = line_sep_re.split("%s%s" % (self.previous_buffer, new_data))
		self.previous_buffer = lines.pop()
		for line in lines:
			utf8_line = decode(line)
			ctcp=False
			m = line_re.search(utf8_line)
			if m:
				prefix, command, arguments = m.groups()
			else:
				self.disconnect("Connection reset by peer - unreadable line")
			raw_line=line
			command = command.lower()
			cmd = "\t%s" % command
			command = numeric_events.get(command, command)
			cmd += " --> %s" % command

			if ":" in arguments:
				params, msg = arguments.split(":",1)
				params = params.strip().split()
			else:
				params, msg = [arguments], ""

			self.parsable=False
			channel=params[0] if params else ""
			if command in ("privmsg", "notice"):
				self.parsable=True
				channel = params[0] if is_channel(params[0]) else ""
				cmd_type = command.replace("priv", "")
				field = "pub" if is_channel(params[0]) else "priv"
				command = "%s%s" % (field, cmd_type)
				cmd += " --> %s" % command
				if ctcp_re.search(msg):
					self.parsable == False
					command = "ctcp" if field == "priv" else "ctcpreply"
					cmd += " --> %s" % command
					ctcp, msg = msg.split(" ", 1) if " " in msg else [msg, ""]
					ctcp=ctcp.replace("\001","").lower()
					msg=msg.replace("\001","")
					if ctcp=="action":
						cmd_type = "action"
						command = "%s%s" % (field, cmd_type)
						cmd += " --> %s" % command
			elif command == "mode":
				params=params[0].split()
				if not is_channel(channel):
					command = "umode"
			elif command == "featurelist":
				self._parse_featurelist(line)

			# Record the nickname in case the client changed nick
			# in a nicknameinuse callback.
			if command == "nick" and prefix.startswith(":") and prefix[1:].split("!", 1)[0] == self.real_nickname:
				self.real_nickname = msg
			elif command == "welcome":
				self.real_server_name = prefix
				self.real_nickname = params[0]
			elif command == "namreply":
				channel = params[2]
			elif command == "join":
				channel = msg

			if _debug or _debug_details:
				print line
				print cmd

			self.event=Event(
				(self.label, self.parsable, raw_line, self.triggers, self.real_nickname),
				command,  # the type of the event.
				params,   # the parameter between command and message.
				msg,      # the message.
				prefix,   # the nick whom the bot can reply to.
				channel,  # the channel where a message was recieved, if any.
				ctcp,     # the type of ctcp
			)
			self._handle_event(self.event)

	def _handle_event(self, event):
		"""[Internal]"""
		self.irclibobj._handle_event(self, event)
		if event.type in self.handlers:
			for fn in self.handlers[event.type]:
				fn(self, event)

	def _filter(self, msg):
		"""[Internal]"""
		# --Pasqual 2010-03-18 21:28:45
		# prevent flood due to sending long messages
		#   control string length
		#   control consecutive message rate

		msg=msg.split(" ", 1)
		if len(msg) < 2: return True
		cmd, msg = msg
		if cmd.lower() not in ("privmsg","notice"): return True
		target, msg = msg.split(" :",1)
		#limit the lenght of the string?
		#msg=msg[:429] #(on freenode)
		length = len(msg)
		self.verbosity['acculen']+=length
		if time.time()-self.verbosity['lastmsg']>10:
			self.verbosity['acculen']=length
			#return False
		self.verbosity['lastmsg']=time.time()
		if self.verbosity['acculen']>800:
			time.sleep(self.verbosity['acculen']/100)
		elif self.verbosity['acculen']>400:
			time.sleep(4)
		elif self.verbosity['acculen']>300:
			time.sleep(1)
		elif self.verbosity['acculen']>100:
			pass
		elif self.verbosity['acculen']<=100 and time.time()-self.verbosity['lastmsg']>1:
			self.verbosity['acculen']=0
		return True

	def _sentinel(self, fn, evt):
		"""[internal]"""
		#Control incomming data that need a response.
		#Prevent flooders that try bot fails by excess flood.
		if fn.skip_sentinel: return True, "alert 0.0"
		if evt.agent in ("services", "server"): return True, "alert 0.1"
		if evt.nick == self.get_nickname() or not re.search ("(priv|pub)(msg|notice|action)", evt.type): return True, "alert 0.2"
		now=time.time()
		maxtime=180 if not self.igns.has_key(evt.nick) else self.igns[evt.nick][1]
		for user in self.requests.copy():
			for request in self.requests[user].copy():
				if now-self.requests[user][request][0]>maxtime:
					del self.requests[user][request]
					if self.igns.has_key(user): self.igns.pop(user)

		if self.igns.has_key(evt.nick):
			if self.requests.has_key(evt.nick) and self.requests[evt.nick].has_key(fn.name):
				self.requests[evt.nick][fn.name]=(now, self.requests[evt.nick][fn.name][1]+1)
			since = datetime.fromtimestamp(self.igns[evt.nick][0]).strftime("%y-%m-%d %H:%M:%S")
			till = datetime.fromtimestamp(self.igns[evt.nick][0]+self.igns[evt.nick][1]).strftime("%y-%m-%d %H:%M:%S")
			return False, "alert 1: ignoring %s since %s till %s" % (evt.nick, since, till)

		if not self.requests.has_key(evt.nick):
			self.requests[evt.nick]={fn.name: (now,1)}
			print self.requests[evt.nick], "checkpoint 1"
			return True, "alert 0.3"
		elif not self.requests[evt.nick].has_key(fn.name):
			self.requests[evt.nick][fn.name]=(now,1)
			print self.requests[evt.nick], "checkpoint 2"
			return True, "alert 0.4"

		last_time, times = self.requests[evt.nick][fn.name]

		if now - last_time < 1.01:
			self.requests[evt.nick][fn.name]=(now, times+1)
			self.igns.update({evt.nick:(now, 720)})
			return False, "alert 2: %s abused with %s command in %.3f sec. for %i times. denied till: %s" % (
				evt.nick, fn.name, now-last_time, times,
				datetime.fromtimestamp(last_time+self.igns[evt.nick][1]).strftime("%y-%m-%d %H:%M:%S")
			)

		self.requests[evt.nick][fn.name]=(now, times+1)

		if times >= fn.limit and now - last_time < maxtime:
			self.igns.update({evt.nick:(now, 60)})
			return False, "alert 3: too requests %s with %s command at %s for %i times in less than 3 min" % (
				evt.nick, fn.name, datetime.fromtimestamp(now).strftime("%y-%m-%d %H:%M:%S"), times
			)

		if now - last_time < 180 and len(self.requests[evt.nick]) > 5:
			self.igns.update({evt.nick:(now, 60)})
			return False, "alert 4: too requests by %s with more than three commands at %s in 3 min" % (
				evt.nick, datetime.fromtimestamp(now).strftime("%y-%m-%d %H:%M:%S")
			)
		print self.requests[evt.nick], "checkpoint 3"
		return True, "alert 0.5"

	def _replace_templates(self, string):
		"""[internal]"""
		evt=self.event
		if evt is None: return string
		string = string.replace("$me", self.get_nickname())
		string=string.replace("$nick", evt.nick)
		string = string.replace("$owner", self.owner)
		string=string.replace("$chan", evt.channel)
		string=string.replace("$serv", self.get_server_name())
		string=string.replace("$more", self.get_help_link())
		return string

	def is_connected(self):
		return self.connected

	def add_global_handler(self, *args):
		"""Add global handler.

		See documentation for IRC.add_global_handler.
		"""
		self.irclibobj.add_global_handler(*args)

	def remove_global_handler(self, *args):
		"""Remove global handler.

		See documentation for IRC.remove_global_handler.
		"""
		self.irclibobj.remove_global_handler(*args)

	# --------------------------------------------------------------
	# - commands of irc client

	def action(self, target, action):
		"""Send a CTCP ACTION command."""
		self.ctcp(target, "ACTION", action)

	def admin(self, server=""):
		"""Send an ADMIN command."""
		if server: server = " %s" % server
		self.send_raw("ADMIN%s" % server)

	def ctcp(self, target, ctcptype, parameter=""):
		"""Send a CTCP command."""
		ctcptype = ctcptype.upper()
		if parameter: parameter=" %s" % parameter
		self.privmsg(target, "\001%s%s\001" % (ctcptype, parameter))

	def ctcp_reply(self, target, parameter):
		"""Send a CTCP REPLY command."""
		self.notice(target, "\001%s\001" % parameter)

	def disconnect(self, message=""):
		"""Hang up the connection.

		Arguments:

			message -- Quit message.
		"""
		if not self.connected:
			return

		self.connected = 0

		self.quit(message)

		try:
			self.socket.close()
		except socket.error, x:
			pass
		self.socket = None

	def globops(self, text):
		"""Send a GLOBOPS command."""
		self.send_raw("GLOBOPS :%s" % text)

	def info(self, server=""):
		"""Send an INFO command."""
		self.send_raw("INFO %s" % server)

	def invite(self, nick, channel):
		"""Send an INVITE command."""
		self.send_raw("INVITE %s %s" % (nick, channel))

	def ison(self, nicks):
		"""Send an ISON command.

		Arguments:

			nicks -- List of nicks.
		"""
		nicks = " ".join(nicks)
		self.send_raw("ISON %s" % nicks)

	def join(self, channel, key=""):
		"""Send a JOIN command."""
		if key: key = " %s" % key
		self.send_raw("JOIN %s%s" % (channel, key))

	def kick(self, channel, nick, comment=""):
		"""Send a KICK command."""
		if comment: comment = " :%s" % comment
		self.send_raw("KICK %s %s%s" % (channel, nick, comment))

	def links(self, remote_server="", server_mask=""):
		"""Send a LINKS command."""
		command = "LINKS"
		if remote_server:
			command += " %s" % remote_server
		if server_mask:
			command += " %s" % server_mask
		self.send_raw(command)

	def list(self, channels="", server=""):
		"""Send a LIST command."""
		command = "LIST"
		if channels:
			if isinstance(channels, list):
				channels = ",".join(channels)
			command += " " + channels
		if server:
			command += " " + server
		self.send_raw(command)

	def lusers(self, server=""):
		"""Send a LUSERS command."""
		if server:server = " %s" % server
		self.send_raw("LUSERS%s" % server)

	def mode(self, target, command):
		"""Send a MODE command."""
		self.send_raw("MODE %s %s" % (target, command))

	def motd(self, server=""):
		"""Send an MOTD command."""
		if server:server = " %s" % server
		self.send_raw("MOTD%s" % server)

	def names(self, channels=""):
		"""Send a NAMES command."""
		if isinstance(channels, list):
			channels = ",".join(channels)
		self.send_raw("NAMES%s" % channels)

	def nick(self, newnick):
		"""Send a NICK command."""
		self.send_raw("NICK %s" % newnick)

	def notice(self, target, text):
		"""Send a NOTICE command."""
		# Should limit len(text) here!
		self.send_raw("NOTICE %s :%s" % (target, text))

	def oper(self, nick, password):
		"""Send an OPER command."""
		self.send_raw("OPER %s %s" % (nick, password))

	def part(self, channels, message=""):
		"""Send a PART command."""
		if message:
			message = " :%s" % message
		if isinstance(channels, list):
			channels = ",".join(channels)
		self.send_raw("PART %s%s" % (channels, message))

	def pass_(self, password):
		"""Send a PASS command."""
		self.send_raw("PASS %s" % password)

	def ping(self, target, target2=""):
		"""Send a PING command."""
		if target2: target2 = " %s" % target2
		self.send_raw("PING %s%s" % (target, target2))

	def pong(self, target, target2=""):
		"""Send a PONG command."""
		if target2: target2 = " %s" % target2
		self.send_raw("PONG %s%s" % (target, target2))

	def privmsg(self, target, text):
		"""Send a PRIVMSG command."""
		# Should limit len(text) here!
		self.send_raw("PRIVMSG %s :%s" % (target, text))

	def privmsg_many(self, targets, text):
		"""Send a PRIVMSG command to multiple targets."""
		# Should limit len(text) here!
		# not available on freenode
		targets = ",".join(targets)
		self.send_raw("PRIVMSG %s :%s" % (targets, text))

	def quit(self, message=""):
		"""Send a QUIT command."""
		# Note that many IRC servers don't use your QUIT message
		# unless you've been connected for at least 5 minutes!
		if message: message = " :%s" % message
		self.send_raw("QUIT%s" % message)

	def send_raw(self, string):
		"""Send raw string to the server.

		The string will be padded with appropriate CR LF.
		"""
		string = colors(string)
		if not self._filter(string): return
		string=self._replace_templates(string)
		if isinstance(string, unicode):
			string=encode(string)
		if self._get_socket() is None:
			raise ServerNotConnectedError, "Not connected."
		try:
			if self.ssl:
				self.ssl.write("%s\r\n" % string)
			else:
				self.socket.send("%s\r\n" % string)
			if _debug or _debug_send_msg:
				print "TO SERVER:", string
		except socket.error, x:
			# Ouch!
			self.disconnect("Connection reset by peer.")

	def squit(self, server, comment=""):
		"""Send an SQUIT command."""
		if comment: comment = " :%s" % comment
		self.send_raw("SQUIT %s%s" % (server, comment))

	def stats(self, statstype, server=""):
		"""Send a STATS command."""
		if server: server=" " % server
		self.send_raw("STATS %s%s" % (statstype, server))

	def time(self, server=""):
		"""Send a TIME command."""
		if server: server=" " % server
		self.send_raw("TIME%s" % server)

	def topic(self, channel, new_topic=None):
		"""Send a TOPIC command."""
		if new_topic: new_topic=" :%s" % new_topic
		self.send_raw("TOPIC %s%s" % (channel, new_topic))

	def trace(self, target=""):
		"""Send a TRACE command."""
		if target: target = " %s" % target
		self.send_raw("TRACE%s" % target)

	def user(self, username, realname):
		"""Send a USER command."""
		self.send_raw("USER %s 0 * :%s" % (username, realname))

	def userhost(self, nicks):
		"""Send a USERHOST command."""
		nicks = ",".join(nicks)
		self.send_raw("USERHOST %s" % nicks)

	def users(self, server=""):
		"""Send a USERS command."""
		if server: server=" " % server
		self.send_raw("USERS%s" % server)

	def version(self, server=""):
		"""Send a VERSION command."""
		if server: server=" " % server
		self.send_raw("VERSION%s" % server)

	def wallops(self, text):
		"""Send a WALLOPS command."""
		self.send_raw("WALLOPS :%s" % text)

	def who(self, target="", op=""):
		"""Send a WHO command."""
		if target: target=" %s" % target
		op = op and (" o")
		self.send_raw("WHO%s%s" % (target, op))

	def whois(self, targets):
		"""Send a WHOIS command."""
		targets = ",".join(targets)
		self.send_raw("WHOIS %s" % targets)

	def whowas(self, nick, max="", server=""):
		"""Send a WHOWAS command."""
		if max: max = " %s" % max
		if server: " %s" % server
		self.send_raw("WHOWAS %s%s%s" % (nick, max, server))

class DCCConnectionError(IRCError):
	pass


class DCCConnection(Connection):
	"""This class represents a DCC connection.

	DCCConnection objects are instantiated by calling the dcc
	method on an IRC object.
	"""
	def __init__(self, irclibobj, dcctype):
		Connection.__init__(self, irclibobj)
		self.connected = 0
		self.passive = 0
		self.dcctype = dcctype
		self.peeraddress = None
		self.peerport = None

	def connect(self, address, port):
		"""Connect/reconnect to a DCC peer.

		Arguments:
			address -- Host/IP address of the peer.

			port -- The port number to connect to.

		Returns the DCCConnection object.
		"""
		self.peeraddress = socket.gethostbyname(address)
		self.peerport = port
		self.socket = None
		self.previous_buffer = ""
		self.handlers = {}
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.passive = 0
		try:
			self.socket.connect((self.peeraddress, self.peerport))
		except socket.error, x:
			raise DCCConnectionError, "Couldn't connect to socket: %s" % x
		self.connected = 1
		if self.irclibobj.fn_to_add_socket:
			self.irclibobj.fn_to_add_socket(self.socket)
		return self

	def listen(self):
		"""Wait for a connection/reconnection from a DCC peer.

		Returns the DCCConnection object.

		The local IP address and port are available as
		self.localaddress and self.localport.  After connection from a
		peer, the peer address and port are available as
		self.peeraddress and self.peerport.
		"""
		self.previous_buffer = ""
		self.handlers = {}
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.passive = 1
		try:
			self.socket.bind((socket.gethostbyname(socket.gethostname()), 0))
			self.localaddress, self.localport = self.socket.getsockname()
			self.socket.listen(10)
		except socket.error, x:
			raise DCCConnectionError, "Couldn't bind socket: %s" % x
		return self

	def disconnect(self, message=""):
		"""Hang up the connection and close the object.

		Arguments:

			message -- Quit message.
		"""
		if not self.connected:
			return

		self.connected = 0
		try:
			self.socket.close()
		except socket.error, x:
			pass
		self.socket = None
		self.irclibobj._handle_event(
			self,
			Event("dcc_disconnect", self.peeraddress, "", [message]))
		self.irclibobj._remove_connection(self)

	def process_data(self):
		"""[Internal]"""

		if self.passive and not self.connected:
			conn, (self.peeraddress, self.peerport) = self.socket.accept()
			self.socket.close()
			self.socket = conn
			self.connected = 1
			if _debug_rcv_msg:
				print "DCC connection from %s:%d" % (
					self.peeraddress, self.peerport)
			self.irclibobj._handle_event(
				self,
				Event("dcc_connect", self.peeraddress, None, None))
			return

		try:
			new_data = self.socket.recv(2**14)
		except socket.error, x:
			# The server hung up.
			self.disconnect("Connection reset by peer")
			return
		if not new_data:
			# Read nothing: connection must be down.
			self.disconnect("Connection reset by peer")
			return

		if self.dcctype == "chat":
			# The specification says lines are terminated with LF, but
			# it seems safer to handle CR LF terminations too.
			chunks = _linesep_regexp.split(self.previous_buffer + new_data)

			# Save the last, unfinished line.
			self.previous_buffer = chunks[-1]
			if len(self.previous_buffer) > 2**14:
				# Bad peer! Naughty peer!
				self.disconnect()
				return
			chunks = chunks[:-1]
		else:
			chunks = [new_data]

		command = "dccmsg"
		prefix = self.peeraddress
		target = None
		for chunk in chunks:
			if _debug_rcv_msg:
				print "FROM PEER:", chunk
			arguments = [chunk]
			if _debug_rcv_msg:
				print "COMMAND: %s, SOURCE: %s, TARGET: %s, ARGS: %s" % (
					command, prefix, target, arguments)
			self.irclibobj._handle_event(
				self,
				Event(command, prefix, target, arguments))

	def _get_socket(self):
		"""[Internal]"""
		return self.socket

	def privmsg(self, string):
		"""Send data to DCC peer.

		The string will be padded with appropriate LF if it's a DCC
		CHAT session.
		"""
		try:
			self.socket.send(string)
			if self.dcctype == "chat":
				self.socket.send("\n")
			if _debug_send_msg:
				print "TO PEER: %s\n" % string
		except socket.error, x:
			# Ouch!
			self.disconnect("Connection reset by peer.")

class SimpleIRCClient:
	"""A simple single-server IRC client class.

	This is an example of an object-oriented wrapper of the IRC
	framework.  A real IRC client can be made by subclassing this
	class and adding appropriate methods.

	The method on_join will be called when a "join" event is created
	(which is done when the server sends a JOIN messsage/command),
	on_privmsg will be called for "privmsg" events, and so on.  The
	handler methods get two arguments: the connection object (same as
	self.connection) and the event object.

	Instance attributes that can be used by sub classes:

		ircobj -- The IRC instance.

		connection -- The ServerConnection instance.

		dcc_connections -- A list of DCCConnection instances.
	"""
	def __init__(self):
		self.ircobj = IRC()
		self.connection = self.ircobj.server()
		self.dcc_connections = []
		self.ircobj.add_global_handler("all_events", self._dispatcher, -10)
		self.ircobj.add_global_handler("dcc_disconnect", self._dcc_disconnect, -10)

	def _dispatcher(self, conn, evt):
		"""[Internal]"""
		# ------
		# - dispatch irc events
		m = "on_" + evt.type
		if hasattr(self, m):
			getattr(self, m)(conn, evt)

		# ------
		# - dispatch user commands
		# - based on phenny script (inadmins.net)
		done=False

		if evt.trigger and not evt.cmd: return
		if irc_lower(encode(evt.nick)) in self.otherbots: return "NO MORE"
		#bot must ignore things like "...", "???", "!!!"
		if evt.trigger and re.match("^%s+$" % (escape_for_regexp(evt.trigger)), evt.msg):
			print "skipping..."
			return "NO MORE" #False positive.
		elif evt.msg.startswith("^"):
			#if line is begun with "^", bot must skip it.
			return "NO MORE"

		if evt.cmd == "clearme" and conn.requests.has_key(evt.nick):
			conn.requests[evt.nick].clear()
			if conn.igns.has_key(evt.nick): del conn.igns[evt.nick]
			print "user requests deleted"
			return "NO MORE"

		def call(fn):
			try:
				return fn(self, conn, evt)
			except Exception, err:
				self.send_error()
				return True

		def do_fn(fn):
			if fn.thread:
				rtn = thread.start_new_thread(call, (fn,))
			else:
				rtn = call(fn)
			return rtn

			"""
			for source in [e.sender, e.nick]:
				try: self.stats[(func.name, source)] += 1
				except KeyError:
					self.stats[(func.name, source)] = 1
			"""

		def switch(regexp):
			pattern=alias.pattern
			if "$me" in pattern:
				pattern = pattern.replace("$me", conn.get_nickname())
			elif "$trigger" in pattern:
				pattern = pattern.replace("$trigger", self.triggers)
			elif "$both" in pattern:
				pattern = pattern.replace("$both", "%s: |%s" %(conn.get_nickname(), self.triggers))
			return re.compile(pattern, re.I)
		
		def watch():
			if isinstance(evt.params, types.InstanceType):
				if evt.opts.has_key("help"):
					self.reply(fn.help)
					return False
				elif evt.opts.has_key("url"):
					if hasattr(fn, "url"):
						self.reply(fn.url)
						return False
					else:
						self.reply("%s has not url.", evt.cmd)
						return False
			return do_fn(fn)

		try:
			break_loops=None
			for priority in ("high","medium","low"):
				for func in self.commands[priority]:
					fn = self.commands[priority][func]
					if fn.evttypes[0] == "*":
						do_fn(fn)
						continue
					elif re.search("|".join(fn.evttypes), evt.type):
						if not re.match("priv|pub", evt.type):
							search_str = evt.type
						else:
							search_str = evt.msg if fn.fullmsg else evt.cmd
					else:
						continue
					if not search_str: continue
					aliases = fn.aliases+fn.rule
					if fn.channels.has_key(evt.channel):
						aliases.append(fn.channels[evt.channel])
					for alias in aliases:
						if not isinstance(alias, basestring):
							alias = switch(alias)
							regexp = alias.search(search_str)
							if regexp:
								if not self.accounts.has_key(evt.identifiedUser) or \
								self.accounts.has_key(evt.identifiedUser) and self.accounts[evt.identifiedUser]['access'] != "master": 
									check, alert = conn._sentinel(fn, evt)
									if not check:
										return
								evt.dict = regexp.groupdict()
								evt.groups = regexp.groups()
								break_loops = watch()
								done = True
						else:
							if alias == search_str:
								if not self.accounts.has_key(evt.identifiedUser) or \
								self.accounts.has_key(evt.identifiedUser) and self.accounts[evt.identifiedUser]['access'] != "master": 
									check, alert = conn._sentinel(fn, evt)
									if not check:
										return
								break_loops = watch()
								done = True
						if done: break
						if break_loops: break
					if break_loops: break
				if break_loops: break
		except RuntimeError:
			#if we add a new command, command dictionary grows.
			print "There are new functions..."

		if not conn.igns.has_key(evt.nick) and not done and evt.trigger:
			if not conn.requests.has_key(evt.nick):
				conn.requests[evt.nick]={"unknown":(time.time(),1)}
			else:
				times=conn.requests[evt.nick]["unknown"][1]+1 if conn.requests[evt.nick].has_key("unknown") else 1
				conn.requests[evt.nick]["unknown"]=(time.time(), times)
				if times>3: return
			self.choose_reply(100, self.replies.unavcmd)

	def _dcc_disconnect(self, c, e):
		self.dcc_connections.remove(c)

	def connect(self, irc_data, extended=None):
		"""Connect/reconnect to a server.

		Arguments:

			server -- Server name.

			port -- Port number.

			nickname -- The nickname.

			password -- Password (if any).

			username -- The username.

			ircname -- The IRC name.

			localaddress -- Bind the connection to a specific local IP address.

			localport -- Bind the connection to a specific local port.

			ssl -- Enable support for ssl.

			ipv6 -- Enable support for ipv6.

		This function can be called to reconnect a closed connection.
		"""
		self.connection.connect(irc_data, extended)

	def dcc_connect(self, address, port, dcctype="chat"):
		"""Connect to a DCC peer.

		Arguments:

			address -- IP address of the peer.

			port -- Port to connect to.

		Returns a DCCConnection instance.
		"""
		dcc = self.ircobj.dcc(dcctype)
		self.dcc_connections.append(dcc)
		dcc.connect(address, port)
		return dcc

	def dcc_listen(self, dcctype="chat"):
		"""Listen for connections from a DCC peer.

		Returns a DCCConnection instance.
		"""
		dcc = self.ircobj.dcc(dcctype)
		self.dcc_connections.append(dcc)
		dcc.listen()
		return dcc

	def start(self):
		"""Start the IRC client."""
		self.ircobj.process_forever()

agents_re = (
	re.compile("^:(?P<nname>[^!]+)!(?P<rname>[^@]+)@(?P<hname>.+)$"), #users, bots
	re.compile("^:(?P<host>(?P<server>[^\.]+)\.(?P<domain>[^\.]+\.[^\.]+))$"), #servers
	re.compile("^:(?P<user>[^!@\.]+)$") #user mode
)
class Nick:
	def __init__(self, sender):
		self.sender = sender
		self._nickname=""
		self._hostname=""
		self._realname=""
		self._agent=""
		if not sender:
			return

		for expr in agents_re:
			mask = expr.search(sender)
			if mask:
				break
		if mask:
			mask = mask.groupdict()
			if mask.has_key("nname"):
				self._nickname=mask['nname']
				self._realname=mask['rname']
				self._hostname=mask['hname']
				if mask['hname']=="services.":
					self._agent="services"
				elif mask['hname'].count("/") == 2 and mask['hname'].split("/")[0] == "freenode":
					self._agent = mask['hname'].split("/")[1] #for staffs, utility-bots
				else:
					self._agent= "user"
			elif mask.has_key('host'):
				self._nickname=self._realname=self._hostname=mask['host']
				self._agent="server"
			elif mask.has_key('user'):
				self._nickname=self._realname=self._hostname=mask['user']
				self._agent="server"

	def __call__(self):
		return self
	def nick(self):
		return self._nickname
	def realname(self):
		return self._realname
	def host(self):
		return self._hostname
	def agent(self):
		return self._agent

class Event:
	"""Class representing an IRC event."""
	def __init__(self, conn, type, params, msg, sender, channel, ctcp):
		"""Constructor of Event objects.

		Arguments:

			type -- A string describing the event.

			source -- The originator of the event (a nick mask or a server).

			target -- The target of the event (a nick or a channel).

			arguments -- Any event specific arguments.
		"""
		label, parsable, raw_line, triggers, _real_nick = conn
		self.raw_line = raw_line
		self.type = type
		self._params = params
		self.msg = msg

		self._sender = Nick(sender)
		self.channel = channel
		self.ctcp = ctcp
		self.agent = self._sender.agent()
		self.nick = self._sender.nick()
		self.host = self._sender.host()
		self.source = channel or self.nick

		self.trigger=""; self.cmd=""; self.cmdline=""; self.args=""
		self.highlight=""; self.match={}; self.dict={}; self.identifiedUser=""
		
		self.opts = [""]

		if parsable:
			#variables for commands
			trigger = re.match("(%s|%s: )" % (triggers, _real_nick), self.msg, re.I)
			self.trigger = trigger.group(1) if trigger else ""
			self.cmdline = self.msg.replace(self.trigger, "", 1) if self.trigger else ""
			self.cmd = self.cmdline.split(" ",1)[0].lower()
			self.args = self.cmdline.split(" ", 1)[1] if " " in self.cmdline else ""
			self.highlight = "%s: " % self.nick if self.trigger and irc_lower(_real_nick) in irc_lower(self.trigger) and self.channel else ""

			#variables for nick
			self.identifiedUser = re.match(r"(?i)(?:freenode/staff|wiki[pm]edia|unaffiliated|wikia)/(.*)", self.host)
			if self.identifiedUser:
				self.identifiedUser = self.identifiedUser.group(1)

			#parsing options for a command
			if label == "wikimedia" and channel:
					self.params = rc_events(self.msg)
					self.wm_change = self.params['event']
			else:
					self.params = GetParams(self.msg)
					#self.args = self.params.arguments()
					self.opts = self.params.options()
					self.items = (self.msg, self.trigger, self.cmd, self.cmdline, self.args, self.opts)
		else:
			self.params = None

_LOW_LEVEL_QUOTE = "\020"
_CTCP_LEVEL_QUOTE = "\134"
_CTCP_DELIMITER = "\001"

_low_level_mapping = {
	"0": "\000",
	"n": "\n",
	"r": "\r",
	_LOW_LEVEL_QUOTE: _LOW_LEVEL_QUOTE
}

_low_level_regexp = re.compile(_LOW_LEVEL_QUOTE + "(.)")

_special = "-[]\\`^{}"
nick_characters = string.ascii_letters + string.digits + _special
_ircstring_translation = string.maketrans(string.ascii_uppercase + "[]\\^",
										  string.ascii_lowercase + "{}|~")

def _ctcp_dequote(message):
	"""[Internal] Dequote a message according to CTCP specifications.

	The function returns a list where each element can be either a
	string (normal message) or a tuple of one or two strings (tagged
	messages).  If a tuple has only one element (ie is a singleton),
	that element is the tag; otherwise the tuple has two elements: the
	tag and the data.

	Arguments:

		message -- The message to be decoded.
	"""

	def _low_level_replace(match_obj):
		ch = match_obj.group(1)

		# If low_level_mapping doesn't have the character as key, we
		# should just return the character.
		return _low_level_mapping.get(ch, ch)

	if _LOW_LEVEL_QUOTE in message:
		# Yup, there was a quote.  Release the dequoter, man!
		message = _low_level_regexp.sub(_low_level_replace, message)

	if _CTCP_DELIMITER not in message:
		return [message]
	else:
		# Split it into parts.  (Does any IRC client actually *use*
		# CTCP stacking like this?)
		chunks = message.split(_CTCP_DELIMITER)

		messages = []
		i = 0
		while i < len(chunks)-1:
			# Add message if it's non-empty.
			if len(chunks[i]) > 0:
				messages.append(chunks[i])

			if i < len(chunks)-2:
				# Aye!  CTCP tagged data ahead!
				messages.append(tuple(chunks[i+1].split(" ", 1)))

			i = i + 2

		if len(chunks) % 2 == 0:
			# Hey, a lonely _CTCP_DELIMITER at the end!  This means
			# that the last chunk, including the delimiter, is a
			# normal message!  (This is according to the CTCP
			# specification.)
			messages.append(_CTCP_DELIMITER + chunks[-1])

		return messages

def irc_lower(s):
	"""Returns a lowercased string.

	The definition of lowercased comes from the IRC specification (RFC1459).
	"""
	s=encode(s)
	return s.translate(_ircstring_translation)

def mask_matches(nick, mask):
	"""Check if a nick matches a mask.

	Returns true if the nick matches, otherwise false.
	"""
	nick = irc_lower(nick)
	mask = irc_lower(mask)
	mask = mask.replace("\\", "\\\\")
	mask = wildcard_to_regexp(escape_for_regexp(mask))
	r = re.compile(mask, re.IGNORECASE)
	return r.match(nick)

def is_channel(string):
	"""Check if a string is a channel name.

	Returns true if the argument is a channel name, otherwise false.
	"""
	return string and string[0] in "#&+!"

def ip_numstr_to_quad(num):
	"""Convert an IP number as an integer given in ASCII
	representation (e.g. '3232235521') to an IP address string
	(e.g. '192.168.0.1')."""
	n = long(num)
	p = map(str, map(int, [n >> 24 & 0xFF, n >> 16 & 0xFF,
						   n >> 8 & 0xFF, n & 0xFF]))
	return ".".join(p)

def ip_quad_to_numstr(quad):
	"""Convert an IP address string (e.g. '192.168.0.1') to an IP
	number as an integer given in ASCII representation
	(e.g. '3232235521')."""
	p = map(long, quad.split("."))
	s = str((p[0] << 24) | (p[1] << 16) | (p[2] << 8) | p[3])
	if s[-1] == "L":
		s = s[:-1]
	return s

def parse_nick_modes(mode_string):
	"""Parse a nick mode string.

	The function returns a list of lists with three members: sign,
	mode and argument.  The sign is \"+\" or \"-\".  The argument is
	always None.

	Example:

	>>> irclib.parse_nick_modes(\"+ab-c\")
	[['+', 'a', None], ['+', 'b', None], ['-', 'c', None]]
	"""

	return _parse_modes(mode_string, "")

def parse_channel_modes(mode_string):
	"""Parse a channel mode string.

	The function returns a list of lists with three members: sign,
	mode and argument.  The sign is \"+\" or \"-\".  The argument is
	None if mode isn't one of \"b\", \"k\", \"l\", \"v\" or \"o\".

	Example:

	>>> irclib.parse_channel_modes(\"+ab-c foo\")
	[['+', 'a', None], ['+', 'b', 'foo'], ['-', 'c', None]]
	"""

	return _parse_modes(mode_string, "bklvo")

def _parse_modes(mode_string, unary_modes=""):
	"""[Internal]"""
	modes = []
	arg_count = 0

	# State variable.
	sign = ""

	a = mode_string.split()
	if len(a) == 0:
		return []
	else:
		mode_part, args = a[0], a[1:]

	if mode_part[0] not in "+-":
		return []
	for ch in mode_part:
		if ch in "+-":
			sign = ch
		elif ch == " ":
			collecting_arguments = 1
		elif ch in unary_modes:
			if len(args) >= arg_count + 1:
				modes.append([sign, ch, args[arg_count]])
				arg_count = arg_count + 1
			else:
				modes.append([sign, ch, None])
		else:
			modes.append([sign, ch, None])
	return modes

def _ping_ponger(connection, event):
	"""[Internal]"""
	connection.pong(event.msg)

# Numeric table mostly stolen from the Perl IRC module (Net::IRC).
numeric_events = {
	"001": "welcome",
	"002": "yourhost",
	"003": "created",
	"004": "myinfo",
	"005": "featurelist",  # XXX
	"200": "tracelink",
	"201": "traceconnecting",
	"202": "tracehandshake",
	"203": "traceunknown",
	"204": "traceoperator",
	"205": "traceuser",
	"206": "traceserver",
	"207": "traceservice",
	"208": "tracenewtype",
	"209": "traceclass",
	"210": "tracereconnect",
	"211": "statslinkinfo",
	"212": "statscommands",
	"213": "statscline",
	"214": "statsnline",
	"215": "statsiline",
	"216": "statskline",
	"217": "statsqline",
	"218": "statsyline",
	"219": "endofstats",
	"221": "umodeis",
	"231": "serviceinfo",
	"232": "endofservices",
	"233": "service",
	"234": "servlist",
	"235": "servlistend",
	"241": "statslline",
	"242": "statsuptime",
	"243": "statsoline",
	"244": "statshline",
	"250": "luserconns",
	"251": "luserclient",
	"252": "luserop",
	"253": "luserunknown",
	"254": "luserchannels",
	"255": "luserme",
	"256": "adminme",
	"257": "adminloc1",
	"258": "adminloc2",
	"259": "adminemail",
	"261": "tracelog",
	"262": "endoftrace",
	"263": "tryagain",
	"265": "n_local",
	"266": "n_global",
	"300": "none",
	"301": "away",
	"302": "userhost",
	"303": "ison",
	"305": "unaway",
	"306": "nowaway",
	"311": "whoisuser",
	"312": "whoisserver",
	"313": "whoisoperator",
	"314": "whowasuser",
	"315": "endofwho",
	"316": "whoischanop",
	"317": "whoisidle",
	"318": "endofwhois",
	"319": "whoischannels",
	"321": "liststart",
	"322": "list",
	"323": "listend",
	"324": "channelmodeis",
	"329": "channelcreate",
	"331": "notopic",
	"332": "currenttopic",
	"333": "topicinfo",
	"341": "inviting",
	"342": "summoning",
	"346": "invitelist",
	"347": "endofinvitelist",
	"348": "exceptlist",
	"349": "endofexceptlist",
	"351": "version",
	"352": "whoreply",
	"353": "namreply",
	"361": "killdone",
	"362": "closing",
	"363": "closeend",
	"364": "links",
	"365": "endoflinks",
	"366": "endofnames",
	"367": "banlist",
	"368": "endofbanlist",
	"369": "endofwhowas",
	"371": "info",
	"372": "motd",
	"373": "infostart",
	"374": "endofinfo",
	"375": "motdstart",
	"376": "endofmotd",
	"377": "motd2",        # 1997-10-16 -- tkil
	"381": "youreoper",
	"382": "rehashing",
	"384": "myportis",
	"391": "time",
	"392": "usersstart",
	"393": "users",
	"394": "endofusers",
	"395": "nousers",
	"401": "nosuchnick",
	"402": "nosuchserver",
	"403": "nosuchchannel",
	"404": "cannotsendtochan",
	"405": "toomanychannels",
	"406": "wasnosuchnick",
	"407": "toomanytargets",
	"409": "noorigin",
	"411": "norecipient",
	"412": "notexttosend",
	"413": "notoplevel",
	"414": "wildtoplevel",
	"421": "unknowncommand",
	"422": "nomotd",
	"423": "noadmininfo",
	"424": "fileerror",
	"431": "nonicknamegiven",
	"432": "erroneusnickname", # Thiss iz how its speld in thee RFC.
	"433": "nicknameinuse",
	"436": "nickcollision",
	"437": "unavailresource",  # "Nick temporally unavailable"
	"441": "usernotinchannel",
	"442": "notonchannel",
	"443": "useronchannel",
	"444": "nologin",
	"445": "summondisabled",
	"446": "usersdisabled",
	"451": "notregistered",
	"461": "needmoreparams",
	"462": "alreadyregistered",
	"463": "nopermforhost",
	"464": "passwdmismatch",
	"465": "yourebannedcreep", # I love this one...
	"466": "youwillbebanned",
	"467": "keyset",
	"471": "channelisfull",
	"472": "unknownmode",
	"473": "inviteonlychan",
	"474": "bannedfromchan",
	"475": "badchannelkey",
	"476": "badchanmask",
	"477": "nochanmodes",  # "Channel doesn't support modes"
	"478": "banlistfull",
	"481": "noprivileges",
	"482": "chanoprivsneeded",
	"483": "cantkillserver",
	"484": "restricted",   # Connection is restricted
	"485": "uniqopprivsneeded",
	"491": "nooperhost",
	"492": "noservicehost",
	"501": "umodeunknownflag",
	"502": "usersdontmatch",
}

generated_events = [
	# Generated events
	"dcc_connect",
	"dcc_disconnect",
	"dccmsg",
	"disconnect",
	"ctcp",
	"ctcpreply",
]

protocol_events = [
	# IRC protocol events
	"error",
	"join",
	"kick",
	"mode",
	"part",
	"ping",
	"privmsg",
	"privnotice",
	"pubmsg",
	"pubnotice",
	"quit",
	"invite",
	"pong",
]

all_events = generated_events + protocol_events + numeric_events.values()
