#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
ops.py - Manage chans
Author: FiloSottile@it.wiki
About
"""
import random, re
from functions import check_access

def parse_params(params, defchan, defnick):
   params=params.strip().split(" ")
   chan=defchan
   nick=defnick
   if len(params)==2:
      if params[0].startswith("#"): chan=params[0]
      if params[1]: nick = params[1]
   elif len(params)==1:
      if params[0]:
         if params[0].startswith("#"): chan=params[0]
         else: nick=params[0]
   if nick == "me": nick = defnick
   print "chanops.py parse_params", params, "||", chan,nick, "||", defchan,defnick, "||", len(params)
   return chan, nick

def topic(bot, evt, cmd):
   """.topic <channnel> <newtopic> - change the topic"""
   if has_access(bot, topic.level):
      params= args.params.encode("utf-8").split(" ",1)
      if len(params)==2:
         chan  = params[0]
         topic = params[1]
      self.connection.topic(origin.target,topic)
topic.rule = 'topic'
topic.showas='topic'

def invite(bot, evt, cmd):
   """.invite <user> <channel> - (reserved) send to server an INVITE command"""
   
   params=args.params.split(" ")
   if len(params)==2:
         self.connection.invite(params[0],parmas[1])
invite.rule = 'invite'
invite.showas='!invite'

def op(bot, evt, cmd):
   """.op <channel> <nick> - (reserved) get op for <user> at <channel>"""
   chan, nick = parse_params(args.params, origin.target, origin.nick)
   if check_access(self,origin.target,origin.nick,"nick"):
      if chan and nick: self.msg("ChanServ","OP %s %s" % (chan, nick))
   else:
      self.connection.notice(origin.nick, "%s: You aren't allowed to do this operation." % origin.nick)      
op.rule = r"!op"
op.showas=r"!op"
 
#/msg chanserv op #botolatori -Filnik
def deop(bot, evt, cmd):
   if not origin.target.startswith("#"): return
   chan, nick = parse_params(args.params, origin.target, origin.nick)
   if check_access(self,origin.target,origin.nick,"nick"):
      if chan and nick: self.msg("ChanServ","DEOP %s %s" % (chan, nick))
   else:
      self.connection.notice(origin.nick, "%s: You aren't allowed to do this operation." % origin.nick)
deop.rule = r"!deop"
deop.showas = r"!deop"

def kick(bot, evt, cmd): 
   if check_access(self,origin.target,origin.nick,"nick"):
      self.connection.kick(origin.target, args.params.encode("utf-8").strip())
   else:
      self.connection.notice(origin.nick, 'Illegal kick!')
kick.rule = '!kick'
kick.showas='!kick'

def ban(bot, evt, cmd): 
   if check_access(self,origin.target,origin.nick,"nick"):
      pass
   else:
      self.connection.notice(origin.nick, 'Illegal kick!')
ban.rule = r"!ban"
ban.showas=r"!ban"

def voice(bot, evt, cmd):
   #/msg ChanServ voice #canale utente
   if check_access(self,origin.target,origin.nick,"nick"):
      pass
   else:
      self.connection.notice(origin.nick, "%s: You aren't allowed to do this operation." % origin.nick)      
voice.rule = r"!voice"
voice.showas = r"!voice"
 
def devoice(bot, evt, cmd): 
   if check_access(self,origin.target,origin.nick,"nick"):
      pass
   else:
      self.connection.notice(origin.nick, "%s: You aren't allowed to do this operation." % origin.nick)
devoice.rule = r"!devoice"
devoice.showas=r"!devoice"
 
