#-*- coding:utf8 -*-
# recent_changes.py

import re

IRC_RC_RE = {
   #09.06.2009
   #ordre de les marques: !NMB http://ca.wikipedia.org/wiki/?oldid=3817722&rcid=3822888

   #modificació de pàgines *M?* grups: page, marques, menor, url, diff, oldid, rcid, usuari, diffsize, summary
   "edit": re.compile(ur'\x0314\[\[\x0307(?P<page>.*?)\x0314\]\]\x034 (?P<flags>(?P<patrol>!?)(?P<minor>M?)(?P<bot>B?))\x0310 \x0302(?P<url>http://.*?/w/index\.php\?diff=(?P<diff>\d*)&oldid=(?P<oldid>\d*)(&rcid=(?P<rcid>\d*))?)\x03 \x035\*\x03 \x0303(?P<user>.*?)\x03 \x035\*\x03 \(\x02?(?P<diffsize>[+-]\d*)\x02?\) \x0310(?P<summary>.*)\x03'), # changed page, with or without rcid, with or without comment
   #pàgina nova amb rcid *M?N* grups: page, marques, menor, nou, url (.../w/index.php?title=...) , rcid, usuari, diffsize, summary
   "new": re.compile(ur'\x0314\[\[\x0307(?P<page>.*?)\x0314\]\]\x034 (?P<flags>(?P<patrol>!?)(?P<new>N)(?P<minor>M?)(?P<bot>B?))\x0310 \x0302(?P<url>http://.*?/w/index\.php\?oldid=(?P<oldid>\d*)&rcid=(?P<rcid>\d*))\x03 \x035\*\x03 \x0303(?P<user>.*?)\x03 \x035\*\x03 \(\x02?(?P<diffsize>[+-]\d*)\x02?\) \x0310(?P<summary>.*)\x03'), # new page with rcid

   #Log:newusers *create* grups: page, marques=create, usuari
   "create": re.compile(ur'\x0314\[\[\x0307(?P<page>.*?)\x0314\]\]\x034 (?P<flags>create)\x0310 \x0302\x03 \x035\*\x03 \x0303(?P<user>.*?)\x03 \x035\*\x03  \x0310.*\x03'), # new users *create*
   #Log:newusres *create2* grups: page, marques=create, usuari, element1 (=usuari nou)
   "create2": re.compile(ur'\x0314\[\[\x0307(?P<page>.*?)\x0314\]\]\x034 (?P<flags>create2)\x0310 \x0302\x03 \x035\*\x03 \x0303(?P<user>.*?)\x03 \x035\*\x03  \x0310.*\x0302.*:(?P<element1>.*)\x0310\x03'), # new users *create*

   #Log:move amb summary (cada llengua utilitza una cadena diferent, adaptat a cawiki) grups: log, marques=move_redir, usuari, element1, element2, summary
   "move": re.compile(ur'\x0314\[\[\x0307(?P<page>.*?)\x0314\]\]\x034 (?P<flags>move(?:_redir)?)\x0310 \x0302\x03 \x035\*\x03 \x0303(?P<user>.*?)\x03 \x035\*\x03  \x0310(?P<element1>.*?) mogut a (?P<element2>.*?)(?: per redirecció)?(?::(?P<summary>.*?) )?\x03'), # move and move_redir with or without summary

   #Log:upload *upload* grups: page, marques, usuari, element1, summary
   "upload": re.compile(ur'\x0314\[\[\x0307(?P<page>.*?)\x0314\]\]\x034 (?P<flags>upload)\x0310 \x0302\x03 \x035\*\x03 \x0303(?P<user>.*?)\x03 \x035\*\x03  \x0310.*\x0302(?P<element1>Fitxer:.*?)\x0310\]\]..?(?P<summary>.*)\x03?'),
   #Log:upload *overwrite* grups: page, usuari, element1, summary
   "overwrite": re.compile(ur'\x0314\[\[\x0307(?P<page>.*?)\x0314\]\]\x034 (?P<flags>overwrite)\x0310 \x0302\x03 \x035\*\x03 \x0303(?P<user>.*?)\x03 \x035\*\x03  \x0310.*\x0302(?P<element1>Fitxer:.*?)\x0310\]\].: (?P<summary>.*)'),

   #Log:delete *delete* *restore* grups: page, marques, usuari, element1, summary
   #                      "\x0314\[\[\x0307(?P<page>.*?)\x0314\]\]\x034 (?P<flags>delete|restore)\x0310 \x0302\x03 \x035\*\x03 \x0303(?P<user>.*?)\x03 \x035\*\x03  \x0310.*? «\[\[\x0302(?P<element1>.*?)\x0310\]\]»: (?P<summary>.*?)\x03"
   "delete": re.compile(ur'\x0314\[\[\x0307(?P<page>.*?)\x0314\]\]\x034 (?P<flags>delete|restore)\x0310 \x0302\x03 \x035\*\x03 \x0303(?P<user>.*?)\x03 \x035\*\x03  \x0310.*? «\[\[\x0302(?P<element1>.*?)\x0310\]\]»: (?P<summary>.*?)\x03'), # delete with summary and restore (always with summary)

   #Log:block *block* *unblock* grups: page, marques, usuari, blocat, durada, summary
   "block": re.compile(ur'\x0314\[\[\x0307(?P<page>.*?)\x0314\]\]\x034 (?P<flags>block)\x0310 \x0302\x03 \x035\*\x03 \x0303(?P<user>.*?)\x03 \x035\*\x03  \x0310.*? \[\[\x0302Usuari:(?P<blocked>.*?)\x0310\]\].*? de (?P<while>.*?) \((?P<options>.*?)\)(?:: (?P<summary>.*))?\x03'), # block with summary
   #Log:block *unblock* grups: page, marques, usuari, blocat, durada, summary
   "unblock": re.compile(ur'\x0314\[\[\x0307(?P<page>.*?)\x0314\]\]\x034 (?P<flags>unblock)\x0310 \x0302\x03 \x035\*\x03 \x0303(?P<user>.*?)\x03 \x035\*\x03  \x0310.*?\x0302.*?:(?P<blocked>.*?)\x0310: (?P<summary>.*)\x03'), # unblock with summary

   #Log:protect *protect* *modify* grups: page, marques, usuari, element1, summary
   "protect": re.compile(ur'\x0314\[\[\x0307(?P<page>.*?)\x0314\]\]\x034 (?P<flags>protect|modify)\x0310 \x0302\x03 \x035\*\x03 \x0303(?P<user>.*?)\x03 \x035\*\x03  \x0310.*?\x0302(?P<element1>.*?)\x0310.*?(?P<summary>.*?)\x03'),
   #Log:protect *unprotect* grups: page, marques, usuari, element1, summary
   "unprotect": re.compile(ur'\x0314\[\[\x0307(?P<page>.*?)\x0314\]\]\x034 (?P<flags>unprotect)\x0310 \x0302\x03 \x035\*\x03 \x0303(?P<user>.*?)\x03 \x035\*\x03  \x0310.*?\x0302(?P<element1>.*?)\x0310\]\](?P<summary>.*?)\x03'),

   #Log:patrol *patrol* grups: page, flags, user, element1
   #10.06.09              '\x0314\[\[\x0307(?P<page>.*?)\x0314\]\]\x034 (?P<flags>patrol)\x0310 \x0302\x03 \x035\*\x03 \x0303(?P<user>.*?)\x03 \x035\*\x03  \x0310.*?\x0302(?P<element1>.*?)\x0310.*?\x03'
   "patrol": re.compile(ur'\x0314\[\[\x0307(?P<page>.*?)\x0314\]\]\x034 (?P<flags>patrol)\x0310 \x0302\x03 \x035\*\x03 \x0303(?P<user>.*?)\x03 \x035\*\x03  \x0310.*?\x0302(?P<element1>.*?)\x0310\]\].*?\x03'),
   #MISSING: renameuser
}

def rc_events(text):
	for rc_re in IRC_RC_RE:
		m = IRC_RC_RE[rc_re].search(text)
		if m:
			opts = m.groupdict()
			opts['event'] = rc_re
			return opts
	return {'event': 'unknown', 'line': r'%r' % text}

