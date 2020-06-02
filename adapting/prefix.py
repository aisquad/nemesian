#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
prefix.py - Munge Prefixes Dynamically
Author: Sean B. Palmer, inamidst.com
About: http://inamidst.com/phenny/
"""

def f_prefix(self, origin, args): 
   name, prefix = args.match.group(1), args.match.group(2)
   method = getattr(self, 'f_' + name)

   rule = method.rule
   self.msg(origin.sender, 'Regexp for %s was %s' % (name, rule))
   if rule.startswith('^\\'): 
      rule = rule.lstrip('^\\')[1:]
   else: rule = rule[rule.index('+')+1:]

   if len(prefix) == 1: 
      rule = '^\\' + prefix + rule
   elif prefix == '$nick': 
      rule = (r'^%s[;,][ \t]+' % self.nick) + rule
   else: self.msg(orgin.isender, "Can't set prefix to %s" % prefix)

   method.rule = rule
   self.bindrules()
   self.msg(origin.sender, 'Regexp for %s is now %s' % (name, method.rule))
f_prefix.rule = ('^\$signprefix (\S+) (\S+)$')
f_prefix.addcmd = "!prefix"
