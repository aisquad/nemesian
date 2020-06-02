# -*- coding: utf8 -*-
# gadgets.py

import os, re, time
from framework.irclib import irc_lower
from random import randint, choice

from util.globals import *

"""
Function attributes:
* load: boolean. Optional. If False the function will not load.
* name: string. Optional.
* priority: string. Optional. Three values are available: "high", "medium" or "low", default value: "medium".
* thread: boolean. Optional. If True, function will work by starting a thread.
* rule: string or regexp object. Requered.
* aliases: list of string or regexp objects. Optional.
* sentence: boolean. Optional. If True, pattern is searched on whole message, else pattern is a command, it begins
  the msg with a sign.
"""

def priv_gadget(bot, irc, cur):
        #print "\n==",cur.eventtype(),"\n",cur.tmsget(),"\n",cur.source(),"\n",cur.msguments(),"\n==\n"
        msg = cur.params
        interv = nm_to_n(cur.source())
        canal=bot.vchan
        canal2=bot.tchan
        #envia un missatge al canal #wikipedia-ca-sysop en nom del bot
        if msg[0]=="!":
            reply=msg[1:]
            irc.privmsg(canal, reply.encode('utf-8'))
            interv=quietNick(interv,bot.connected)
            reply=u"<"+BOLD+interv+NORMAL+"> envia al xat: "+BLUE+reply+NORMAL
            irc.privmsg(canal2,reply.encode('utf-8'))
        #envia un missatge a l'usuari indicat per exemple "@user hola" envia "hola" a <user>(obre un privat amb <user>)
        elif msg[0]=="%":
            destinatari_privat=msg.split(" ")[0][1:]
            reply=msg.lstrip("@"+destinatari_privat+" ")
            try:
                irc.privmsg(destinatari_privat.encode('utf-8'),reply.encode('utf-8'))
                interv=quietNick(interv,bot.connected)
                reply=u"<"+BLACK+interv+NORMAL+"> envia un priv a: "+DARK_GREEN+BOLD+destinatari_privat+NORMAL+". Ha escrit: "+BLUE+reply+NORMAL
                if len(reply)>200: reply=reply[:200]
                irc.privmsg(canal2,reply.encode('utf-8'))
            except:
                irc.privmsg(interv, u"sisplau, no poses accents en missatges privats, encara no ho hem solventat.".encode('utf-8'))
                interv=quietNick(interv,bot.connected)
                reply=u"<"+BOLD+interv+NORMAL+"> "+BLUE+"ha enviat un missatge a "+RED+destinatari_privat+BLUE+" amb accents!"
                irc.privmsg(canal2,reply.encode('utf-8'))
        elif msg[0]=="@":
                bot.executa(cur, msg[1:])
        #retorna al xat el missatge que l'usuari li ha enviat
        else:
            reply=msg[1:]
            if reply.startswith("/me "):
                reply=reply[4:]
                if len(reply)>200: reply=reply[:200]
                irc.action(canal,reply.encode('utf-8'))
            else:
                #per fer-lo més real, afegim (simulem) un temps de reacció (i tecleig)
                time.sleep(2+len(msg)/3)
                reply=u"%s m'ha dit: %s xD"%(interv, msg)
                if len(reply)>200: reply=reply[:200]
                irc.privmsg(canal, reply.encode('utf-8'))
            interv=quietNick(interv,bot.connected)
            reply=u"<"+BOLD+interv+NORMAL+"> ha escrit: "+BLUE+reply+NORMAL
            irc.privmsg(canal2,reply.encode('utf-8'))

def pub_gadget(bot, irc, cur):
    msg=cur.params
    #envia un missatge al canal #wikipedia-ca en nom del bot
    if msg.startswith("$!"):
        reply=msg[2:]
        if reply.startswith("/me "):
            reply=reply[4:]
            irc.action(bot.vchan, reply.encode('utf-8'))
        else:
            irc.privmsg(bot.vchan, reply.encode('utf-8'))
    #retorna els usuaris connected a #wikipedia-ca
    elif msg=="$%":
        presents=[]
        for usr in bot.connected:
            usr=quietNick(usr,bot.connected)
            presents.append(usr)
        reply=', '.join(presents)
        reply=DARK_GREEN+u"usuaris connected: "+NORMAL+reply
        irc.privmsg(bot.tchan,reply.encode('utf-8'))
    #envia un missatge a l'usuari indicat per exemple "@user hola" envia "hola" a <user>(obre un privat amb <user>)
    elif msg.startswith("$@"):
        ara=int(time.time())
        destinatari_privat=msg.split(" ")[0][2:]
        reply=u""+msg[len("@"+destinatari_privat+" "):]
        irc.privmsg(destinatari_privat.encode('utf-8'), reply.encode('utf-8'))
        nick=quietNick(interv,bot.connected)
        reply=u"<"+BOLD+nick+NORMAL+"> envia un priv a: "+DARK_GREEN+NEGRETA+destinatari_privat+NORMAL+". Ha escrit: "+BLUE+reply+NORMAL
        irc.privmsg(bot.tchan,reply.encode('utf-8'))
    elif msg.startswith("$#"):
        sporadic_canal=msg[1:msg.find(" ")]
        if sporadic_canal == "#":
            sporadic_canal="#wikipedia-ca"
        elif sporadic_canal == "#1":
            sporadic_canal=bot.vchan
        elif sporadic_canal == "#2":
            sporadic_canal=bot.tchan
        elif sporadic_canal == "#3":
            sporadic_canal=bot.schan
        if sporadic_canal in [bot.vchan, bot.tchan, bot.schan]:
            reply=msg[msg.find(" ")+1:]
            irc.privmsg(encode_msg(sporadic_canal), encode_msg(reply))
            return
        else:
            irc.join(sporadic_canal)
            reply=msg[msg.find(" ")+1:]
            irc.privmsg(encode_msg(sporadic_canal), encode_msg(reply))
            irc.send_raw("PART " + encode_msg(sporadic_canal))
