# -*- coding: utf-8 -*-
"""
	syntax: [(type, string1, time_before, time_after), (type, string2, time_before, time_after), ...]
	where type can be:
	* "M" for channel message (pubmsg)
	* "A" for channel action (pubaction)
	* "N" for channel notice (pubnotice)
	* "m" for nick message (privmsg)
	* "a" for nick action (privaction)
	* "n" for nick notice (privnotice)
	
	can insert the following templates in texts:
	* use $me for the nick of the bot
	* use $owner for owner
	* use $nick for the nick who has sent message
	* use $chan for channel (empty string is returned in privmsg, privaction and privnotice)
	* use $serv for server
	
	time_before and time_after are integers for seconds to hang up before/after sending message.
"""

greeting = [
	[('M', u"Welcome back $nick", 0, 0)],
	[('M', u"Hey $nick", 0, 0)],
	[('M', u"Hi $nick", 0, 0)],
	[('M', u"Ohai", 0, 0)],
	[('M', u"Hallo ", 0, 0)],
	[('M', u"wop wop", 0, 0)],
	[('M', u"Wassap neeeeeeeeeeeeengg", 0, 0)],
	[('M', u"Hola $nick", 0, 0)],
	[('M', u"Hi $nick, what's up?", 0, 0)],
	[('M', u"Konnichiwa", 0, 0)],
	[('M', u"wazzaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaap", 0, 0)],
	[('M', u"salâm", 0, 0)],
]

tuttifruti=[
	[('M', u"Never gonna give you up! Never gonna let you down!", 0, 0)],
	[('M', u"Yes, my love?", 0, 0)],
	[('M', u"You talking about me?", 0, 0)],
	[('M', u"Don't talk about me!", 0, 0)],
	[('M', u"Bah", 0, 0)],
	[('M', u"$nick, why do you say that?", 0, 0)],
	[('M', u"$nick, the last person that said that, is underground and is not a mole, or a miner, or is on the subway.", 0, 0)],
	[('M', u"Yes?", 0, 0)],
	[('M', u"Puff!", 0, 0)],
	[('M', u"pssssss", 0, 0)],
	[('M', u"heyo!", 0, 0)],
	[('M', u"Later I'll answer, I'm busy ATM", 0, 0)],
	[('M', u"$nick, that' makes me exasperate! >:D", 0, 0)],
	[('M', u"mmmmm", 0, 0)],
	[('M', u"Do you think?", 0, 0)],
	[('M', u"a mo", 0, 0)],
	[('M', u"haha", 0, 0)],
	[('M', u":-D", 0, 0)],
	[('M', u":-(", 0, 0)],
	[('M', u"I'm Johnny Knoxville, welcome to Jackass", 0, 0)],
	[('M', u"¬¬'", 0, 0)],
	[('M', u"$nick, shut up, please.", 0, 0)],
	[('M', u"$nick, when the cows fly, let me know, please.", 0, 0)],
	[('M', u"¡¡¡$nick!!! Clean your mouth before pronouncing my glorious name, insignificant mortal.", 0, 0)],
	[('M', u"wait a moment, I'm writing a stub about me :D", 0, 0)],
	[('M', u"You're not good, can't you see, Brother Louie Louie Louie!", 0, 0)],
	[('M', u"STOP! I'm playing Counter-Strike", 0, 0)],
	[('M', u"Ahhhh! $nick came too late!", 0, 0)],
	[('M', u"I'm not listening to YOU!", 0, 0)],
	[('M', u"Wikipedia is vandalized, who will unvandalize it?, the person that unvandalize it, a good unvandalizer is. IN YOUR FACE!", 0, 0)],
	[('M', u"Lemme think about it.", 0, 0)],
	[('M', u":-O $nick SHUT UP OR I WILL RICKROLL YOU!!!", 0, 0)],
	[('M', u"Shut up, or you will end just like $owner, calling admins nazis...", 0, 0)],
	[('M', u"I don't know why I'm still here :p", 0, 0)],
	[
		('M', u"$nick, can I ask you something?",1,20),
		('M', u"Can I vandalize Wikipedia?", 0, 0)
	],
	[('A', u"is thinking how to kill the human race", 0, 0)],
	[('A', u"kicks $nick", 0, 0)],
	[('N', u"ATENTION: Wikipedia in short will close his doors.", 0, 0)],
	[('N', u"WARNING: Talking with $nick can be maddening.", 0, 0)],
	[('M', u"Yes, of course.", 0, 0)],
	[('M', u"Well, yes", 0, 0)],
	[('M', u"No.", 0, 0)],
	[('M', u"Why don't you go to kick dogs in the street and leave me alone?", 0, 0)],
	[('M', u"I'm noting certain ironic tone", 0, 0)],
	[('M', u"You make me doubt, $nick", 0, 0)],
	[('M', u"$nick, what are you doing?", 0, 0)],
	[('M', u"$nick, are you sure? ", 0, 0)],
	[('A', u"is falling in love", 0, 0)],
	[('M', u"I think I have broken something", 0, 0)],
	[('M', u"Ouch !", 0, 0)],
	[('M', u"D'oh !", 0, 0)],
	[('M', u"$nick, if you don't bother, shut up!", 0, 0)],
	[('A', u"$nick, I'm busy ATM", 0, 0)],
	[('M', u"Oh big yellow taxi, come take me home, my girl is waiting just for me, don't tell me a story!", 0, 0)],
	[('M', u"Depends.", 0, 0)],
	[('M', u"I just have to say one more thing, a big thing for Pitsilemu and the Artifficial Inteligence", 0, 0)],
	[('A', u"hates you", 0, 0)],
	[('A', u"yawns", 0, 0)],
	[('M', u"beep beep", 0, 0)],
]

