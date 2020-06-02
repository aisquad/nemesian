#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
search.py
"""

import re
import browser

def f_search(self, origin, args): 
   cmd = args.match.group(1)
   params = args.match.group(2)
   reply=""

   print "search.py",cmd,params
   if cmd == "busca-co":
      params=params.replace(" ","+")
      params=params.replace("\"","%22")
      reply = "http://www.google.es/search?hl=es&q="+params.encode('utf-8')+"+site:commons.wikimedia.org"
   elif cmd == "busca-me":
      params=params.replace(" ","+")
      params=params.replace("\"","%22")
      reply="http://www.google.es/search?hl=es&q="+params.encode('utf-8')+"+site:meta.wikimedia.org"
   elif cmd == "busca-go":
      params=params.replace(" ","+")
      params=params.replace("\"","%22")
      reply="http://www.google.es/search?hl=es&q="+params.encode('utf-8')
   elif cmd.startswith("busca-"):
      wiki=cmd[cmd.find("-")+1:]
      from sitematrix import wikimap
      if wikimap.has_key(wiki):
         params=params.replace(" ","+")
         params=params.replace("\"","%22")
         reply="http://www.google.es/search?hl=es&q="+params.encode('utf-8')+"+site:"+wiki+".wikipedia.org"
      else:
         reply="Lameruzooo, que no existe esa wikipedia"
   elif cmd == "wikipedia":
      if args[0][1:] == "wikipedia":
         reply="Tamos tontos? o qué!! Qué coño haces en este canal.  --> http://www.wikipedia.org/ <--"
      else:
         params=params.replace(" ","+")
         params=params.replace("\"","%22")
         reply = "http://www.google.es/search?hl=es&q="+params+"+site:wikipedia.org"
   elif cmd == "google":
      if args[0][1:] == "google":
         reply = "http://www.google.com"
      else:
         params=params.replace(" ","+")
         params=params.replace("\"","%22")
         reply = "http://www.google.es/search?hl=es&q="+params
   elif cmd == "flickr":
      if args[0][1:] == "flickr":
         reply = "http://www.flickr.com"
      else:
         params=params.replace(" ","+")
         params=search.replace("\"","%22")
         reply = "http://www.flickr.com/search/?q="+params+"&l=commderiv"
   elif cmd == "youtube":
      if args[0][1:] == "youtube":
         reply = "http://www.youtube.com"
      else:
         params=params.replace(" ","+")
         params=params.replace("\"","%22")
         reply = "http://youtube.com/replys?search_query="+params+"&search=Search"

   if reply:
         self.msg(origin.target, reply)
f_search.rule = (r'(?i)^\.(?:google|youtube|flickr|wikipedia|busca-..)(?: (.+))?',)
f_search.thread = True
f_search.showas = ["busca-*","youtube","flickr","google","wikipedia"]
