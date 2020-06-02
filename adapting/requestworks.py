#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
games.py
"""

import os, re, urllib
from util.functions import isAlpha

def dicts(self, origin, args): 
   """.drae <word> - return a url of <word>, ably a definition too."""
   word=args.params
   cmd=args.cmd
   result = ""
   msg=""
   msgs=[]
   if cmd == "en-es":
      #/usr/bin/sh ~/i2e-0.5.1/i2e-cli
      call="~/i2e-0.5.1/i2e.sh "+word.encode('latin-1')
      if isAlpha(word.encode('utf-8')):
         a=os.popen(call)
         quid=a.readlines()
         a.close()
         salida=""
         for i in quid[1:4]:
            msgs.append(i)
   elif cmd == "es-en":
      call="~/i2e-0.5.1/i2e.sh -r "+word.encode('latin-1')
      if isAlpha(word.encode('utf-8')):
         a=os.popen(call)
         quid=a.readlines()
         a.close()
         for i in quid[1:9]:
            msgs.append(i)
   elif cmd in ["es-en","en-es"] and args: #deprecated
      word=args
      number, result = dictorg(word,"*",cmd)
      msg=u"%i resultados. %s"%(number, result)
   elif cmd == "orto":
      call="echo \""+word.encode('latin-1')+"\"|ispell -a"
      if isAlpha(word.encode('utf-8')):
         a=os.popen(call)
         kaka=a.readlines()
         a.close()
         salida=""
         for i in kaka[1:-1]:
            msgs.append(unicode(i,'latin-1').encode('utf-8'))
   elif cmd == "drae":
      msg = "http://buscon.rae.es/draeI/SrvltGUIBusUsual?TIPO_HTML=2&LEMA="+urllib.quote(word.encode('utf-8'))
   elif cmd == "dpd":
      msg = "http://buscon.rae.es/dpdI/SrvltGUIBusDPD?lema="+urllib.quote(word.encode('latin-1'))
   ##Pide sinónomimos, problems con la codificación de acentos :(
   elif cmd == "sino":
      msg = "http://sinonimos.org/"+urllib.quote(word.encode('utf-8'))
   ##  enlaza a la EL
   elif cmd == "el":
      msg = "http://enciclopedia.us.es/index.php/"+urllib.quote(word.encode('utf-8'))
   if msg:
      self.msg(origin.target,msg)
   elif msgs:
      self.msglines(origin.target, msgs)
f_dicts.rule = ['drae','en-es','es-en','orto','dpd','sino']
f_dicts.showas = ["drae","dpd","en-es|es-en","orto","sino"]

def f_thesaurus(self, origin, args): 
   """.thesaurus <word> - Get <word>'s synonyms."""
   # 2004-07-13 17:10Z <evangineer> tell sbp` can we have a .thesaurus 
   # or .synonym feature for phenny that just outputs the synonyms please?
   word = args.params
   uri = 'http://thesaurus.reference.com/search?q=' + urllib.quote(word)
   s = browser.get(uri)

   striphtml = lambda s: re.sub(r'<[^?>][^>]*>', '', s)
   r_thesaurus = re.compile(r'<b>Synonyms:</b>[^\r\n]+<td>([^\r\n]*)</td>')
   m = r_thesaurus.search(s)
   if m: 
      result = m.group(1)
      result = striphtml(result)[:500]
      result = ["%s synonyms: %s" % (word, line)
                for line in textwrap.wrap(result, 200)][:2]
      self.msglines(origin.sender, result)
   else: 
      msg = "%s: sorry, no synonyms found for %s"
      self.msg(origin.sender, msg % (origin.nick, word))
f_thesaurus.rule = ['thesaurus', 'synonym']
f_thesaurus.thread = True
f_thesaurus.showas = "thesaurus|synonym"
