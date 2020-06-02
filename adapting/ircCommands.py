#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
names.py - names Functionality
Author: Sean B. Palmer, inamidst.com
About: http://inamidst.com/phenny/
"""

import re

def f_names(self, origin, args): 
   """.names <channel> - list users on <channel>."""
   chan = args.params
   if not chan:
      chan=origin.target
   chan=chan.lower().encode("utf-8")
   if chan[0]!="#":
      chan="#"+chan
   if self.channels.has_key(chan):
      users=self.channels.get(chan).users()
      users2=[]
      for user in users:
         user=self.quietNick(user)
         users2.append(user)
      users=", ".join(users2)
      nick = origin.nick
      users=users.replace(nick,nick[0]+":"+nick[1:])
      self.msg(origin.target, "%s: %s" % (chan, users))
   else:
      self.msg(origin.target, "I'm not on %s" % chan)
f_names.rule = 'names'
f_names.thread = True
