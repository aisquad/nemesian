#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
codepoint.py - Unicode Utilities
Author: Sean B. Palmer, inamidst.com
About: http://inamidst.com/phenny/
"""

import re, unicodedata

def f_charinfo(self, origin, args): 
   """.char <seq> - Get info about a sequence."""
   import unicodedata
   input = args.params

   chars = {
      '\xa3': u'\u00A3', 
      'E/': u'\u00C9', 
      'a\\': u'\u00E0', 
      'ae': u'\u00E6', 
      'e\\': u'\u00E8', 
      'e/': u'\u00E9', 
      'i/': u'\u00ED', 
      'o^': u'\u00F4', 
      'o:': u'\u00F6', 
      '|': u'\u017F', 
      'long s': u'\u017F', 
      'long-s': u'\u017F', 
      '--': u'\u2014', 
      '->': u'\u2192'
   }

   if chars.has_key(input): 
      char = chars[input]
   else: char = input[:1]

   if char: 
      cp = ord(char)
      name = unicodedata.name(char).title()
      msg = '&#x%04X; - %s (%s)' % (cp, name, char.encode('utf-8'))
      self.msg(origin.target, msg)
   else: self.msg(origin.target, '%s: sorry, no such char' % origin.nick)
f_charinfo.rule = ['char', 'charinfo']
f_charinfo.thread = True
f_charinfo.showas = 'char(info)'

def f_unicode(self, origin, args): 
   import unicodedata
   label = args.params.upper()
   r_label = re.compile('\\b' + label.replace(' ', '.*\\b'))
   results = []
   for i in xrange(0xFFFF): 
      try: name = unicodedata.name(unichr(i))
      except ValueError: continue
      if r_label.search(name): 
         results.append((len(name), i))
   if not results: 
      self.msg(origin.target, 'Sorry, no results found for "%s".' % label)
      return
   name, u = sorted(results)[0]
   cp = unichr(u).encode('utf-8')
   if unicodedata.combining(unichr(u)): 
      msg = 'U+%04X %s (\xe2\x97\x8c%s)' % (u, unicodedata.name(unichr(u)), cp)
   else: msg = 'U+%04X %s (%s)' % (u, unicodedata.name(unichr(u)), cp)
   self.msg(origin.target, msg)
f_unicode.rule = 'unicode'
f_unicode.thread = True
f_unicode.addcmd = "unicode"

def f_representation(self, origin, args): 
   """.repres <str> - Return the representation of <str>."""
   self.msg(origin.target, '%r' % args.params)
f_representation.rule = ['bytes', 'octets', 'repres', 'repr']
f_representation.addcmd = "bytes|octets|repr(es)"
