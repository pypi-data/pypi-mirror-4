#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def hyphenate(text, margin=1):
	"""hyphenate_finnish(text, margin=1)

	Hypenates finnish text with Unicode soft hyphens. (U+00AD)
	Allows to set margins for words so that they won't break right at start or end.
	For example, it'd be a bit silly to break a word like 'erikoinen' at 'e-rikoinen'.
	With default margin of 1, it breaks like 'eri-koinen'.
	"""
	kerake = "bcdfghjklmnpqrstvwxz"			# eli konsonantit.
	kerake = list( kerake + kerake.upper() )
	vokaali = "aeiouyäöå"
	vokaali = list( vokaali + vokaali.upper() )
	pitkat = ['yi', 'öi', 'äi', 'ui', 'oi', 'ai', 'äy', 'au', 'yö', 'öy', 'uo', 'ou', 'ie', 'ei', 'eu', 'iu', 'ey', 'iy', 'aa', 'ii', 'uu', 'ee', 'oo', 'yy', 'ää', 'öö']	# suomen pitkät vokaalit ja diftongit
	pitkat = pitkat + [a.upper() for a in pitkat] + [a[0].upper()+a[1] for a in pitkat] + [a[0]+a[1].upper() for a in pitkat]
	tavuydin = vokaali + pitkat
	tavuviiva = '\u00AD'
	valmis_teksti = []				# anteex et kommentit on niin *tun paskat ja koodi sekavaa
	
	# looppi, jossa siis sanaa edetään kirjain kerrallaan, ja sen mukaan, mitä vastaan tulee, yritetään päätellä tavurakenne
	
	for sana in text.split(' '):			# homma toimii niin, että varmistuneita tavuja tungetaan
		tavutettu = ''						# tavutettu-muuttujaan
		buff = ''					# parhaillaan tavu jota kursitaan kasaan, on buffissa.
		rajatapaus = ''		# rajatapaus tarkoittaa kirjainta, josta ei etukäteen tiedä,
											# miten tavuraja menee. esim: ka-Na, kaN-nu
		raja = ''			# muuttuja raja sisältää tavuviivamerkin, joka tungetaan aina buffin alkuun, siis tavujen väliin.
		for i, c in enumerate(sana):				# Tarkoitan btw. alla kommenteissa isolla kirjaimella kulloistakin 
													# c:tä eli käsittelyssä olevaa merkkiä.
			if c in vokaali:								# ja suluissa olevalla rajatapausta, joka jäi edelliseltä 
															# kierrokselta päättämättä kummalle puolelle tavuviivaa kuuluu.
				if rajatapaus != '':				# ha(l)Oo, a(k)U. jooh, ei pitkää konsonanttia. -> tavuraja
					buff = raja + rajatapaus+c
					rajatapaus = ''
				elif buff[-2:] in pitkat:			# hääYö, aaAah! kaksi edellistä muodostaa oman tavunsa. -> tavuraja
					tavutettu += buff
					raja = tavuviiva
					buff = raja + c
				elif buff[-1:] in vokaali:			# Jos edellinen on vokaali.
					if buff[-1:]+c in tavuydin:		# kiIski, nuOtta. edellinen ja nykynen muodostavat tavuytimen.
						buff += c
					else:							# ta-loA, loAnheitto. eivät muodosta tavuydintä. -> tavuraja
						tavutettu += buff
						raja = tavuviiva
						buff = raja + c
				else:								# Aamu, Ilta, kAmpa. kun edellä ei ole 1) epävarmuutta 2) vokaaleja.
					buff += c
			elif c in kerake:
				if rajatapaus != '':
					if c == rajatapaus and i < len(sana)-1:	# ka(n)Nu, huu(s)Si. kaksi peräkkäistä samaa konsonanttia -> tavuraja
						tavutettu += rajatapaus					# Jännä tietysti et aivan sanan vikalle kirjaimelle tää ei päde.
						rajatapaus = ''
						buff = raja + c
					else:							# ka(r)Kki, ku(l)Ttuuri, sa(r)Ka tavuydin on jo ohi, ja tavu on heitetty jo
													# tavutettujen pinoon, mutta lopussa onkin yllättävän paljon kamaa! 
						if tavutettu[-1:] in vokaali:	# esim. särk-kä vai sar-ka? ei tiedetä -> rajatapaus.
							tavutettu += rajatapaus
							rajatapaus = c
						else:						# ar(s)Ka? kaksi konsonanttia, nyt kyllä viimeistään tavuraja, huh huh
							tavutettu += rajatapaus
							raja = tavuviiva
							rajatapaus = ''
							buff = raja+ c
				elif buff == tavuviiva or buff =='':	# Riku, Kronikka. Aloitetaan puhtaalta pöydältä.
					buff = raja+ c
				elif buff[-2:] in pitkat:		# ääLiö vai pääLlikkö? -> rajatapaus.
					tavutettu += buff
					raja = tavuviiva
					buff = raja
					rajatapaus = c
				elif buff[-1:] in tavuydin:		# kaMa, moKa vai kaMpa, mokKa? -> rajatapaus
					tavutettu += buff
					raja = tavuviiva
					buff = raja
					rajatapaus = c
				else:							# Mikäs tää olikaan ees?
					tavutettu += buff
					buff = raja
					rajatapaus = c
			else:							# jos se ei ole vokaali tai konsonanntti, se on jokin välimerkki!
				if rajatapaus != '':		#	japaniN-matka
					tavutettu += rajatapaus+c
					rajatapaus = ''
					raja = ''
					continue
				else:							# ??
					tavutettu += buff+c
					buff = raja
					raja = ''
					continue
			# Tässä on ideana ehkäistä rajojen piirto jos ollaan lähellä sanojen reunoja
			if i > margin and i < len(sana)-margin:
				raja = tavuviiva
			else:
				raja = ''
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
		text=' '.join(sys.argv[2:])
	except:
		print("Usage: hyphenate_finnish.py [margin] text... OR inside Python: from hyphenate_finnish import hyphenate; hyphenate(text, margin) ")
		sys.exit(2)
	hyp = hyphenate(text, margin=margin)
	print(hyp)