# -*- coding: utf8 -*-
"""
Function attributes:
* load: boolean. Optional. If False the function will not load.
* name: string. Optional.
* priority: string. Optional. Three values are available: "high", "medium" or "low",
  default value: "medium".
* thread: boolean. Optional. If True, function will work by starting a thread.
* rule: string or regexp object. Required.
* aliases: list of string or regexp objects. Optional.
* fullmsg: boolean. Optional. If True, pattern is searched on whole message, else
  pattern is a command, the message must begin with a sign.

* access
* evttypes: must be tuple
* skip_sentinel: skip sentinel instance
* limit
* channels
* url
"""

import json, os, re, time
from util.functions import *

def send_lists(bot, irc, cur):
    llista=cur.cmd
    nomLlista=""
    if llista=="llista" or llista=="cua":
       llista=g.usersQueue
       nomLlista="de voluntaris disponibles en cua"
    elif llista=="connectats":
       nomLlista="d'usuaris connectats"
       llista=bot.connected
    elif llista=="interessats":
       nomLlista="d'usuaris %s per ser avisats"%llista
       llista=g.interested
    elif llista=="operadors":
       nomLlista=u"d'%s"%llista
       llista=bot.channels[cur.sender].opers()
    elif llista=="moderadors":
       nomLlista="de %s" % llista
       llista=bot.channels[cur.sender].voiced()
    elif llista=="autoritzats":
       nomLlista="d'%s" % llista
       llista=g.logs['authorized']
    elif llista=="admins":
       nomLlista="d'%s"%llista
       llista=[]
       for usr in bot.connected:
          nickVP=WPnick(usr)
          if nickVP in ADMINS:
             if nickVP != usr:
                usr+=NORMAL+u" (VP: %s%s%s)"%(GREEN,nickVP,NORMAL)
             llista.append(usr)
    if nomLlista:
       txtLlista=bot.list_users(llista)
       msg=u"llista %s: %s."%(nomLlista, txtLlista)
       bot.pubmsg(msg)
       #irc.privmsg(cur.sender, msg.encode('utf-8'))
send_lists.rule=re.compile(r"^(connectats|llista|cua|operadors|moderadors|interessats|autoritzats|admins)$")
send_lists.showas = "connectats, llista, operadors, moderadors, interesats, autoritzats, admins"

def modify_list(bot, irc, cur):
   params = getParams(cur.cmdline)
   #{'cmd': u'ist', u'add': u'pasqual', u'r': u'Pasqual'}
   print params
   if 'a' in params:
      list_ = g.logs['authorized']
      if 'r' in params:
         if params['r'] in list_:
            list_.remove(params['r'])
         else:
            bot.pubmsg("%s no és a la llista" % params['r'])
            return "NO MORE"
      if 'add' in params:
         list_.append(params['add'])
      bot.pubmsg("S'han efectuats els canvis.")
      g.logs['authorized']=list_
      bot.save_log()
modify_list.rule = "list"

def remove_usr(bot, irc, cur):
    #traem l'usuari si es trau ell mateix, o si qui ho fa és un moderador
    requestedUser = cur.params or cur.nick
    usr=aliases(requestedUser)
    if usr in bot.connected:
       if ((cur.nick == usr) or (cur.nick != usr and cur.identifiedUser)):
           if usr in g.usersQueue:
              g.usersQueue.remove(usr)
              bot.save_log()
              usersQueue_str=bot.list_users(g.usersQueue)
              bot.pubmsg("s'ha eliminat l'usuari de la cua.")
              bot.pubmsg("llista de voluntaris disponibles en cua: %s." % encode_msg(usersQueue_str))
              if len(g.usersQueue)==0 and len(bot.connected)>0:
                  callUsers = list(bot.connected)
                  callUsers.remove(usr)
                  list_ = bot.list_users(callUsers)
                  list_ = "%s. " % list_ if  "(buida)" not in list_ else ""
                  list_ = list_.replace(u"·","")
                  qui = u"Algú vol " if len(callUsers)>1 else "Vols"
                  msg = u"%sLa llista és buida. %s entrar-hi?" % (list_, qui)
                  bot.pubmsg(encode_msg(msg))
           else:
              bot.pubmsg("l'usuari no figura a la llista.")
       else:
          bot.pubmsg("No teniu els permissos necessaris.")
    else:
          bot.pubmsg("L'usuari no existeix o no està present en estos moments.")
