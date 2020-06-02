#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
banalities.py
"""

import random, re, time
from config import nick as botnick

def f_banalities(self, origin, args):
   """mola|ey tío|melón|heh|@_@|ping"""
   m = args.match.group(1).lower()
   reply=""
   if m=="mola":
      reply="Ey tío"
   elif re.search(u"ey t[íi]o", m):
      reply="mola"
   elif re.search(u"(?iu)mel[oó]n", m):
      reply="XD"
   elif m=="heh":
      if random.randint(1,2)==1:
         reply="lol"
   elif m =="@_@":
      reply="^_^"
   elif re.search("^(?:%s[:,]? +)?ping$|[\.@]ping" % self.botnick, m, re.I):
      ping=re.search("(?i)(p[i1]ng)",args.match.group(1)).group(1)
      if ping:
         pong=ping.replace("i","o").replace("I","O").replace("1","0")
         reply = "%s: %s" % (origin.nick, pong)
   elif re.search("^l[ou]lz?!?$", m, re.I):
      lol=random.choice(["LOL","","xD","",":D","","O_O","","o_O","",">)"])
      if lol:
         reply = random.choice(["",origin.nick+": "]) + lol + random.choice([""," ?","",])

   if reply:
      self.msg(origin.target,reply)
f_banalities.rule = (ur"(?iu)^(ey t[íi]o|mola|mel[óo]n.*|heh|@_@|$signp[i1]ng|l[ou]lz?)$",)
f_banalities.show = "ping"

def f_stuff(self, origin, args):
   from functions import isAlpha
   import os
   
   cmd = args.cmd
   params=args.params
   reply=""
   if cmd in ("tonteria", u"tontería") and params:
      call="cowthink -f sodomized "+params.encode('latin-1')
      if isAlpha(params.encode('utf-8')):
         a=os.popen(call)
         lines=a.readlines()
         a.close()
         for i in lines:
            self.msg(origin.target, i)
            time.sleep(2.0)
         return
      else:
         reply="Tú si que eres tonto chaval !!"
   elif cmd == "mes":
      if not origin.target.startswith("#"):
         call="cal -m3"
         a=os.popen(call)
         lines=a.readlines()
         a.close()
         for i in lines:
            self.msg(chan, i)
            time.sleep(2.0)
         return
      else:
         from time import strftime
         reply="mes: " + strftime("%B")
   elif cmd == "galletita":
      if origin.target.startswith("#"):
         self.msg(origin.nick, "Comando disponible únicamente en privado")
         return
      call="fortune"
      a=os.popen(call)
      lines=a.readlines()
      a.close()
      for i in lines:
         self.msg(origin.nick, i)
         time.sleep(1.0)
      return
   elif cmd == "wtf":
      call="wtf "+params.encode('latin-1')
      if isAlpha(params.encode('utf-8')):
         a=os.popen(call)
         lines=a.readlines()
         a.close()
         for i in lines:
            self.msg(origin.target, i)
            time.sleep(1.0)
         return
   elif cmd =="smileys":
      reply=':) :S >:( ;) B) >:D :D :") XD :~( :O :| :? :P :( 9_9 O_O o_O O_o >)'

   if reply:
      self.msg(origin.target, reply)
f_stuff.rule = ["tonteria",u"tontería","e","pi","wtf","galletita","mes","smileys"]
f_stuff.showas = ["mes","galletita","wtf","smileys"]

def f_stupid(self, origin, args):
      self.msg(origin.target, "42")
f_stupid.rule = ("(?i)^$sign=answer to life the universe and everything$",)
   
def f_games(self, origin, args):
   import reply
   cmd = args.cmd
   if cmd in (u"café", "cafe"):
      reply.answer(self.connection, origin.target, reply.cofee, 100, (origin.nick,))
   elif cmd == "tabaco" :
      reply.answer(self.connection, origin.target, reply.tobacco, 100, (origin.nick,))
   elif cmd == "porro" :
      reply.answer(self.connection, origin.target, reply.joint, 100, (origin.nick,))
   elif cmd in ("litrona", "cerveza", "birra"):
      reply.answer(self.connection, origin.target, reply.beer, 100, (origin.nick,))
   elif cmd == "guapo" :
      reply.answer(self.connection, origin.target, reply.beautiful, 100, (origin.nick,))
   elif cmd == "sexy" :
      reply.answer(self.connection, origin.target, reply.sexy, 100, (origin.nick,))
   elif cmd in ("listo", "inteligente"):
      reply.answer(self.connection, origin.target, reply.clever, 100, (origin.nick,))
   elif cmd == "fuente":
      reply.answer(self.connection, origin.target, reply.springs, 100, (origin.nick,))
   elif cmd == "love":
      users=self.channels.get(origin.target).users()
      user1=random.choice(users)
      users.remove(user1)
      user2=random.choice(users)
      reply.answer(self.connection, origin.target, reply.love, 100, (origin.nick, user1, user2))
f_games.rule = [u"café",u"cafe","tabaco","porro","litrona","cerveza","birra","guapo","listo","inteligente","fuente","love"]


def f_irc(self, origin, args):
   m = args.cmd.lower()
   reply=""
   if m == "die":
      dado=random.randint(1,3)
      if dado==1:
         reply=["Muérete tu cabrón"]
      elif dado==2:
         reply=["Aggghhh me mueeeeeero"]
         reply+=["Exception: self.die() Operación imposible de realizar :þ"]
      elif dado==3:
         reply=["Uy sí, que miedoooo... muérete tú, pendejo"]

   if reply:
      self.msglines(origin.target,reply)
f_irc.rule = "die"
f_irc.showas = "die"

def f_pong(self, origin, args): 
   msg = random.choice(['er... ping?', 'ping? pang?', 'hmm?'])
   self.msg(origin.target, msg)
f_pong.rule = 'pong'
f_pong.showas = "pong"