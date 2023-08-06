#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def rajaaja(margin, len, merkki):
	def raja(i):
		if i > margin and i < len-margin:
			return merkki
		else:
			return ''
	return raja

def hyphenate(text, margin=1, skip_html=False):
	"""hyphenate_finnish(text, margin=1, skip_html=False)

	Hyphenates Finnish text with Unicode soft hyphens. (U+00AD) Mainly intended for server-
	side-hyphenation of web sites.
	
	Allows to set hyphenation-preventing character margins for words so that they won't
	break right at start or end. (For example, it'd be a bit silly - although certainly
	possible in Finnish language - to break a word like 'erikoinen' at 'e-rikoinen'.
	With default margin of 1, it breaks more stylistically pleasingly, 'eri-koinen'.)

	Hyphenated html tags break web sites, so there's the boolean argument skip_html.
	That enabled, it skips over all the words that are contained within "<" and ">" characters.
	"""
	
	# Uh, sorry, my comments are in Finnish. Well, I can hardly think anybody else than Finnish people reading this...
	
	kerake = "bcdfghjklmnpqrstvwxz"		# eli konsonantit.
	kerake = list( kerake + kerake.upper() )
	vokaali = "aeiouyäöå"
	vokaali = list( vokaali + vokaali.upper() )
	pitkat = ['yi', 'öi', 'äi', 'ui', 'oi', 'ai', 'äy', 'au', 'yö', 'öy', 'uo', 'ou', 'ie', 'ei', 'eu', 'iu', 'ey', 'iy', 'aa', 'ii', 'uu', 'ee', 'oo', 'yy', 'ää', 'öö']	# suomen pitkät vokaalit ja diftongit
	pitkat = pitkat + [a.upper() for a in pitkat] + [a[0].upper()+a[1] for a in pitkat] + [a[0]+a[1].upper() for a in pitkat]
	tavuydin = vokaali + pitkat
	tavuviiva = '\u00AD'
	valmis_teksti = []				# anteex et kommentit on niin *tun paskat ja koodi sekavaa
	
	ei_html_toistaiseksi = True
	
	# looppi, jossa siis sanaa edetään kirjain kerrallaan, ja sen mukaan, mitä vastaan tulee, yritetään päätellä tavurakenne
	
	
	for sana in text.split(' '):		# Homma toimii niin, että varmistuneita tavuja tungetaan
		
		if skip_html and ei_html_toistaiseksi and "<" in sana:
			ei_html_toistaiseksi = False
		
		if not ei_html_toistaiseksi:
			if ">" in sana:
				ei_html_toistaiseksi = True
			valmis_teksti.append(sana)
			continue
		
		raja = rajaaja(margin, len(sana), tavuviiva)
			
		tavutettu = ''							# tavutettu-muuttujaan
		buff = ''						# parhaillaan tavu jota kursitaan kasaan, on buffissa.
		rajatapaus = ''					# rajatapaus tarkoittaa kirjainta, josta ei etukäteen tiedä ...
												# miten tavuraja(i) menee. esim: ka-Na, kaN-nu
		for i, c in enumerate(sana):				# Alla esimerkkikommenteissa iso kirjain senhetkistä 
															# c-muuttujaa eli käsittelyssä olevaa merkkiä.
			if c in vokaali:						# Suluissa oleva taas on rajatapaus, joka jäi edelliseltä 
															# ...kierrokselta epäselväksi kummalle puolelle tavuviivaa kuuluu.
				if rajatapaus != '':				# ha(l)Oo, a(k)U. jooh, ei pitkää konsonanttia. -> tavuraja
					buff = raja(i-1) + rajatapaus+c
					rajatapaus = ''
				elif buff[-2:] in pitkat:			# hääYö, aaAah! kaksi edellistä muodostaa oman tavunsa. -> tavuraja
					tavutettu += buff
					buff = raja(i) + c
				elif buff[-1:] in vokaali:			# Jos edellinen on vokaali.
					if buff[-1:]+c in tavuydin:		# kiIski, nuOtta. edellinen ja nykynen muodostavat tavuytimen.
						buff += c
					else:							# ta-loA, loAnheitto. eivät muodosta tavuydintä. -> tavuraja
						tavutettu += buff
						buff = raja(i) + c
				else:								# Aamu, Ilta, kAmpa. kun edellä ei ole 1) epävarmuutta 2) vokaaleja.
					buff += c
			elif c in kerake:
				if rajatapaus != '':
					if c == rajatapaus and i < len(sana)-1:	# ka(n)Nu, huu(s)Si. kaksi samaa konsonanttia -> tavuraja
						tavutettu += rajatapaus				# Jännä tietysti et aivan sanan vikalle kirjaimelle tää ei päde.
						rajatapaus = ''
						buff = raja(i) + c
					else:							# ka(r)Kki, ku(l)Ttuuri, sa(r)Ka tavuydin on jo ohi, 
														# mutta lopussa onkin yllättävän paljon kamaa! 
						if tavutettu[-1:] in vokaali:	# esim. särk-kä vai sar-ka? ei tiedetä -> rajatapaus.
							tavutettu += rajatapaus
							rajatapaus = c
						else:						# ar(s)Ka? kaksi konsonanttia, nyt kyllä viimeistään tavuraja, huh huh
							tavutettu += rajatapaus
							rajatapaus = ''
							buff = raja(i) + c
				elif buff == tavuviiva or buff =='':	# Riku, Kronikka. Puhtaalta pöydältä.
					buff = raja(i-1) + c
				elif buff[-2:] in pitkat:		# ääLiö vai pääLlikkö? -> rajatapaus.
					tavutettu += buff
					buff = raja(i)
					rajatapaus = c
				elif buff[-1:] in tavuydin:		# kaMa, moKa vai kaMpa, mokKa? -> rajatapaus
					tavutettu += buff
					buff = raja(i)
					rajatapaus = c
				else:							# Mikäs tää olikaan ees?
					tavutettu += buff
					buff = raja(i)
					rajatapaus = c
			else:							# jos se ei ole vokaali tai konsonanntti, se on jokin välimerkki!
				if rajatapaus != '':		#	japaniN-matka
					tavutettu += rajatapaus+c
					rajatapaus = ''
					continue
				else:							# ??
					tavutettu += buff+c
					buff = raja(i)
					continue

		if buff != '' and buff != tavuviiva:
			tavutettu += buff + rajatapaus
		else:
			tavutettu += rajatapaus
		valmis_teksti.append( tavutettu )
	hyphenated = ' '.join(valmis_teksti)
	return hyphenated
	
if __name__ == "__main__":
	import sys
	try:
		margin=int(sys.argv[1])
		text = sys.argv[2:]
	except:
		margin = 1
		try:
			text=sys.argv[1:]
		except:
			print("Usage: hyphenate_finnish.py [margin] text... OR inside Python: from hyphenate_finnish import hyphenate; hyphenate(text, margin) ")
			sys.exit(2)
	text = ' '.join(text)
	hyp = hyphenate(text, margin=margin, skip_html=True)
	print(hyp)