#!/usr/bin/env python
import os
from util.globals import Dicts, Logs
from files import File

def logs_():
	accounts = Dicts("accounts")
	channels = Dicts("channels")
	definitions = Dicts("definitions")
	igns = Dicts("igns")
	#ips = Dicts("ips")
	logs = Dicts("log")
	#users = Dicts("users")
	for log in (accounts, channels, definitions, logs):
		print log.name(), log()
	
	logs['interested']=["coet", "lluis_tgn", "Mafoso-Espieta", "krls-ca", "Vriullop", "Lohen", "Paucabot", "SMP_ca"]
	logs.update('usersQueue', [])
	logs.update('channels', {})
	logs.save()

def files_():
	logdir = os.path.join(os.getcwd(), "logs")
	f = File("av_log.bin", path=logdir)
	
	f.put(
		{
			"interested": ["coet", "lluis_tgn", "Mafoso-Espieta", "krls-ca", "Vriullop", "Lohen", "Paucabot", "SMP_ca"],
			"authorized": ["pasqual", "krls-ca", "Lohen", "SMP", "Vriullop"],
			"usersQueue": [],
			"channels": {}
		}
	)
	f.close()
	data=f.get()
	print data
	f.put(data)

g = Logs()
print g.interested
print g.logs()
print g.logs['interested']
	
