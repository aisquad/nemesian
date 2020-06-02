#!/usr/bin/env python
# -*- coding:utf8 -*-

import re, sys

def reorder(e):
	if isinstance(e, bool):
		return e
	elif isinstance(e, list):
		return " ".join(reversed(e)).strip()

class GetParams:
	def __init__(self, text=None):
		self.params = {}
		self.text = text
		self.sep = ";"
		self.delimiter = "-"
		self.required = {}
		self.aliases = {}
		self.items = tuple()
		self.get_params()

	def __call__(self):
		return self.params

	def __getitem__(self, key):
		if not self.params.has_key(key):
			self.params[key]=False
		return self.params[key]

	def __setitem__(self, key, value):
		self.params.update({key: value})

	def __delitem__(self, key):
		if self.params.has_key(key):
			del self.params[key]

	def __repr__(self):
		return "%s%s" %(self.__class__.__name__, repr(self.params))

	def __contains__(self, key):
		return self.params.has_key(key)
	
	def sum(self):
		return '%s(%d keys, %d req keys, %d aliases)' \
		% (self.__class__.__name__, len(self.params), len(self.required), len(self.aliases))

	def get(self, key, fail=None):
		return self.params.get(key, fail)

	def has_key(self, key):
		return self.params.has_key(key)

	def keys(self):
		return self.params.keys()

	def values(self):
		return self.params.values()
	
	def get_params(self):
		#2010-03-25 00:37:29
		line = self.text or " ".join(sys.argv[1:])
		values=[]; keys=[]; unnamed = []; temp = []
		join_args = False; insensitive = False
		self.params["%m%"]={"i": insensitive, "j": join_args}
		for token in reversed(line.split()):
			if not token[0] in "-+.:":
				values.append(token)
				temp.append(token)
			if token.startswith("-"):
				temp=[]
				token=token[1:]
				keys.append(token)
				if ":" in token:
					token, value=token.split(":",1)
					values.append(value)
				if values == []:
					if token.startswith("!"):
						token=token[1:]
						values=False
					else:
						values=True
				if self.params.has_key(token):
					if isinstance(self.params[token], (basestring, bool)):
						self.params[token]=[self.params[token], reorder(values)]
					elif isinstance(self.params[token], list):
						self.params[token].append(reorder(values))
				else:
					if isinstance(values, list):
						self.params[token]=" ".join(reversed(values)).strip()
					else:
						self.params[token]=values
				values=[]
			elif token.startswith("+"):
				token = token[1:]
				if temp:
					token = " ".join([token]+list(reversed(temp)))
				unnamed.append(token)
				for t in temp:
					if values: values.pop()
				temp=[]
			elif token.startswith("."):
				token = token[1:]
				if token == "j":
					#space works as separator if %u% is the only key for the option dict
					#if join_args is False, then space doesn't split string
					join_args = True
					self.params["%m%"].update({token: join_args})
				if token == "i":
					#if insensitive is True, options are insensitive case. -t 1 -T 3 = "t": [1, 3] <NOTDONE>
					insensitive = True
					self.params["%m%"].update({token: insensitive})
				if len(token)>1 and token.startswith("s"):
					self.sep = self.params["%m%"]["s"] = token[1:]
			elif token.startswith(":"):
				self.params['%a%']=token[1:]

		if values != []:
			self.params["%u%"] = " ".join(reversed(values))
			if unnamed:
				self.params["%u%"] = list(reversed(unnamed)) + [self.params["%u%"]]
		elif unnamed:
			self.params["%u%"] = list(reversed(unnamed))
		for key in self.params:
			if isinstance(self.params[key], basestring) and self.sep in self.params[key]:
				self.params[key] = self.params[key].split(self.sep)
				tokens = []
				for token in self.params[key]:
					if token == "": continue
					tokens.append(token.strip())
				self.params[key] = tokens
			elif isinstance(self.params[key], list):
				i = 0
				for s in self.params[key]:
					if isinstance(s, basestring):
						i += 1
						strings=list(reversed(s.split(self.sep)))
						if len(strings)>1:
							for sub in strings:
								if sub:
									self.params[key].insert(i, sub.strip())
									i += 1
							self.params[key].remove(s)
				self.params[key] = list(reversed(self.params[key]))
		self.params["%m%"]["%"]=0
		for k in self.params:
			if len(k)==3 and k.count("%") == 2 and k[1] != "%":
				self.params["%m%"]["%"]+=1
		if join_args and self.params.has_key('%u%') and isinstance(self.params['%u%'], basestring) and len(self.params) - self.params["%m%"]["%"] == 0:
			self.params['%u%'] = self.params['%u%'].split()
		for param in self.params:
			if isinstance(self.params[param], list) and len(self.params[param]) == 1:
				self.params[param] = self.params[param][0]
		self.items = [self.text, self.arguments(), self.options()]
		return self.params

	def check_params(self):
		err_msg=[]
		
		for alias in self.aliases:
			values=[]
			if alias in self.params:
				if isinstance(self.params[alias], list):
					values += self.params[alias]
				else:
					values = [self.params[alias]]
			for key in self.aliases[alias]:
				if key in self.params:
					if isinstance(self.params[key], list):
						values += self.params[key]
					else:
						values.append(self.params[key])
					del self.params[key]
			if values:
				self.params[alias] = values
			
		for param in self.required:
			if param not in self.params:
				err = "OPTION: -%s %s\nSETTING %s AS %s\nHELP: %s\n" % (param, self.required[param][2], param, self.required[param][0], self.required[param][1])
				self.params[param] = self.required[param][0]
				print (err)
				err_msg.append(err)
		for param in self.params:
			if isinstance(self.params[param], list) and len(self.params[param]) == 1:
				self.params[param] = self.params[param][0]
		return err_msg
				
	def add_required(self, option, def_value=True, help_msg="This parameter is not optional.", err_msg="is required"):
		self.required.update({option: [def_value, help_msg, err_msg]})
		
	def add_alias(self, option, *args):
		if self.aliases.has_key(option):
			self.aliases[option] += args
		else:
			self.aliases[option] = args

	def cense(self):
		return len(self.params), self.params["%m%"]["%"], len(self.params)-self.params["%m%"]["%"]
	
	def action(self):
		return self.params["%a%"]

	def arguments(self):
		return self.get("%u%")
		
	def options(self):
		params = {}
		for param in self.params:
			if not (len(param)==3 and param.count("%") == 2 and param[1] != "%"):
				params.update({param: self.params[param]})
		return params

	def special(self):
		return self.get("%m%")