#!/usr/bin/env python
bot = {
	"label": "freenode",
	"server": {
		"host": 'irc.freenode.net',
		"port": 6667,
		"password": ""
	},
		"channels": [
		'##botzilla',
		'##bots-ca',
		'##pampolut'
	],
	"user": {
		"nickname": 'buggybot',
		"ircname": 'pybot',
		"realname": 'geni 2.0',
		"password": "----------"
	},
	"owner": 'coet',
	"killword": "--------",
	"bootword": "--------",
	"folders": [
		"freenode",
		"common",
		#"adapting"
	],
	"triggers": "[\.!@?]",
	"reconnection_interval": 60,
	"otherbots":["geni", "botzil-la", "orejotas",],
	"help_url": "http://ca.wikipedia.org/wiki/User:TronaBot/IRC/ordres_geni",
}

bot2={
	"label": "wikimedia",
	"server": {
		"host": 'irc.wikimedia.org',
		"port": 6667,
		"password": ""
	},
	"channels": ['#ca.wikipedia',"#no.wikipedia", "#zh.wikipedia"],
	"user": {
		"nickname": 'rc_nemesian',
		"ircname": 'pybot2',
		"realname": 'vf-irclib2.0',
		"password": ""
	},
	"owner": 'pasqual',
	"killword": "secret",
	"bootword": "reboot",
	"folders": ["wikimedia", "common"],
	"triggers": "[\.!@?]",
	"reconnection_interval": 60,
	"otherbots": [],
	"help_url": "http://ca.wikipedia.org/wiki/User:TronaBot/IRC/ordres_geni",
}