remove_usr.rule = re.compile(r'tr[ae]u|^-$')
remove_usr.showas = "treu"

def add_usr(bot, irc, cur):
    #afegix un usuari a la cua
    requestedUser = cur.params or cur.nick
    usr=aliases(requestedUser)
    if usr in bot.connected:
        if usr not in g.usersQueue:
            if ((cur.nick == usr) or (cur.nick != usr and cur.identifiedUser)):
               g.usersQueue.insert(0, usr)
               bot.save_log()
               usersQueue_str=bot.list_users(g.usersQueue)
               bot.pubmsg("s'ha afegit l'usuari a la cua.")
               bot.pubmsg("llista de voluntaris disponibles en cua: %s." % encode_msg(usersQueue_str))
            else:
               bot.pubmsg("No teniu els permissos necessaris.")
        else:
           bot.pubmsg("Ja consta aquest usuari a la llista")
    else:
        bot.pubmsg("L'usuari no existeix o no està present en estos moments.")
add_usr.rule = re.compile(r'afege?ix|^\+$')
add_usr.showas = "afegeix"

def change_queue_(bot, irc, cur):
   #passem l'usuari a la posició desitjada de la cua, sols per moderadors, que algun privilegi han de tenir
   if re.search(ur"^-?[1-9][0-9]*$",cmd) and identifiedUser:
      ordinal=int(cmd)
      if ordinal<0:
         ordinal=len(g.usersQueue)-abs(ordinal)
      else:
         ordinal-=1
      requestedUser = cur.params or cur.nick
      usr=aliases(requestedUser)
      if usr in bot.connected:
         if usr == cur.nick or (usr != cur.nick and identifiedUser):
            if usr in g.usersQueue:
               cuaUsuarisAbans = g.usersQueue
               g.usersQueue.remove(usr)
               g.usersQueue.insert(ordinal, usr)
               bot.save_log()
               usersQueue_str=bot.list_users(g.usersQueue)
               if cuaUsuarisAbans != g.usersQueue:
                  bot.pubmsg("s'ha modificat l'ordre de la cua.")
                  bot.pubmsg("llista de voluntaris disponibles en cua: %s."%usersQueue_str.encode('utf-8'))
               elif usr not in g.usersQueue:
                  g.usersQueue.insert(ordinal, usr)
                  bot.save_log()
                  usersQueue_str=bot.list_users(g.usersQueue)
                  bot.pubmsg("s'ha afegit l'usuari a la cua en l'ordre indicat.")
                  bot.pubmsg("llista de voluntaris disponibles en cua: %s."%usersQueue_str.encode('utf-8'))
               else:
                  bot.pubmsg(u"no teniu els permissos suficients per efectuar este canvi".encode('utf-8'))
      else:
         bot.pubmsg(u"l'usuari no està present o no existeix".encode('utf-8'))
change_queue_.load = False

def nocmd_addUsr_(bot, irc, cur):
   add_usr(bot, irc, cur, g)
nocmd_addUsr_.rule = re.compile(r"^(?:entr[eo]|present)[!.]?$")
nocmd_addUsr_.fullmsg = True

def nocmd_remUsr_(bot, irc, cur):
   remove_usr(bot, irc, cur, g)
nocmd_remUsr_.rule = re.compile(r"^(?:isc|(?:me'n|m'en) vaig|surto?|ara torn[eo]?)[!.]?$")
nocmd_remUsr_.fullmsg = True