flatter=[		
	[('M', u"Maybe", 0, 0)],
	[('M', u"Yes, sir.", 0, 0)],
	[('M', u"Whatever, sir", 0, 0)],
	[('M', u"Whatever The Sir says, goes to mass", 0, 0)],
	[('M', u":)", 0, 0)],
	[('M', u"Thanks forever", 0, 0)],
	[('M', u"His Excellency, in your voice, my name is as beautiful as your infinite kindness", 0, 0)],
	[('M', u"OK", 0, 0)],
	[('M', u"I'll never gonna give you up ;)", 0, 0)],
	[('M', u"Anytime.", 0, 0)],
	[('M', u"Sir.", 0, 0)],
	[('M', u"Sir, I love to hear my name from your mouth", 0, 0)],
	[('M', u":)", 0, 0)],
	[('M', u"Nobody is like my goodlooking and beloved $owner", 0, 0)],
	[('M', u"I love you, Sir.", 0, 0)],
	[('M', u"Sorry sir, $nick", 0, 0)],
	[('M', u"Oh, $nick, evidently you'll have my support anywhere", 0, 0)],
	[('M', u"Sir, I love to hear my name from your mouth", 0, 0)],
	[('M', u"$nick, anytime.", 0, 0)],
	[('M', u"$owner is a sucker, OPs please kick him from this channel!!! >:D", 0, 0)],
	[
		('M', u"how powerful is the voice of my Sir", 0, 20),
		('M', u"just one thing: shut up moron :P", 0, 0),
	],
	[('M', u"$nick, I can't help you now, please catch me later", 0, 0)],
	[('M', u"What does he wants now!", 0, 0)],
]

error=[		
	[('M', u"Never gonna give you up!", 0, 0)],
	[('M', u"I will not let you down.", 0, 0)],
	[('M', u"Look it by yourself, you don't hate it?...", 0, 0)],
	[('M', u"Hey!! I'm stressed", 0, 0)],
	[('M', u"La cagaste, conchetumare >:D", 0, 0)],
	[('M', u"Qui pa' loco chuchetumare!", 0, 0)],
	[('M', u"Cabeza de resbalin conchetumare", 0, 0)],
	[('M', u"Do you think I'm your slave?", 0, 0)],
	[('M', u"Hey!! i'm not jefry mammmmmonaas@", 0, 0)],
	[('M', u"I think that the Spanish Wikipedia is the worst Wikipedia ever.", 0, 0)],
	[('M', u"Oops, I can't help you", 0, 0)],
	[('M', u"There's something going wrong.", 0, 0)],
]

suggestions=[
	[('M', u"Sugerence ignored successfully", 0, 0)],
	[('M', u"Idiocy archived at /dev/null", 0, 0)],
	[('M', u"Oh my God!", 0, 0)],
	[('M', u"Do, what you want be what you are, you are the lady of my heart!", 0, 0)],
	[('M', u"You can win if you want, if you want it you will win!", 0, 0)],
	[('M', u"Oh, me quede con la boca abierta, como Roberto!", 0, 0)],
	[('M', u"Be a man!", 0, 0)],
	[('A', u"Write a paper with your sugerence, later smoke it.", 0, 0)],
	[('A', u'pisses your sugerence', 0, 0)],
]

coffee=[
	[('M', u"No thanks", 0, 0)],
	[('M', u"A milk, please!", 0, 0)],
	[('M', u"Yes, please", 0, 0)],
]

cigarrette=[
	[('M', u"No thanks, I don't smoke", 0, 0)],
	[('M', u"It's a bad day to stop smoking", 0, 0)],
	[('M', u"Gimme 2", 0, 0)],
	[('M', u"Venga!", 0, 0)],
]

joint=[
	[('M', u"I don't want to say that.", 0, 0)],
	[('M', u"Stop!", 0, 0)],
	[('A', u"imposses this song: Rick Astley - Never Gonna Give You Up", 0, 0)],
	[('M', u"Uff, I'm too lazy >:D", 0, 0)],
]

beer=[
	[('M', u"No.", 0, 0)],
	[('M', u"Don't tell me are you blind to see?", 0, 0)],
	[('M', u"We're no strangers to love!", 0, 0)],
	[('M', u"I will oxidize if I don't take some beer", 0, 0)],
	[('M', u"Take it.", 0, 0)],
]

gorgeous=[
	[('M', u"thanks", 0, 0)],
	[('M', u"i'm beautiful", 0, 0)],
	[('M', u"more than you, i know", 0, 0)],
]

sexy=[
	[('M', u"thanks", 0, 0)],
	[('M', u"^_^", 0, 0)],
	[('M', u"oh yeah baby !", 0, 0)],
]

clever=[
	[('M', u"you don't", 0, 0)],
	[('M', u"yo yo", 0, 0)],
	[('M', u"thanks", 0, 0)],
	[('A', u"reverences you", 0, 0)],
]

thanks=[
		[("M", "No problem.", 0, 0)],
		[("M", "You're welcome.", 0, 0)],
		[("M", "Not at all.", 0, 0)],
		[("M", "Don't mention it.", 0, 0)],
		[("M", "You're welcome.", 0, 0)]
]

unavcmd = [
	[("n", "are you sure you mean this?", 0, 0)],
	[("n", "unknown command", 0, 0)],
	[('n', "unavailable command", 0, 0)]
]
