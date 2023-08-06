#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def hyphenate(text, margin=2, skip_html=False, hyphen='\u00AD'):
	"""hyphenate_finnish(text, margin=2, skip_html=False, hyphen='\u00AD')

	Hyphenates Finnish text with Unicode soft hyphens. (U+00AD) Mainly intended for server-
	side-hyphenation of web sites.
	
	Allows to set hyphenation-preventing character margins for words so that they won't
	break right at start or end. (For example, it'd be a bit silly - although certainly
	possible in Finnish language - to break a word like 'erikoinen' at 'e-rikoinen'.
	With default margin of 2, it breaks more stylistically pleasingly, 'eri-koinen'.)

	Hyphenated html tags break web sites, so there's the boolean argument skip_html.
	That enabled, it skips over all the words that are contained within "<" and ">" characters.
	"""
	
	# Uh, sorry, my comments are in Finnish. Well, I can hardly think anybody else than Finnish people reading this...
	
	if margin < 1:
		margin = 1
	kerake = "bcdfghjklmnpqrstvwxz"
	kerake = list( kerake + kerake.upper() )
	vokaali = "aeiouyäöå"
	vokaali = list( vokaali + vokaali.upper() )
	pitkat = ['yi', 'öi', 'äi', 'ui', 'oi', 'ai', 'äy', 'au', 'yö', 'öy', 'uo', 'ou', 'ie', 'ei', 'eu', 'iu', 'ey', 'iy',
				'aa', 'ii', 'uu', 'ee', 'oo', 'yy', 'ää', 'öö']			# suomen pitkät vokaalit ja diftongit
	pitkat = pitkat + [a.upper() for a in pitkat] + [a[0].upper()+a[1] for a in pitkat] + [a[0]+a[1].upper() for a in pitkat]
	valmis_teksti = []
	skipataan = False
	
	for sana in text.split(' '):
		
		if skip_html:
			if not skipataan and "<" in sana:
				skipataan = True
		
			if skipataan:
				valmis_teksti.append(sana)
				if ">" in sana:
					skipataan = False
				continue
			
		tavut = []
		buff = ''					# parhaillaan tavu jota kursitaan kasaan, on buffissa.
		rajakerake = None	
		kerakecount = 0
		# rajakerake tarkoittaa konsonanttia, josta ei etukäteen tiedä miten tavuraja menee. esim: ka-Na, kaN-nu
		
		# Alla esimerkkikommenteissa ISO kirjain viittaa c-muuttujan arvoon eli loopissa käsittelyssä olevaan merkkiin.
		# Suluissa oleva taas on rajakerake, josta jäi edelliseltä kierrokselta epäselväksi kummalle puolelle tavuviivaa se kuuluu.
		
		for c in sana:
				
			if c in kerake:
				kerakecount += 1
			else:
				kerakecount = 0
			if kerakecount > 3:						# pakotettu tavuraja, että rivit tyyliin kkkkkkkkkk rivittyisivät myös
				tavut.append(buff+ (rajakerake if rajakerake else ''))
				buff = c
				rajakerake = None
				kerakecount = 1
				continue
				
			# Kirjain voi olla joko vokaali, konsonantti tai välimerkki.
			
			if c in vokaali:						
				if rajakerake:						# ha(l)Oo, a(k)U. jooh, eli rajakerake on tavun on alkukonsonantti. -> tavuraja
					tavut.append(buff)
					buff = rajakerake+c
					rajakerake = None
				elif buff[-2:] in pitkat:			# hääYö, aaAah! kaksi edellistä vokaalia muodostaa oman tavuytimensä. -> tavuraja
					tavut.append(buff)
					buff = c
				elif buff[-1:] in vokaali:
					if buff[-1:]+c in pitkat:		# kiIski, nuOtta. edellinen ja nykynen muodostavat yhdessä tavuytimen.
						buff += c
					else:							# ta-loA, loAnheitto. eivät muodosta tavuydintä. -> tavuraja
						tavut.append(buff)
						buff = c
				else:								# Aamu, Ilta, kAmpa. kun edellä ei ole 1) rajakonsonantteja 2) vokaaleja.
					buff += c
			
			elif c in kerake:		# Konsonantti
				if rajakerake:				# ka(n)Nu, huu(s)Si vai mu(r)R? ka(r)Kki, ku(l)Ttuuri, sa(r)Ka tavuydin on ohi mutta konsonantteja piisaa
											# esim. särK-kä vai sar-Ka? ar(s)Ka vai mur(s)K? ei tiedetä -> uusi rajakerake.
					buff += rajakerake
					rajakerake = c
				elif buff[-1:] in vokaali:		# ääLiö vai pääLlikkö? kaMa, moKa vai kaMpa, mokKa? -> rajakerake
					rajakerake = c
				else:
					buff += c					# sKruudata, Riku, Kronikka. konsonanttia toisensa perään, tai puhtaalta pöydältä.
					
			else:				# Välimerkki.
				if rajakerake:					# japani(n)-matka
					buff += rajakerake + c
					rajakerake = None
					# tavut.append(buff)	# Oikeasti tässä kulkee tavuraja, mutta välimerkki toimikoon tavumerkin asemasta.
					# buff = ''
				else:							# ukko-pekka, liu'un
					buff += c
					# tavut.append(buff)	# Oikeasti tässä kulkee tavuraja, mutta välimerkki toimikoon tavumerkin asemasta.
					# buff = ''
		if rajakerake:
			tavut.append( buff + rajakerake)
		else:
			tavut.append(buff)
		tavutettava = ''
		charcount = 0
		for tavu in tavut:
			tavutettava += tavu
			charcount += len(tavu)
			if charcount >= margin and charcount <= len(sana) - margin:
				tavutettava += hyphen
		valmis_teksti.append( tavutettava )
	valmis_teksti = ' '.join(valmis_teksti)
	return valmis_teksti
	
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
	text = hyphenate(text, margin=margin)
	print(text)