def do_cmd(bot, irc, cur, g=None, chan=None):
    if not chan:
        chan=cur.target()
    cur.nick = nm_to_n(cur.source())
    cmd = fullCmd = cur.params[1:]
    identifiedUser=cur.nick in bot.channels[chan].voiced() or cur.nick in bot.channels[chan].opers()
    if " " in cmd:
        requestedUser=cmd.split(" ",1)[1]
        args=cmd.split(" ",1)[1]
        cmd=cmd.split(" ")[0]
        if "::" in requestedUser or u"·" in requestedUser:
            requestedUser=requestedUser.replace("::","").replace(u"·","")
    else:
        requestedUser=cur.nick
        args=u""
    cmd=cmd.lower()
    isCmd1=isCmd2=False
    if chan==bot.vchan:
        """
        ordres exclusives per al canals de vandalismes
        """
        #retorna les llistes d'usuaris
        if cmd=="ajuda":
            bot.pubmsg("vegeu: http://ca.wikipedia.org/wiki/Usuari:PasqualBot/IRC/ordres")
        else:
            nointerpretat1=True
    if chan != "": #forcem a entrar
        """
        ordres per a tots els canals
        """
        #comandes no vol dir ordres! xD SMP sempre s'enganya!
        if re.search(r"comand[eo]s",cmd):
                bot.pubmsg("DIEC: comanda:  f. [LC] Encàrrec")
                bot.pubmsg("esteu intentant aconseguir una llista de totes les @ordres? :P")
        #estadístiques
        elif cmd=="s":
            elimina_inactius()
            msg=estadistiques()
            bot.pubmsg(msg.encode("utf-8"))
        elif cmd=="ns":
            llista=NS.values()
            for el in llista:
              llista[llista.index(el)]=int(llista[llista.index(el)])
            llista.sort()
            nova_llista=[]
            for el1 in llista:
             for el2 in NS:
               if NS[el2]==str(el1):
                 nova_llista.append(BLUE+el2+NORMAL+": "+str(el1))
            for subllista in range(0, len(nova_llista), 10):
              llista=", ".join(nova_llista[subllista:subllista+10])
              bot.pubmsg(llista.encode("utf-8"))
        elif cmd == "ip" and args:
          ip=re.search("^(\d{1,3}\.){3}\d{1,3}$",args)
          msg=u"ip no vàlida"
          if ip:
            #msg="http://tools.wikimedia.de/~chm/whois.php?ip="+args
            msg="http://www.dnsstuff.com/tools/ipall.ch?domain="+args
            bot.pubmsg(msg.encode("utf-8"))
        #ordres disponibles
        elif cmd=="ordres":
            bot.pubmsg(BOLD+"ordres disponibles:"+NORMAL)
            bot.pubmsg(BLUE+"@afegeix "+NORMAL+"/"+BLUE+" @afegix "+NORMAL+"/"+BLUE+" @+"+NORMAL)
            bot.pubmsg(BLUE+"@treu "+NORMAL+"/"+BLUE+" @trau "+NORMAL+"/"+BLUE+" @-"+NORMAL)
            bot.pubmsg(BLUE+"@llista "+NORMAL+"/"+BLUE+" @cua"+NORMAL)
            bot.pubmsg("altres: "+BLUE+"@connectats"+NORMAL+", "+BLUE+"@interessats"+NORMAL+", "+BLUE+"@operadors"+NORMAL+", "+BLUE+"@moderadors"+NORMAL+", "+BLUE+"@admins"+NORMAL)
            bot.pubmsg(BLUE+"@cur(stat)"+NORMAL+" [a la VP]"+NORMAL)
            bot.pubmsg("contibucions:"+BLUE+" @irc "+NORMAL+"/"+BLUE+" @reg(istre)"+NORMAL+" [del bot], "+BLUE+"@irc "+NORMAL+"/"+BLUE+" @info "+NORMAL+"[del tools]")
            bot.pubmsg(BLUE+"@ign u"+NORMAL+": ignora les edicions d'un usuari durant 15 min."+BLUE+"@ign p"+NORMAL+": ignora les edicions en una pàgina durant 15 min.")
            bot.pubmsg(BLUE+"@ip"+NORMAL+": dades IP segons http://www.dnsstuff.com")
            bot.pubmsg(BLUE+"@defineix"+NORMAL+": registra una definició de l'usuari, "+BLUE+"@descriu"+NORMAL+": mostra la definició de l'usuari")
            bot.pubmsg(RED+"vegeu també"+NORMAL+": http://ca.wikipedia.org/wiki/Usuari:PasqualBot/IRC/ordres")
        #ajuda sintaxi de r
        elif cmd=="r?":
            bot.pubmsg("%r cur <usuari>: modifica les edicions de l'<usuari> al registre.")
            bot.pubmsg("%r d <usuari>: modifica la data de creació de l'<usuari>.")
            #bot.pubmsg("%r ")
        #definició del DIEC
        elif cmd=="diec" :
            bot.pubmsg("http://dlc.iec.cat/results.asp?txtEntrada="+urlLat(args))
        #retorna una URL del GREC amb la traducció castellà-català
        elif re.search("^(?:en|ang|fra?|de|ale|es|cas)-cat?$",cmd):
            l1= cmd.split("-")[0]
            #cast= b, frnc= irc, angl= d, alem= cur
            if l1 in ["es","cas"]:
             l1="b"
            elif l1 in ["fr","fra"]:
              l1="irc"
            elif l1 in ["en","ang"]:
              l1="d"
            elif l1 in ["de","ale"]:
              l1="cur"
            bot.pubmsg("http://www.grec.cat/cgibin/mlt003c.pgm?CBD=%s&GECART=%s"%(l1,urlLat(args)))
            #bot.pubmsg("http://www.grec.net/cgibin/mlt00x.pgm?CASTELL%C0.x=1&GECART="+urllib.quote(urlLat(args))
        #traduccions d'un mot català als idiomes del GREC
        elif re.search("^trads$|^cat?-(?:en|ang|fra?|de|ale|es|cas)$",cmd):
            bot.pubmsg("http://www.grec.net/cgibin/mlt00x.pgm?=1&GECART="+urlLat(args))
        elif cmd == "dgec":
            bot.pubmsg("http://ec.grec.net/cgi-bin/AppDLC3.exe?APP=CERCADLC&GECART="+urlLat(args))
        elif cmd == "gec":
            bot.pubmsg("http://www.grec.cat/cgibin/gec3cencp.pgm?PAG=0001&CERCA="+urlLat(args))
        #fixem definició d'un usuari existent al registre
        elif re.search(r"^def(ine?ix)?$",cmd):
            try:
               requestedUser=requestedUser.split(" ")[0]
               definicio=' '.join(fullCmd.split(" ")[2:])
            except:
                definicio=""
            cur.nick=nomVP(requestedUser)
            definit=definix(cur.nick,definicio)
            bot.pubmsg(definit.encode("utf-8"))
        #retorna definició fixada al registre d'usuaris
        elif re.search(r"^desc(riu)?$",cmd):
            element=args
            tipus=""
            if " -" in args and args[-1] in "uid":
              tipus= args[-2:]
              element=args[:-3]
            definicio=descripcio(element, tipus)
            if definicio:
              msg=quietNick(element,bot.connected)+": "+definicio
              bot.pubmsg(msg.encode("utf-8"))
            else:
                msg="sense arguments"
                bot.pubmsg(msg.encode("utf-8"))
        #estat de l'usuari a la Viquipèdia
        elif re.search(r"^cur(?:stat)?$", cmd):
            usuari=nomVP(requestedUser)
            estat=getURL("http://%s.%s.org/wiki/Usuari:%s/Estat"%(LANG,FAM,urlWiki(usuari))).split('<!-- start content -->')[1].split('<!-- end content -->')[0].decode('utf-8','replace')
            if 'id="noarticletext"' not in estat:
                try:
                    estat=estat.split('<p>')[1].split('</p>')[0]
                    if not estat in [u'en línia','desconnectat', 'connectat', 'ocupat', 'inactiu','Funcionant','Aturat']:
                        estat="desconegut"
                except:
                    estat="desconegut"
                if estat in [u"en línia","connectat","Funcionant"]:
                    estat=BOLD+GREEN+estat+NORMAL
                elif estat=="ocupat":
                    estat=BOLD+OLIVE+estat+NORMAL
                elif estat in ["desconnectat", "Aturat"]:
                    estat=BOLD+RED+estat+NORMAL
                else:
                    estat=BOLD+DARK_GRAY+estat+NORMAL
                estat2, darreraEdicio =estatVP(usuari,LANG,FAM)
                msg=u"L'estat de l'usuari %s en la Viquipèdia és: %s. Darrera edició %s" % (quietNick(usuari,bot.connected), estat,\
                      time.strftime("%H:%M (%d-%m-%y)",time.localtime(darreraEdicio)))
                bot.pubmsg(msg.encode('utf-8'))
            else:
                estat, darreraEdicio =estatVP(usuari,LANG,FAM)
                if estat ==0:
                    estat=BOLD+GREEN+"connectat"+NORMAL
                elif estat==1:
                    estat=BOLD+OLIVE+"absent"+NORMAL
                else:
                    estat=BOLD+DARK_GRAY+"desconegut"+NORMAL
                if darreraEdicio:
                    estat=estat+u". Darrera edició "+time.strftime("%H:%M (%d-%m-%y)",time.localtime(darreraEdicio))
                msg=u"L'estat de l'usuari %s en la Viquipèdia és: %s"%(quietNick(usuari,bot.connected),estat)
                bot.pubmsg(msg.encode('utf-8'))
                #bot.pubmsg(u"Usuari sense pàgina d'estat o inexistent.".encode('utf-8'))
        #contribucions de l'usuari segons el registre del bot
        elif cmd =="irc":
            usuari=requestedUser
            if " " not in fullCmd:
              usuari=nomVP(usuari)
            else:
              usuari=fullCmd.split(" ",1)[1]
            usuari=nomVP(usuari)
            usuari=usuari.replace(" ","_")
            if not isip(usuari):
              for usr in dUsuaris.keys():
                #print "usr: '%s'; usuari: '%s'" %(usr,usuari)
                if re.search(ur"(^"+usuari+ur"$)",usr,re.I):
                  usuari=re.match(ur"(^"+usuari+ur"$)",usr,re.I).group(1)
                  break
            contribs=n_edicions(usuari)
            darreraContr = darreraContrib(usuari)
            if contribs < 0:
                msg=u"usuari desconegut."
            else:
                msg=u"Segons el meu registre, %s tenia %s contribucions a les %s"%(quietNick(usuari,bot.connected),TEAL+str(contribs)+NORMAL,time.strftime("%H:%M (%d-%m-%y)",time.localtime(darreraContr)))
            bot.pubmsg(msg.encode('utf-8'))
            msg=u"http://ca.wikipedia.org/wiki/Especial:Contribucions/%s"%urlWiki(usuari)
            bot.pubmsg(msg.encode('utf-8'))
        #contribucions de l'usuari segons el tools
        elif cmd == "info":
            if " " not in fullCmd:
               usuari=nomVP(usuari)
            else:
              usuari=fullCmd.split(" ",1)[1]
            usuari=nomVP(requestedUser)
            usr_=usuari.replace(" ","_")
            try:
              contribs=comptaedicions(usr_ ,LANG,FAM)
            except:
              contribs=comptaedicionsVP(usr_,LANG,FAM)
            if dUsuaris.has_key(usr_) and dUsuaris[usr_][2]<contribs:
                dUsuaris[usr_][2]=contribs
            if not isip(usuari):
                msg="Segons el toolserver, %s"%quietNick(usuari,bot.connected)
            else:
                msg=u"Segons la pàgina [[Especial:Contribucions/%s]]"%quietNick(usuari,bot.connected)
            msg+=u" té actualment %s edicions registrades."%(TEAL+str(contribs)+NORMAL)
            bot.pubmsg(msg.encode('utf-8'))
            msg=u"http://ca.wikipedia.org/wiki/Especial:Contribucions/%s"%urlWiki(usuari)
            bot.pubmsg(msg.encode('utf-8'))
        elif cmd=="tots" and usuari in moderadors:
            avisals=g.usersQueue
            if usuari in avisals:
                 avisals.remove(usuari)
            if avisals:
                 usuaris=', '.join(g.usersQueue)
                 usuaris+=". %s avisa:"%usuari
                 bot.pubmsg("%s"%usuaris)
                 msg = re.sub(r"^tots ","",fullCmd)
                 #msg = fullCmd.split(" ",1)[1])
            else:
                msg=RED+u"Ho sentim, en estos moments no hi ha ningú disponible."+NORMAL
            bot.pubmsg("%s"%msg.encode("utf-8"))
        elif cmd=="rc":
            bot.pubmsg("irc://irc.wikimedia.org/"+LANG+"."+FAM+"".encode('utf-8'))
        elif cmd=="r":
            msg=""
            llista=[]
            args= re.sub(r"^r ","",fullCmd)
            if "-lu" in args:
                llista=dUsuaris.keys()
            elif "-li" in args:
                llista=dIPs.keys()
            elif "-ld" in args:
                llista=dAltres.keys()
            llista.sort()
            coincid=""
            llista_nova=llista
            if len(args)>4:
                coincid=args[4:].replace('"',"")
                assolit=False
                llista_nova=[]
                for el in llista:
                  if el.startswith(coincid):
                    assolit=True
                    llista_nova.append(el)
                  elif assolit==True:
                    break
            hihames=False
            llista_nova100=llista_nova
            if len(llista_nova)>100:
              llista_nova100=llista_nova[0:100]
              hihames=True
            if llista_nova100:
               msg=u"s'han trobat %i coincidències de un total de %i usuaris al registre."%(len(llista_nova),len(llista))
               irc.privmsg(usuari,msg.encode('utf-8'))
               if hihames:
                 msg=u"degut a l'extensió de la llista es mostraran els 100 primers"
                 irc.privmsg(usuari,msg.encode('utf-8'))
               thread.start_new_thread(bot.escriullista,(usuari,llista_nova100))
            else:
               msg=RED+u'llista buida'+NORMAL
               bot.pubmsg(msg.encode('utf-8'))
        elif cmd=="reinicia't":
            autoritzats=re.search("pasqual|iradigalesc",usuari.lower()) and (usuari in moderadors or usuari in operadors)
            if autoritzats:
               bot.pubmsg("reiniciant...")
               thread.interrupt_main()
            else:
                bot.pubmsg("sí, home! :P")
        elif cmd=="compta":
            msg=u"la cadena conté %s%i%s caràcters"%(TEAL,len(args),NORMAL)
            bot.pubmsg(msg.encode("utf-8"))
        elif cmd=="ign":
            global ign
            el=args[0]
            nom_el=args[2:]
            if el in ['p','u']:
              ign[el][nom_el]=anotatemps()+900
              if el=='u':
                el="l'usuari"
              else:
                el=u"la pàgina"
              msg=u"s'ignorarà %s %s%s%s durant quinze minuts" % (el,BLUE,nom_el,NORMAL)
              bot.pubmsg(msg.encode("utf-8"))
        elif cmd=="igns" and not args:
            igns=ign['p'].copy()
            for i in igns:
              if ign['p'][i]<anotatemps():
                 del ign['p'][i]
            igns=ign['u'].copy()
            for i in igns:
              if ign['u'][i]<anotatemps():
               del ign['u'][i]
            elements=""
            for l in ['p','u']:
              els=ign[l].keys()
              if not els:
                continue
              els=bot.list_users(els)
              if l == 'p':
                tipus=u"les pàgines"
              else:
                conj=""
                if elements:
                  conj=", "
                tipus=conj+"els usuaris"
              elements+=tipus+": "+els
            if elements:
              msg=u"els elements ignorats són: %s." % (elements)
            else:
              msg="no hi ha elements a ignorar."
            bot.pubmsg(msg.encode("utf-8"))
        #no s'ha pogut interpretar
        else:
            isCmd2=True
    if [isCmd1, isCmd2] == [True, True] or (chan != bot.vchan and isCmd2):
        reply=choice(["volies dir @ordres?","segur que volies escriure això?","ordre desconeguda","pss..."])
        bot.pubmsg(reply)
