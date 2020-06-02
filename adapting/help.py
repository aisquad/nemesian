#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
help.py - Help Facilities
Author: Sean B. Palmer, inamidst.com
About: http://inamidst.com/phenny/
"""
from config import nick as botnick, helpdoc, owner

def f_chelp(self, origin, args): 
   command = args.params
   if self.doc.has_key('f_' + command): 
      self.msg(origin.target, '%s' % self.doc['f_' + command])
   elif self.doc.has_key(command): 
      self.msg(origin.target, '%s' % self.doc[command])
   else: self.msg(origin.target, "Sorry, no documentation for %s. Please see %s" % (command, helpdoc))

def f_help(self, origin, args): 
   if (args.sign == self.connection.get_nickname()) and origin.target.startswith('#'): 
      return
   if args.params: 
      f_chelp(self, origin, args)
      return
f_help.rule = 'help'
f_help.showas = "help <command>"

def f_shelp(self, origin, args):
   from random import randint
   if args.params:
      f_help(self, origin, args)
      return
   dice = randint(1,20)
   if "freenode" not in origin.host and (self.nicks.has_key(origin.nick) and not self.nicks[origin.nick] == "Pasqual") and dice != 1:
      import reply
      reply.answer(reply.nohelp,100,self.connection,origin.target,(origin.nick,))
      return
   result = ["Hi, I'm %s. My owner is %s." % (self.botnick, owner)]
   if dice > 18:
      msg='Commands: '
      for key in self.all:
         if key[0] != "!":
            msg+="%s, " % key
            if len(msg)>350:
               result.append(msg)
               msg=''
      if msg:
         result.append(msg[:-2]+".")

   result.append('Try "%s: help command" if stuck. ' % self.botnick)
   if dice > 5:
      result.append('Type ".all" for a list of all commands. See also %s' % helpdoc)   
   self.msglines(origin.nick, result)
f_shelp.rule = "help"


def f_all(self, origin, args):
   """.all - show all commands."""
   print "help.py f_all"
   keys = []
   for cmd in self.all: 
      if not cmd.startswith('!'): 
         keys.append(cmd)
   msg ='%i commands are available: ' % len(keys)
   for key in keys:
      msg+="%s, " % key
      if len(msg)>350:
         self.msg(origin.target, msg)
         msg=''
   if msg:
      self.msg(origin.target, msg[:-2]+".")
f_all.rule = ['all','commands']
f_all.showas = "all|commands"

def f_nokey(self, origin, args):
   """.??? - This command notices that requested command doesn't exist."""
   #implemented by Pasqual@cawiki 27-09-2008 14:57 CEST
   #this function seems to return an errmsg if there's no ordre available.
   if not self.debug: return
   selectedkey=args.cmd
   if not selectedkey:
      self.msg(origin.target, selectedkey+str(args.cmd))
      return

   keys = self.all
   if selectedkey not in keys:

      #COLORS
      BLK="\x0301"  #black
      BLU="\x0312"  #blue
      BRN="\x0305"  #brown
      CYN="\x0311"  #cyan
      DBL="\x0302"  #dark blue
      DGN="\x0303"  #dark green
      DGY="\x0314"  #dark gray
      GRN="\x0309"  #green
      LGY="\x0315"  #light gray
      MGN="\x0313"  #magenta
      OLV="\x0307"  #olive
      PRP="\x0306"  #purple
      RED="\x0304"  #red
      TEL="\x0310"  #teal
      WHT="\x0300"  #white
      YLW="\x0308"  #yellow
      #FORMAT
      BLD="\x02"    #bold
      NRM="\x0f"    #normal
      INV="\x16"    #inverse
      UND="\x1f"    #underline

      i=1
      mm=""
      for m in match.groups()[:-1]:
         if i%2==0:
            m=GRN+m+NRM
         else:
            m=BLU+m+NRM
         m+=", "
         mm+=m
         i+=1
      lastClr=GRN if i%2==0 else BLU
      lastM = ""
      if match.groups(): lastM=lastClr+match.groups()[-1]+NRM+"." if len(match.groups())>1 and match.groups()[-1] else ""
      mm+=lastM
      matches="matches: "+mm

      aa=""
      i=0
      for a in args[:-1]:
         if i%2==0:
            a=GRN+a+NRM
         else:
            a=BLU+a+NRM
         a+=", "
         aa+=a
         i+=1
      lastClr=GRN if i%2==0 else BLU
      lastA=""
      if args: lastA=lastClr+args[-1]+NRM+"." if len(args)>1 else ""
      aa+=lastA
      args="args: "+aa

      kk=""
      i=0
      for k in keys[:-1]:
         if i%2==0:
            k=GRN+k+NRM
         else:
            k=BLU+k+NRM
         k+=", "
         kk+=k
         i+=1
      lastClr=GRN if i%2==0 else BLU
      lastK=""
      if keys: lastK=lastClr+keys[-1]+NRM+"." if len(keys)>1 else ""
      kk+=lastK
      keys="keys: "+kk
      
      #self.msg(origin.target, selectedkey+" is not an available command.")
      self.msg(origin.target, "selectedkey: "+RED+selectedkey+NRM)
      self.msg(origin.target, matches)
      self.msg(origin.target, args)
      keys=keys.split(", ")
      for k in range(0,len(keys),30):
         ksplitted=keys[k:k+30]
         self.msg(origin.target, ", ".join(ksplitted))
f_nokey.rule = (r'^$sign(\S+)( .*)??$',)
f_nokey.thread = True
f_nokey.load = False
