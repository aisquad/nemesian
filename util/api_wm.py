#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
	API mediawiki
	05-04-2009. Pasqual @ cawiki
	Classes:
		API
"""
import json, os, re, sys, time
import codecs as cs, datetime as dt

from relativedelta import relativedelta as rd
from datetime import datetime, timedelta, date
from dateutil.parser import *

from browser import B

class FromAPIFormat:
	"""Return some formats based on API timestamp"""
	def __init__(self, string):
		self.string=string
		self.struc=time.strptime(string, "%Y-%m-%dT%H:%M:%SZ")

	def timestamp(self):
		return time.mktime(self.struc)

	def as_tuple(self):
		return (self.struc.tm_year, self.struc.tm_mon, self.struc.tm_mday,
				self.struc.tm_hour, self.struc.tm_min, self.struc.tm_sec, self.struc.tm_wday, self.struc.tm_yday, self.struc.tm_isdst)

	def as_dt(self):
		return datetime.fromtimestamp(self.timestamp)

	def readable(self, f="[%Y-%m-%d %H:%M]"):
		ts = time.strftime(f, self.as_tuple())
		#print ts, self.as_tuple()
		return ts

class ToAPIFormat:
	def __init__(self, string=None):
		if not string:
			self.date = datetime.now()
		elif isinstance(string, basestring):
			if string.count("-")==2 and not ":" in string:
				self.date= dt.strptime(string, "%Y-%m-%d")
			elif ":" in string and "-" in string:
				if string.index(":") > string.index("-"):
					self.date=dt.strptime("%Y-%m-%d %H:%M")
				elif string.index(":") > string.index("-"):
					self.date=dt.strptime("%H:%M %d-%m-%Y")

		self._midnight = datetime.strptime(self.date.strftime("%Y-%m-%d 00:00:00"), "%Y-%m-%d %H:%M:%S")

	def midnight(self):
		return self._midnight.strftime("%Y-%m-%dT%H:%M:%SZ")

	def whole_day(self):
		end_at = self._midnight
		start_at = end_at+rd(hours=23, minutes=59, seconds=59)
		start_at = start_at.strftime("%Y-%m-%dT%H:%M:%SZ")
		end_at = end_at.strftime("%Y-%m-%dT%H:%M:%SZ")
		return start_at, end_at

	def days(self, d=0):
		end_at = self._midnight+rd(days=d)
		start_at = end_at+rd(hours=23, minutes=59, seconds=59)
		start_at = start_at.strftime("%Y-%m-%dT%H:%M:%SZ")
		end_at = end_at.strftime("%Y-%m-%dT%H:%M:%SZ")
		return start_at, end_at

	def today(self):
		today = self._midnight
		return today.strftime("%Y-%m-%dT%H:%M:%SZ")

	def now(self):
		now=datetime.now()
		return now.strftime("%Y-%m-%dT%H:%M:%SZ")

def parse_date(string):
	formats=(
		"%H:%M:%S %d-%m-%y",
		"%H:%M:%S %d-%m-%Y",
		"%H:%M %d-%m-%y",
		"%H:%M %d-%m-%y",
		"%H:%M %d-%m-%Y",
		"%d-%m-%y H:%M:%S",
		"%d-%m-%Y %H:%M:%S",
		"%d-%m-%y %H:%M",
		"%d-%m-%y %H:%M",
		"%d-%m-%Y %H:%M",
		"%H:%M:%S",
		"%H:%M",
		"%d-%m-%y",
		"%d-%m-%Y"
	)
	string=string.replace(",","")
	string=string.replace("/","-")
	string=string.replace("h",":")
	string=string.replace("m",":")
	date="<not parsed/>"
	for format in formats:
		try:
			date = datetime.strptime(string, format)
			break
		except:
			continue
	print date

	args = sys.argv[1:]
	args=" ".join(args)
	parse_date(args)
	print parse(args)

def get_new_articles(start, end, redirect):
	print B._site
	params={
		"action": "query",
		#newarticles
		"list": "recentchanges",
		"rclimit": "max",
		"rctype": "new",
		"rcprop": "title|timestamp",
		"rcnamespace": 0,
		"rcstart": start,
		"rcend": end,
		#statistics
		"meta":"siteinfo",
		"siprop":"statistics"
	}
	if not redirect:
		params['rcshow']="!redirect"
	newpages = B.get_api(params)
	return newpages

def log_new_arts():
	site = B._site
	log=cs.open(time.strftime("psq_recentchanges_newarts_%y%m%d-%H%M.log"), "w", "utf-8")

	for i in range(0,15):
		langs={}

		for lang in ("ca","fi","no"):
			site = B.site(lang)
			time_stamps = ToAPIFormat().days(-i)
			langs[lang]={}
			for redirect in (True,False):
				start=time_stamps[0]
				arts=0
				while start:
					rc=get_new_articles(start, time_stamps[1], redirect)
					if rc.has_key("error"):
						print "ERROR:", rc['error']['info']
						return
					pages=rc['query']['recentchanges']
					if rc.has_key("query-continue"):
						print "\tMORE than 500?"
						start=rc["query-continue"]["recentchanges"]["rcstart"]
					else: start=False
					arts+=len(pages)
				if redirect:
					langs[lang].update({"new_arts": arts})
				else:
					langs[lang].update({"new_arts_without_redir": arts})
				langs[lang]["info"] = rc['query']['statistics']['articles']
		if i == 1:
			ca_info=('<span title="%i %s">' % (langs["ca"]['info'], time.strftime("(%d %H:%M)")), '</span>')
			fi_info=('<span title="%i %s">' % (langs["fi"]['info'], time.strftime("(%d %H:%M)")), '</span>')
			no_info=('<span title="%i %s">' % (langs["ca"]['info'], time.strftime("(%d %H:%M)")), '</span>')
		else:
			ca_info=("","")
			fi_info=("","")
			no_info=("","")
		line='|-\r\n| %s || %s%i/%i%s || %s%i/%i%s || %s%i/%i%s' % (
			FromAPIFormat(time_stamps[0]).readable("%Y-%m-%d"),
			ca_info[0], langs["ca"]['new_arts_without_redir'], langs["ca"]['new_arts'], ca_info[1],
			fi_info[0], langs["fi"]['new_arts_without_redir'], langs['fi']['new_arts'], fi_info[1],
			no_info[0], langs["no"]['new_arts_without_redir'], langs['no']['new_arts'], no_info[1]
		)
		print line
		log.write("%s\r\n" % line)
		log.flush()
	log.close()

def en_new_arts():
	site = B.site("ca")
	time_stamps = ToAPIFormat().days(-1)
	enwiki={}
	for redirect in (True,False):
		start=time_stamps[0]
		arts=0
		while start:
			print "de %s a %s" % (FromAPIFormat(start).readable("%H:%M"), FromAPIFormat(time_stamps[1]).readable("%H:%M"))
			rc=get_new_articles(start, time_stamps[1], redirect)
			if rc.has_key("error"):
				print "ERROR:", rc['error']['info']
				return
			pages=rc['query']['recentchanges']
			if rc.has_key("query-continue"):
				start=rc["query-continue"]["recentchanges"]["rcstart"]
			else: start=False
			arts+=len(pages)
		if redirect:
			enwiki.update({"new_arts": arts})
		else:
			enwiki.update({"new_arts_without_redir": arts})
		enwiki["info"] = rc['query']['statistics']['articles']
	en_info=('<span title="%i %s">' % (enwiki['info'], time.strftime("(%d %H:%M)")), '</span>')
	line='|-\r\n| %s || %s%i/%i%s' % (
		FromAPIFormat(time_stamps[0]).readable("%Y-%m-%d"),
		en_info[0], enwiki['new_arts_without_redir'], enwiki['new_arts'], en_info[1],
	)
	print line

if __name__ == "__main__":
	log_new_arts()
