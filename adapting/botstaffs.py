#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
staff.py - Manage bot
Author: Pasqual@ca.wiki
About
"""
 
import random, re, time
from functions import check_access, saveobj

def f_ign(self, origin, args):
   if check_access(self,origin.target,origin.nick,"ign"):
      params=args.params.strip()
      els=[]
      nousigns=[]
      if ", " in params:
         els=args.split(", ")
      else:
         els=[params]
      if "*" in els: els.remove("*")
      for el in els:
         if "pasqual" in el.lower():
             if origin.host.lower() != "wikipedia/pasqual":
                el=nick
             else:
                self.msg(origin.nick, "je je que cachondo!")
                continue
         if el and el not in self.igns.keys():
             nousigns.append(el)
             self.log("igns", "+ | " + el + " |: " + origin.nick + " :| " + time.strftime("%d-%m-%y %H:%M:%S"))
      if len(nousigns)==1:
         els="el siguiente nick"
      else:
         els="los siguientes nicks"
      if nousigns:
         msg  = u"se ha añadido %s a la lista de ignorados: %s"%(els,', '.join(nousigns))
         self.igns.append(nousigns)
      else:
         igns = ', '.join(self.igns.keys()).encode("utf-8")
         msg  = u"Error: no se han podido añadir los nuevos ignorados, el bot ignorará: %s" % igns
      msg=msg.encode("utf-8")
      self.msg(origin.nick, msg)
   else:
      self.connection.notice(origin.nick, "%s: Only staff can use this command." % origin.nick)
f_ign.rule = 'ign'
f_ign.showas = '!ign'

def f_unign(self, origin, args): 
   if check_access(self,origin.target,origin.nick,"unign"):
      params=args.params.strip().lower()
      els=[]
      elim=[]
      if params=="*":
         self.igns=[]
         self.msg(origin.nick, "se han eliminados todos los registros")
         self.log("igns", "- | all_log |: " + origin.nick + " :| " + time.strftime("%d-%m-%y %H:%M:%S"))
         return
      if ", " in params:
         els=params.split(", ")
      else:
         els=[params]
      for el in els:
         if re.search("\*|\?",el):
            el0=el.replace(".*","*").replace(".?","?").replace("*",".*").replace("?",".?")
            for el1 in self.igns.keys():
               if re.search(r"("+el0+")",el1,re.I):
                  el2=re.search(r"("+el0+")",el1,re.I).group(1)
                  if el1.lower() == el2.lower():
                     elim.append(el1)
         else:
            for el1 in self.igns.keys():
               if el1.lower() == el.lower():
                  elim.append(el1)
      for el in elim:
          self.igns.remove(el)
          self.log("igns", "- | " + el + " |: " + origin.nick + " :| " + time.strftime("%d-%m-%y %H:%M:%S"))
      if elim:
         msg="elementos eliminados: %s"%(', '.join(elim))
         self.msg(origin.nick, msg)
         time.sleep(len(msg)/10)
         msg = "elementos restantes: %s"%(', '.join(self.igns.keys()))
      else:
         msg = "no se han encontrado coincidencias"
      self.msg(origin.nick, msg)
   else:
      self.connection.notice(origin.nick, "%s: Only staff can use this command." % origin.nick)
f_unign.rule = 'unign'
f_unign.showas = '!unign'

def f_igns(self, origin, args): 
   if check_access(self,origin.target,origin.nick,"unign"):
      if self.igns.keys():
         users=', '.join(self.igns.keys())
         self.msg(origin.nick, users)
      else:
         self.msg(origin.nick, "there are no users ignored.")
   else:
      self.msg(origin.nick, "%s: Only staff can use this command." % origin.nick)
f_igns.rule = 'igns'
f_igns.showas = '!igns'

def f_dontreport(self, origin, args): 
   if check_access(self,origin.target,origin.nick,"reboot"):
      if self.chans.keys():
         chans=', '.join(self.chansDB)
         self.msg(origin.nick, chans)
   else:
      self.msg(origin.nick, "%s: Only staff can use this command." % origin.nick)
f_dontreport.rule = 'dontreport'
f_dontreport.showas = '!dontreport'

def f_allchans(self, origin, args): 
   if check_access(self,origin.target,origin.nick,"ign"):
      if self.channels:
         chans=', '.join(self.channels.keys())
         self.msg(origin.nick, chans)
   else:
      self.msg(origin.nick, "%s: Only staff can use this command." % origin.nick)
f_allchans.rule = 'allchans'
f_allchans.showas = '!allchans'


def f_checking(self, origin, args):
   nick = origin.nick if not args.params else args.params.strip()
   self.connection.whois([nick])
f_checking.rule=['check','checking']