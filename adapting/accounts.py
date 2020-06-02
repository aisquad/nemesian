#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time
from framework.irclib import irc_lower

def credits(bot, irc, cur): 
   msg=""
   targeted_nick = cur.params.strip().encode("utf-8")
   if not targeted_nick: targeted_nick=irc.nick
   if bot.nicks.has_key(irc_lower(targeted_nick)): targeted_nick = bot.nicks[irc_lower(targeted_nick)]
   elif bot.accounts.has_key(targeted_nick): targeted_nick = targeted_nick
   else: targeted_nick=""

   if targeted_nick:
      msg=targeted_nick+" "
      c = bot.accounts.get_credits(targeted_nick)
      if c != "<|nocredits|>":
         msg+="has got %i credits." % (c-1)
      else:
         msg+="has no credits."
   else:
     msg+="no account founded."
   if msg:
      bot.msg(irc.nick, cur.calluser + msg)
   if bot.nicks[irc_lower(irc.nick)]=="Pasqual" and cur.params.strip()=="*":
         time.sleep(1)
         bot.connection.privmsg(irc.nick, "nicks:%s" % (str(bot.nicks)[:350]))
         time.sleep(2)
         msgs=[]
         msg="%i keys: " % len(bot.accounts.keys())
         from functions import colors
         for u in sorted(bot.accounts.keys()):
            if len(msg)  > 300:
               bot.connection.privmsg(irc.nick,msg)
               time.sleep(len(msg)/100)
               msg=""
            elif len(msg)>10: msg+=", "
            msg+="$B$l%s$N $o%i$N (%s)" % (u, bot.accounts.get_credits(u), time.strftime("%d-%m-%y %H:%M",time.localtime(bot.accounts.get_lasttalk(u))))
            msg=colors(msg)
         bot.connection.privmsg(irc.nick,msg)
         time.sleep(len(msg)/100)
credits.rule = 'credits'
credits.showas = "credits"
credits.thread=True

def setdata(bot, irc, cur): 
   msg=""
   params = cur.params.strip().split(" ")
   if not bot.nicks.has_key(irc_lower(irc.nick)): return
   if len(params)==2:
      item = params[0]
      value = params[1]
      if item =="lang":
         account = bot.nicks[irc_lower(irc.nick)]
         bot.accounts.set_lang(account,value)
         bot.msg(irc.nick, '%s\'s language set as "%s"' % (account, value))
setdata.rule = 'my'

def keys(bot, irc, cur): 
   msg=""
   nick = cur.params.strip()
   if not nick: nick=irc.nick
   nick_lwr=irc_lower(nick)
   l=bot.accounts.keys()
   msg="%i keys: %s" % (len(l), ", ".join(l))
   if msg:
      bot.msg(irc.nick, cur.calluser + msg)
keys.rule = 'keys'

def flags(bot, irc, cur):
    params = cur.params.strip()
    keys = params.split(" ")
    if len(keys)==2 or len(keys)==3:
        cmd = keys[0] if keys[0] in ("add","rem","mod","del") else ""
        target = keys[1] if cmd else keys[0]
        flags = keys[2] if cmd else keys[1]
        account = bot.account(irc.nick)
        if account == target or bot.accounts.has_flags(account, "d"):

			if not boss:
				bot.abuso.registracomando(nick,"flags",9)
				c.privmsg(canal, "no tiene los permisos necesarios")
				return
			if cur:
				usr=""
				flag=""
				if ":" in cur:
					usr=cur.split(":",1)[0].lower()
					flag=cur.split(":",1)[1]
				else:
					usr=cur.lower()
				if usr and flag:
					if usr not in flags:
						flags[usr]=flag
						c.privmsg(canal, "flags aceptados.")
					else:
						flags[usr]=flag
						c.privmsg(canal, "flags modificados.")
					desaReg()
				elif usr and not flag:
					if usr in flags:
						del flags[usr]
						c.privmsg(canal, "flags eliminados.")
						desaReg()
				else:
						c.privmsg(usuario, u"parámetros erróneos.")
flags.rule="flags"
