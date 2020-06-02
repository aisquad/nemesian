#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
defaultlinks.py - Perform Greetings
"""

import random, re, time
from functions import *

def f_links(self, origin, args):
   cmd = args.match.group(1)
   params = args.match.group(2)
   reply=""
   if cmd in ["b", "block"]:
      usr=args.match.group(2)
      reply=u"http://es.wikipedia.org/wiki/Special:Blockip/"+qurl(usr)
   elif cmd in  ["cb", "bc"]:
      usr=args.match.group(2)
      url=u"http://es.wikipedia.org/wiki/Special:$sp$/%s"%qurl(usr)
      reply=[]
      for l in cmd:
         if l == "c":
            reply.append(url.replace("$sp$","Contributions"))
         else:
            reply.append(url.replace("$sp$","BlockIP"))
      self.msglines(origin.target, reply)
      reply=""
   elif cmd.startswith("mant"):
      epotime=int(time.time())-(86400*31)
      reply = ["http://es.wikipedia.org/wiki/Categor%C3%ADa:Wikipedia:Mantenimiento",
             u"http://es.wikipedia.org/wiki/Categor%%C3%%ADa:Wikipedia:Mantenimiento:%d_de_%s" %\
             (int(time.strftime("%d",time.localtime(epotime))), i_mes[int(time.strftime("%m",time.localtime(epotime)))])
             ]
      self.msglines(origin.target, reply)
      reply=""
   elif cmd.startswith("dest") or cmd.startswith("bor"):
      reply="http://es.wikipedia.org/wiki/Categor%C3%ADa:Wikipedia:Borrar%20%28definitivo%29"
   elif cmd.startswith("vec"):
      reply="http://es.wikipedia.org/wiki/Wikipedia:Vandalismo_en_curso"
         
   if reply:
      self.msg(origin.target, reply)
f_links.rule = (r"(?i)^$sign(mant.*|dest.*|bor.*|vec.*|bc|cb|b|block|a[bd]|cad)(?: (.*))?$",)
f_links.showas =["bc|cb", "b(lock)", "mant*", "dest*", "bor*", "vec*"]
