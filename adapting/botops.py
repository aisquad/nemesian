#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
admin.py - Manage bot
Author: FiloSottile@it.wiki
About
"""
 
import random, re
from functions import check_access

clips={"wp-cbl": "##wikipedia-cabal",
       "cvn": "#cvn-wp-es",
       "mant": "#wp-mant-es",
       "wp-es": "#wikipedia-es",
       "wp-ca": "#wikipedia-ca",
       "<main>": "##pampolut",
       }

def resolve(params, to_nick=False):
   params = params.encode("utf-8")
   params = params.split(" ",1)
   if len(params)<2: return False, False
   chan=params[0]
   msg=params[1]
   if clips.has_key(chan): chan = clips[chan]
   if not to_nick and not chan.startswith("#"): chan="#"+chan

   return chan, msg

def resolve2(chan, nick, msg, channels):
	msg = msg.split(" ",1)
	print msg
	if len(msg)==2:
		chan=msg[0]
		msg=msg[1]
		if clips.has_key(chan): chan = clips[chan]
		if not chan.startswith("#"):
			for ch1 in channels:
				ch2=ch1.replace("#","")
				if chan == ch2:
					chan=ch1
		if not chan.startswith("#"): chan="#"+chan
	elif len(msg)==1 and msg[0] is not "":
		checkchan=msg[0]
		if clips.has_key(checkchan): checkchan = clips[checkchan]
		if checkchan.startswith("#"):
			chan=checkchan
			msg=""
		elif not checkchan.startswith("#"):
			for ch1 in channels:
				ch2=ch1.replace("#","")
				if checkchan == ch2:
					chan=ch1
					msg=""
					break
				else: msg=msg[0]
		else:
			msg=msg[0] 
	else:
		msg = nick
	
	if not msg or msg==['']:
		msg=nick
	
	line = chan+" :"+msg
	return line

def f_chans(self, origin, args):
   if check_access(self,origin.target,origin.nick,"join"):
      self.msg(origin.target, str(self.channels.keys()))
f_chans.rule = "chans"      
      
#In and out
def f_join(self, origin, args):
	chan = args.params.strip().encode("utf-8")
	if check_access(self,origin.target,origin.nick,"join"):
	  if chan in clips: chan = clips[chan]
	  elif chan == "<chans>":
		f_gochans(self, origin, args)
		self.msg(origin.target, origin.nick+": recuerda, ahora el comando es @gochans, pronto no se podrá utilizar @j <chans>")
	  elif not chan.startswith("#"):
		 chan="#"+chan
	  if chan in self.channels.keys():
			self.msg(origin.target, "I am already on %s" % chan)
	  else:
			self.connection.join(chan)
	else:
	  self.connection.notice(origin.nick, "%s: Only my owner can make join me on other channels." % origin.nick)   
f_join.rule = ["j","join"]

def f_gochans(self, origin, args):
   if check_access(self,origin.target,origin.nick,"join"):
		chans = ",".join(self.otherchans)
		self.connection.join(chans)
		self.msg(origin.target, "I've joined channels.")
   else:
      self.connection.notice(origin.nick, "%s: Only my owner can make join me on other channels." % origin.nick)   
f_gochans.rule = "gochans"
 
def f_part(self, origin, args):
   line = resolve2(origin.target, origin.nick, args.params.encode("utf-8"), self.channels.keys())
   if check_access(self,origin.target,origin.nick,"part"):
      self.connection.part(line)
   else: self.connection.notice(origin.nick, "%s: Only my owner can do this operation." % origin.nick)
f_part.rule = 'part'

def f_quit(self, origin, args): 
   if check_access(self,origin.target,origin.nick,"quit"):
      msg = "i'll come back, i swear!" if args.cmd == "reboot" else args.params.encode("utf-8") or origin.nick
      self.die(msg)
   else: self.connection.notice(origin.nick, "%s: Only my owner can do this operation." % origin.nick)
f_quit.rule = ['quit', 'reboot']

#For bot nickname 
def f_nickname(self, origin, args): 
   c = self.connection
   newnick = args.params
   if check_access(self,origin.target,origin.nick,"nick"):
      c.nick(newnick)
   else:
      c.notice(origin.nick, "%s: Only my owner can change my nickname." % origin.nick)
f_nickname.rule = 'nick'
 
def f_identify(self, origin, args):
   if check_access(self,origin.target,origin.nick,"identify"):
      self.msg('NickServ', 'IDENTIFY %s' % self.config.passw)
      self.connection.notice(origin.nick, 'Identified!')
f_identify.rule = "identify"
 
def f_ghost(self, origin, args):
   if access(self,origin.target,origin.nick,"ghost"):
      self.msg('NickServ', 'GHOST %s %s' %(self.botnick,self.config.password))
      self.connection.notice(origin.nick, "pampolut has been ghosted!") 
f_ghost.rule = "ghost"

def f_group(self, origin, args): 
   c = self.connection
   if check_access(self,origin.target,origin.nick,"nick"):
      c.privmsg("NickServ", "group")
   else:
      c.notice(origin.nick, "%s: Only my owner can change my nickname." % origin.nick)
f_group.rule = 'group'

def f_chflag(self, origin, args): 
   c = self.connection
   newop = args.params.strip().split(" ")[0]
   flag  = args.params.strip().split(" ")[1]
   if check_access(self,origin.target,origin.nick,"nick"):
	self.accounts.set_flag(newop.encode("utf-8"), flag.encode("utf-8"))
	c.privmsg(self.mainchan, "Now %s is flagged as %s " % (newop, flag))
   else:
      c.notice(origin.nick, "%s: Only my owner can change my nickname." % origin.nick)
f_chflag.rule = 'chflag'