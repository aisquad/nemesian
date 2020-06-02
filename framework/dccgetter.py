#!/usr/bin/python

CONFIG_FILE="/home/asus/dccgetter/dccgetter.conf"
DEFAULT_CONFIG_SECTION="DCC"


###############################################################################
### Don't touch anything below this line unless you know what you are doing ###
###############################################################################

### This program is free software; you can redistribute it and/or modify ###
### it under the terms of the GNU General Public License as published by ###
### the Free Software Foundation; either version 2 of the License, or    ###
### (at your option) any later version.                                  ###


import ConfigParser,string,sys,os,re,struct,time
SHUT_RDWR=2

def dccGET(startpos):
	import socket
	socket.setdefaulttimeout(SOCKET_TIMEOUT)
	global TRANSFER_STATS
	if startpos>0:
		try:
			CONNECTED=False
			BOUND=False
			try:
				event=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM,0)
				event.settimeout(RESUME_TIMEOUT)
				if os.access(TMP_PATH+"/"+FILE+"_"+str(PORT),os.F_OK):
					os.unlink(TMP_PATH+"/"+FILE+"_"+str(PORT))
				event.bind(TMP_PATH+"/"+FILE+"_"+str(PORT))
				os.chmod(TMP_PATH+"/"+FILE+"_"+str(PORT),0600)
				BOUND=True
				event.listen(1)
				try:
					os.write(2,"Sending RESUME request from position %d\n" % startpos)
				except: pass
				os.write(0,"PRIVMSG %s :\x01DCC RESUME %s %d %d\x01\n" % (NICK,FILE,PORT,startpos))
				(s,addr)=event.accept()
				CONNECTED=True
				s.settimeout(10.0)
				buffer=s.recv(BUFDIM)
				if int(buffer)!=startpos:
					raise ValueError
				s.close()
				try: os.write(2,"Resuming %s\n" % FILE)
				except: pass
			finally:
				try:
					event.close()
					os.unlink(TMP_PATH+"/"+FILE+"_"+str(PORT))
				except: pass
		except socket.error, msg:
			if not BOUND:
				os.write(2,"Can't bind unix socket to: %s" % (TMP_PATH+"/"+FILE+"_"+str(PORT)))
			elif not CONNECTED:
				os.write(2,"No DCC ACCEPT received from %s\nI cannot safely resume or get the file... aborting.\n" % NICK)
			else:
				os.write(2,"Internal error - unix socket timeout?: %s\n" % msg)
			return
		except ValueError:
			os.write(2,"Ehmmm, wrong RESUME POSITION in sender's DCC ACCEPT\n")
			return
		except:
			os.write(2,"Woops, unrecoverable error: %s\n" % sys.exc_info()[1])
			return

	(ACK,BAR,TIME,CONNECTED)=(0,0,0,False)
	ADDRESS=socket.inet_ntoa(struct.pack("I",socket.htonl(IP)))
	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM,0)
	for retry in range(CONNECT_RETRIES):
		try:
			s.connect((ADDRESS,PORT))
			CONNECTED=True
			break
		except:
			try:
				os.write(2,"%s - Can't connect to %s:%s -  %s\n" % (FILE,ADDRESS,PORT,sys.exc_info()[1]))
			except: pass
		if retry==CONNECT_RETRIES-1 and not GUESS_SENDER_HOST:
				s.close()
				os.write(2,"%s - Connect failed. Transfer aborted\n" % FILE)
				return
		time.sleep(RETRY_DELAY)
	if not CONNECTED:
		try: os.write(2,"%s - Connect failed. Guessing sender host...\n" % FILE)
		except: pass
		try:
			try:
				if len(USER)!=3 or len(USER[2])==0: raise
			except: raise Exception("format")
			if socket.gethostbyname(USER[2])==ADDRESS: raise Exception("sameaddr")
		except Exception, E:
			if E.args==("format",):
				os.write(2,"%s - nick!ident@host format error. Transfer aborted...\n" % FILE)
			elif E.args==("sameaddr",):
				os.write(2,"%s - Guessed host matches the one provided in the DCC request. Aborting\n" % FILE)
			else:
				os.write(2,"%s - Error resolving: %s - %s\n" % (FILE,USER[2],E))
			s.close()
			return
		try: s.shutdown(SHUT_RDWR)
		except: pass
		for retry in range(CONNECT_RETRIES_GUESS_MODE):
			try:
				s.connect((USER[2],PORT))
				break
			except:
				try:
					os.write(2,"%s - Can't connect to %s:%s -  %s\n" % (FILE,USER[2],PORT,sys.exc_info()[1]))
				except: pass
			if retry==CONNECT_RETRIES_GUESS_MODE-1:
				s.close()
				os.write(2,"%s - Sorry. Guessed host doesn't work. Transfer aborted\n" % FILE)
				return
			time.sleep(RETRY_DELAY_GUESS_MODE)
	BAR=int(startpos*1.0*TRANSFER_STATS/SIZE)
	s.settimeout(RECV_TIMEOUT)
	TIME=time.time()
	while True:
		try:
			buffer=s.recv(BUFDIM)
			if not buffer: break
			fd.write(buffer)
			ACK+=len(buffer)
			s.send(struct.pack("I",socket.htonl(ACK+startpos)))
			if TRANSFER_STATS<=0: continue
			if ((ACK+startpos)*1.0/SIZE>=BAR*1.0/TRANSFER_STATS):
				output="%s - %3d%% " % (FILE,((ACK+startpos)*100.0/SIZE))
				for x in range(BAR_LENGTH):
					if x<=(BAR_LENGTH*(ACK+startpos)*1.0/SIZE): output+="#"
					else: output+="_"
				os.write(2,"%s|  %.2f kB/s\n" % (output,ACK/((time.time()-TIME)*1024)))
				BAR=int((ACK+startpos)*1.0*TRANSFER_STATS/SIZE+1)
		except socket.error:
			break
		except:
			# disabling progress bar logging due to the psybnc bug.
			TRANSFER_STATS=0
	s.close()
	os.write(2,"%s - %d bytes received in %.2f seconds\n" % (FILE,ACK,time.time()-TIME))
	if (ACK+startpos)!=SIZE:
		os.write(2,"%s - Warning: file size does not match expected one. Probably transfer has been aborted.\n" % FILE)


