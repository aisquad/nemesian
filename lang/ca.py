#!/usr/bin/env python
#-*- coding: utf-8 -*-
# Catalan translation strings
# --Pasqual@cawiki 2010.03.22 21:02:03
"""
	You'll can add the following templates:
	* $chan returns the current channel where the message was sent.
	* $me returns the bot's nickname.
	* $more returns the link to the help page on ca.wikipedia.org.
	* $nick returns the current nick who originated the event.
	* $owner returns the owner nickname.
	* $serv returns the server on the bot is connected.
"""

single_words={
	"and": "i",
}

errors={
	"Got an error.": "error desconegut",
	"unknown source": "fitxer font desconegut.",
	"are you sure you mean this?": u"segur que volies dir això?",
	"unknown command": "ordre desconeguda.",
	"unavailable command": u"ordre no vàlida.",
	"no such help.": "no hi ha ajuda disponible.",
	"%s has not url.": u"%s no té url assignada."
}

#aboutme.py
aboutme = {
	"$nick: what do you want?": "$nick, et puc ajudar?"
}

#botops.py
botops = {
	"I'm already in this channel": "Ja estic en eixe canal",
	"I'm not in this channel": "No estic en eixe canal",
}

#calc.py
calc ={
	"Calcute parameters. Use '(', ')', operators ('*', '/', '+', '-', '^' for power, ':' for modulo) and numbers, putting '=' at beginning of the line.":
		u"Calculadora. Empreu '(', ')', operadors ('*', '/', '+', '-', '^' per a la potència, ':' per al mòdul) i els nombres, afegiu '=' al principi de línia."
}
#help.py
help={
	"Wikilinks. It returns an url link from a wikilink. You can use [[X]] to redirect to a page or {{X}}"
	"to a template, it accepts lang/proj codes and some prefixes. More: $more":
		"Viquienllaços. Torna una url d'un enllaç. Podeu emprar [[X]] per a redirigir a una pàgina o {{X}}"
		"cap a una plantilla. Accepta codi de llengües i projectes, i alguns prefixos. Més: $more",
	"See %s": "Vegeu %s",
	"help link": "http://ca.wikipedia.org/wiki/Usuari:TronaBot/IRC/ordres_geni",
	"available commands: %s": "ordres disponibles: %s"
}

#memory.py
memory = {
	"$nick meant: %s": "$nick volia dir: %s"
}
#reload.py
reload = {
	"module %s not found": u"no s'ha trobat el mòdul %s.",
	"module name expected": "s'esperava un nom de fitxer.",
	"unknown module": u"mòdul desconegut.",
	"reloaded %s langs in %.4f ms": u"s'ha recarregat els mòduls %s en %.4f ms.",
	'%r (version: %s)': u"%r (versió: %s).",
}

#tests.py
tests={
	u"$nick wanted to say: %s": u"$nick volia dir: %s",
	u"I've join %s at %s (%s ago)": u"M'he unit a %s el %s (fa %s)"
}

#users.py
users={
	"I'm not in this channel.": "No estic en eixe canal.",
	"Show users of a given channel. Syntax: .users #channel": u"Mostra els usuaris d'un canal determinat. Sintaxi: .[users|opers|voiced] #canal",
	"There is no opers in this channel.": "No hi ha cap operador en este canal.",
	"There is no voiced users in this channel.": "No hi ha cap moderador en este canal.",
	"There is no users in this channel.": "No hi ha usuaris en este canal.",
}

