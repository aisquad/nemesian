#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
articles.py
"""

import random, re, threading, time
import config, reply, browser
from functions import fetch, qurl
from sitematrix import wikimap

def size(page):
   t1      =  time.time()
   msg     =  browser.wiki_link(page)
   apilink =  browser.wlink2url(page).replace("index.php?","api.php?").split("?title=")[0]
   apilink += "?action=query&prop=info&titles=%s" % page.split("|")[0]
   data    =  browser.get(apilink)
   size    =  re.search("length=&quot;(\d+)&quot;", data)
   if size:
      size = int(size.group(1))
      if size>1024:
         msg+= " ocupa %i bytes (%iKb)." % (size, size/1024)
      else:
         msg+= " ocupa %i bytes." % (size)
      if re.search("redirect=&quot;&quot;", data):
         msg+= " (redirección)"
      msg+= " %f segundos." % (time.time()-t1)
   else:
      msg += " no existe."
   return msg

class Articles(threading.Thread):
   def __init__ (self, s, lang=config.lang, chan=""):
      self.s = s
      self.chan = chan
      self.lang=lang
      self.delang = config.lang
      threading.Thread.__init__ ( self )

   def run (self):
      self.articles(self.s, self.lang)

   def articleCount(self, xx): #xx es el código de la wiki. Ejemplos - "es:", "en:", "de:"..
      url='http://%s.wikipedia.org/w/index.php?title=Special:Statistics&action=raw' % xx
      txt=browser.get(url)
      m=re.search(ur"good=(.*);views=", txt)
      print "="*70,"\n",xx, url, "\ntxt:", txt, "\nm:", m
      if m:
	 return m.group(1)
      else:
	 return 0  

   def articles(self, s, b):
      try:
         articles=int(self.articleCount(b))
         if b!=self.delang:
            our_articles=int(self.articleCount(self.delang))
            #print "our_arts:",our_articles,"ext_articles:",articles, b
            if our_articles > articles :
               diference=our_articles-articles
               prep="debajo"
            else:
               diference=articles-our_articles
               prep="encima"
            s.msg(self.chan, u"http://%s.wikipedia.org tiene %s artículos (%i por %s de w:es)" % (b, str(articles),diference,prep))
         else:
            s.msg(self.chan, "Tenemos %s artículos... Pero de mucha más calidad que el resto. ¡Y ahora poneos a wikificar!" % str(articles))
      except:
         reply.answer(reply.art_error,100,s.connection,self.chan)

def arts(self, origin, args):
   if not origin.target.startswith("#"):
      self.msg(origin.target, "Comando no disponible en privado")
      return
   reply="" 
   c=args.cmd
   a=args.params

   if c=="art":
       b=""
       if a:
          b=a
          b=b.replace(" ","")
          b=b.replace(":","")
          b=b.replace(".","")
       else:
          b="es"
       reply = Articles(self, b, origin.target).start()
   elif c in ("tam","size") and a:
      reply=size(qurl(a))
   elif c == "fetch" and a:
      reply =fetch(qurl(a))
   elif c == "stats":
      if not a: a= "es"
      a=a.replace(":","").replace(".","").strip()
      if a not in wikimap:
         reply = "el proyecto '%s' no existe" % a
      else:
         reply = fetch(a+":Special:Statistics")
       
   if reply:
      self.msg(origin.target, reply)
arts.rule = ["art", "tam", "size", "fetch", "stats"]
arts.showas = ["art","tam|size","fetch", "stats"]
arts.thread = True