cf=ConfigParser.RawConfigParser()
cf.readfp(open(CONFIG_FILE))
if cf.has_section(DEFAULT_CONFIG_SECTION):
	for o,v in cf.items(DEFAULT_CONFIG_SECTION):
		exec(string.upper(o)+'=%s' % v)
else:
	os.write(2,"Woops, no section %s defined in %s!\n" % (DEFAULT_CONFIG_SECTION,CONFIG_FILE))
	sys.exit(1)

P=[]
if len(sys.argv) != 6:
	CNT=1
	while (os.environ.has_key("P"+str(CNT))):
		P.append(os.environ["P"+str(CNT)])
		CNT+=1
	if CNT<9:
		os.write(2,"Usage:\n%s <nick!user@host> <file> <ip> <port> <size>\n" % sys.argv[0])
		os.write(2,"If called without arguments it will search for Pnn-Variables as described in psybnc/SCRIPTING\n")
		sys.exit(1)
	USER=re.split("!|@",P[0])
	NICK=string.lstrip(USER[0],":")
	FILE="_".join(P[5:len(P)-3])
	IP=P[len(P)-3]
	PORT=P[len(P)-2]
	SIZE=string.rstrip(P[len(P)-1],"\x01")
else:
	P.append(sys.argv[1])
	USER=re.split("!|@",sys.argv[1])
	NICK=USER[0]
	FILE=re.split('/',sys.argv[2])
	FILE=FILE[len(FILE)-1]
	IP=sys.argv[3]
	PORT=sys.argv[4]
	SIZE=sys.argv[5]

try:
	IP=int(IP)
	PORT=int(PORT)
	SIZE=int(SIZE)
except:
	os.write(2,"Wooops, something wrong with ip address, port or filesize!\n");
	sys.exit(1)

if IGNORECASE:
	RE_FLAGS=re.IGNORECASE
else:
	RE_FLAGS=0

if string.lower(POLICY)=="allow":
	if len(BLACKLISTED_USERS)>0:
		if re.match("|".join(BLACKLISTED_USERS),string.lstrip(P[0],":"),RE_FLAGS):
			os.write(2,"User %s is BLACKLISTED!\n" % NICK)
			sys.exit(1)
else:
	if len(WHITELISTED_USERS)==0 or not re.match("|".join(WHITELISTED_USERS),string.lstrip(P[0],":"),RE_FLAGS):
		os.write(2,"User %s isn't in whitelist... denying\n" % NICK)
		sys.exit(1)
os.umask(CONFIG_UMASK)
try: os.write(2,"Accepting %s - %s bytes\n" % (FILE,SIZE))
except: pass

try:
	if RESUME and os.access(DOWNLOAD_DIR+"/"+FILE,os.F_OK):
		fd=file(DOWNLOAD_DIR+"/"+FILE,"a")
	else:
		fd=file(DOWNLOAD_DIR+"/"+FILE,"w+")
except:
	os.write(2,"Mhm, cannot open file %s: %s\n" % (FILE,sys.exc_info()[0]))
	sys.exit(1)

try:
	if fd.tell()<SIZE:
		dccGET(fd.tell())
	else:
		os.write(2,"File is already completed\n")
except:
	pass
fd.close()

