#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
reload.py - Reload Modules Dynamically
Author: Sean B. Palmer, inamidst.com
About: http://inamidst.com/phenny/
"""
import os, time
from functions import check_access

def f_reload(self, origin, args):
   if not check_access(self, origin.target, origin.nick, "reload"): return
   folder=""
   name = args.params
   modules = os.path.join(os.getcwd(), 'modules')
   is_home=name+".py" in os.listdir(os.getcwd())
   is_in_modules=name+".py" in os.listdir(modules)
   if not name:
      self.connection.notice(origin.nick, "module name expected")
      return
   elif not is_home and not is_in_modules:
      self.connection.notice(origin.nick, "unknown module")
      return

   module = getattr(__import__('modules.' + name), name)
   
   reload(module)
   self.register(vars(module))
   self.bindrules()

   if hasattr(module, '__file__'):
      mtime = os.path.getmtime(module.__file__)
      modified = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(mtime))
   else: modified = 'unknown'

   msg = '%r (version: %s)' % (module, modified)
   self.connection.notice(origin.nick, origin.nick + ': ' + msg)
#f_reload.rule = ('$nick', ['reload'], r'(\S+)')
f_reload.rule = 'reload'
f_reload.showas = "reload"
