#!/usr/bin/env python3
# -*- coding: utf-8 -*-

kerake = "bcdfghjklmnpqrstvwxz"
kerake = list( kerake + kerake.upper() )
vokaali = "aeiouyäöå"
vokaali = list( vokaali + vokaali.upper() )
# suomen pitkät vokaalit ja diftongit
pitkat = ['yi', 'öi', 'äi', 'ui', 'oi', 'ai', 'äy', 'au', 'yö', 'öy', 'uo', 'ou', 'ie',
 'ei', 'eu', 'iu', 'ey', 'iy', 'aa', 'ii', 'uu', 'ee', 'oo', 'yy', 'ää', 'öö']
pitkat = pitkat + [a.upper() for a in pitkat] + [a[0].upper()+a[1] for a in pitkat] + [a[0]+a[1].upper() for a in pitkat] # O(2^n) mut mitä välii ku maksimitapaus on n=2 :D

def syllables(sana):
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
	return tavut

def add_hyphens(tavut, sana, hyphen, margin):
	tavutettava = ''
	charcount = 0
	for tavu in tavut:
		tavutettava += tavu
		charcount += len(tavu)
		if charcount >= margin and charcount <= len(sana) - margin:
			tavutettava += hyphen
	return tavutettava

def hyp_paska(tavuttamaton_osa, margin=2, hyphen='\u00AD'):
	tavutettu = ''
	while len(tavuttamaton_osa) > 0:
		raja_asti = tavuttamaton_osa.find('[[[')
		if raja_asti != -1:
			tavutettava_osa = tavuttamaton_osa[:raja_asti]
			tavuttamaton_osa = tavuttamaton_osa[raja_asti+3:]
			tavutettu += hyp_html(tavutettava_osa, margin, hyphen)
		else:
			tavutettava_osa = tavuttamaton_osa
			tavuttamaton_osa = ''
			tavutettu += hyp_html(tavutettava_osa, margin, hyphen)
		raja_alkaen = tavuttamaton_osa.find(']]]')
		if raja_alkaen != -1:
			tavutettu += tavuttamaton_osa[:raja_alkaen]
			tavuttamaton_osa = tavuttamaton_osa[raja_alkaen+3:]
	return tavutettu

def hyp_html(tavuttamaton_osa, margin=2, hyphen='\u00AD'):
	tavutettu = ''
	while len(tavuttamaton_osa) > 0:
		raja_asti = tavuttamaton_osa.find('<')
		if raja_asti != -1:
			tavutettava_osa = tavuttamaton_osa[:raja_asti]
			tavuttamaton_osa = tavuttamaton_osa[raja_asti:]
			tavutettu += hyp_text(tavutettava_osa, margin, hyphen)
		else:
			tavutettava_osa = tavuttamaton_osa
			tavuttamaton_osa = ''
			tavutettu += hyp_text(tavutettava_osa, margin, hyphen)
		raja_alkaen = tavuttamaton_osa.find('>')
		if raja_alkaen != -1:
			tavutettu += tavuttamaton_osa[:raja_alkaen+1]
			tavuttamaton_osa = tavuttamaton_osa[raja_alkaen+1:]
	return tavutettu

def hyp_text(text, margin=2, hyphen='\u00AD'):
	valmis_teksti = []
	for rivi in text.split('\n'):
		valmis_rivi = []
		for sana in rivi.split(' '):
	
			tavut = syllables(sana)
			sana = add_hyphens(tavut, sana, hyphen, margin)

			valmis_rivi.append( sana )
			
		valmis_rivi = ' '.join(valmis_rivi)
		valmis_teksti.append(valmis_rivi)
	valmis_teksti = '\n'.join(valmis_teksti)
	return valmis_teksti
	

def hyphenate(text, margin=2, skip_html=False, hyphen='\u00AD', skip_brackets=False):
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
	
	if skip_brackets:
		return hyp_paska(text, margin, hyphen)
	elif skip_html:
		return hyp_html(text, margin, hyphen)
	else:
		return hyp_text(text, margin, hyphen)


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