#sitematrix.py
sitematrix={
#1
u"Afar": "afar",
"Abkhazian": "abkhaz",
"Afrikaans": u"afrikaans",
"Akan": u"akan",
"Alemannic": "baix alemany",
"Amharik": "", #needed
"Aragonese": u"aragonés",
"Anglo-Saxon": u"anglosaxó",
"Arabic": u"àrab",
#10
"Assyrian Neo-Aramaic": "", #needed
"Egyptian Arabic": u"àrab egipci",
"Assammese": "",
"Asturian": u"asturià",
"Avar": "avar",
"Aymara": "aimara",
"Azeri": u"azerí",
"Bashkir": "baixkir",
"Bavarian": u"bavar", #verify
"Samogitian": "", #needed
#20
"Central Bicolano": "bikol central", #verify
"Belarusian": u"bielorús",
"Belarusian (Tarashkevitsa)": u"bielorús antic",
"Bulgarian": u"búlgar",
"Bihari": "bihari", #verify
"Bislama": u"bislama",
"Bambara": "", #needed
"Bengali": u"bengalí",
"Tibetan": "tibetà",
"Bishnupriya Manipuri": "", #needed
#30
"Breton": u"bretó",
"Bosnian": "bosni",
"Buginese": "", #needed
"Buryat (Russia)": "buriat",
"Catalan": u"català",
"Zamboanga Chavacano": "chavacano de Zamboanga", #verify
"Min Dong": "", #needed
"Chechen": u"txetxè",
"Cebuano": "", #needed
"Chamorro": "chamorro",
#40
"cho":{"*": "choctaw"},
"Cherokee": "cherokee",
"Cheyenne": "cheyenne",
"closed-zh-tw": {},
"Corsican": u"cors",
"Cree": u"cree",
"Crimean Tatar": "tatar crimeà",
"Czech": "txec",
"Kashubian": "caixubi",
u"Old Church Slavonic": u"eslau eclesiàstic antic",
#50
"Chuvash": "txuvaix",
"Welsh": u"galès",
"cz": "", #--> cs
"Danish": u"danés",
"German": "alemany",
"Zazaki": "zazaki",
"dk": "", #--> da
"dsb": "", #needed {"en": "Lower Sorbian", "l": "Dolnoserbski"},
"Divehi": "divehi",
"Dzongkha": "dzongkha",
#60
"Ewe": "ewe",
"Greek": "grec",
"eml": {"en": "Emilian-Romagnol", "l": u"emigliàn e rumagnôl"},
"English": u"anglés",
"eo": "esperanto",
"epo": "", #--> eo
"Spanish": u"catellà",
"Estonian": "estoni",
"Basque": "basc",
"Extremaduran": "extremeny",
#70
"Persian": "persa",
"Fula": "fulde",
"Finnish": u"finés",
u"Võro": u"võro",
"Fijian": "na vosa vakaviti",
"Faroese": u"feroés",
"French": u"francés",
"Franco-Provençal/Arpitan": u"francoprovençal",
"Friulian": u"friulés",
"West Frisian": u"frisó occidental",
#80
"Irish": u"gaèlic irlandés",
"Gan": "gan",
"Scotish Gaelic": u"gaèlic escocés",
"Galician": "gallec",
"Gilaki": "guilaki",
"Guarani": u"guaraní",
"Gothic": u"gòtic",
"Gujarati": "gujurati",
"Manx": u"gaèlic manx",
"Hausa": "hausa",
#90
"Hakka": "",
"Hawaiian": u"hawaià",
"Hebrew": "hebreu",
"Hindi": u"hindi",
"Fiji Hindi": "hindi de Fiji",
"Hiri Motu": u"hiri motu",
"Croatian": "croata",
"Upper Sorbian": "",
"Haitian": u"crioll haitià",
"Hungarian": u"hongarés",
#100
"Armenian": "armeni",
"Herero": "herero",
"Interlingua": "interlingua",
"Indonesian": "indonesi",
"interlingue": "interlingue",
"Igbo": "igbo",
"Sichuan Yi": "", #needed
"Inupiak": u"iñupiak",
"Ilokano": "ilokano",
"Ido": "ido",
#110
"Icelandic": u"islandés",
"Italian": u"italià",
"Inuktitut": "inuktitut",
"Japanese": u"japonés",
"Lojban": "lojban",
"jp": "", # --> ja
"Javanese": u"javanés",
"Georgian": u"georgià",
"Karakalpak": "karakalpak",
"Kabyle": "", #needed
#120
"kongo": "", #needed
"Kikuyu": "", #needed
"Kuanyama": "", #needed
"Kazakh": "kazakh",
"Greenlandic": u"groenlandés",
"Khmer": "khmer",
"Kannada": "", #needed
"Korean": u"coreà",
"kanuri": "Kanuri", #verify
"Kashmiri": "kaixmir", #verify
#130
"Ripuarian": "", #needed
"Kurdish": "kurd",
"Komi": "", #needed
"Cornish": u"còrnic",
"Kirghiz": "kirguiz",
"Latin": u"llatí",
"Ladino": "ladino",
"Luxemgourgish": u"luxemburgués",
"Lak": "", #needed
"Luganda": "luganda",
#140
"Limburgian": u"limburgués",
"Ligur": "ligur",
"Lombard": "llombard",
"Lingala": "lingala",
"Lao": u"laosià",
"Lithuanian": u"lituà",
"Latvian": u"letó",
"Banyumasan": "", #needed
"Moksha": "", #needed
"Magalasy": "malgaix",
#150
"Marshallese": "", #needed
"Maori": "maori",
"minnan": "", #--> zh-min-nan
"Macedonian": "macedoni",
"Malayalam": "malaialam",
"Mongolian": "mongol",
"Moldovian": "moldau", #--> ro
"mr": u"maratí",
"ms": u"malai",
"mt": u"maltès",
#160
"mus": u"muscogee",
"my": u"birmà",
"na": u"fica",
"nah": u"nahuatl",
"nap": u"napilità",
"nds": u"baix saxó",
"nds-nl": u"baix saxó",
"ne": u"nepalés",
"ng": u"oshiwambo",
"nl": u"nederlandès",
#170
"nn": u"noruec nynorsk",
"no": u"noruec bokmål",
"nov": u"novial",
"nrm": u"normand",
"nv": u"navaho",
"ny": u"chichewa",
"oc": u"occità",
"om": u"oromo",
"or": u"oriya",
"os": u"osset",
#180
"pa": u"panjabi",
"pam": u"pampango",
"pap": u"papiamentu",
"pdc": u"alemany pennsilvànià",
"pi": u"pali",
"pih": u"norfuk / pitkern",
"pl": u"polonès",
"pms": u"piemontès",
"ps": u"paixto",
"pt": u"portuguès",
#190
"qu": u"quítxua",
"rm": u"romanche",
"rmy": u"romaní",
"rn": u"rundi",
"ro": u"romanès",
"roa-rup": u"aromanès",
"ru": u"ruso",
"rw": u"ruanda",
"sa": u"sánscrito",
"sc": u"sardo",
#200
"scn": u"siciliano",
"sco": u"escocés",
"sd": u"sindhi",
"se": u"sami",
"sg": u"sango",
"sh": u"serbocroata",
"si": u"singalés",
"simple": u"Simple English",
"sk": u"eslovac",
"sl": u"esloveè",
#210
"sm": u"samoano",
"sn": u"shona",
"so": u"somalí",
"sq": u"albanés",
"sr": u"serb",
"ss": u"swati",
"st": u"sotho",
"su": u"sunda",
"sv": u"suec",
"sw": u"swahili",
#220
"ta": u"tàmil",
"te": u"tegulú",
"tet": u"tetun",
"tg": u"tayiko",
"th": u"tailandés",
"ti": u"tigrinya",
"tk": u"turcman",
"tl": u"tagalog",
"tlh": u"",
"tn": u"twana",
"to": u"tongalès",
#230
"tokipona": u"toki pona",
"tpi": u"tok pisin",
"tr": u"turc",
"ts": u"tonga",
"tt": u"tàtar",
"tum": u"tumbuka",
"tw": u"twi",
"ty": u"tahità",
"udm": u"udmurt",
"ug": u"uigur",
#240
"uk": u"ucraïnès",
"ur": u"urdú",
"uz": u"uzbeko",
"ve": u"venda",
"vec": u"venciano",
"vi": u"vietnamita",
"vls": u"flamenc occidental",
"vo": u"volapük",
"wa": u"walon",
"war": u"waray",
#250
"wo": u"wollof",
"xal": u"calmuc",
"xh": u"xhosa",
"yi": u"yídis",
"yo": u"yoruba",
"za": u"Zuangh",
"zh": u"xinès",
"zh-min-nan": u"min del sur",
"zh-yue": u"cantonès",
"zu": u"zulú",
}
