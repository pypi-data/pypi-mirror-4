#!/usr/bin/env python3
from hyphenate_finnish import hyphenate


def testaa(tavutus, oikea_vastaus, testinimi):
	if tavutus == oikea_vastaus:
		print (testinimi+" läpi!")
	else:
		print (testinimi+" fail!")
		print (tavutus)
		for i, c in enumerate(tavutus):
			try:
				if c != oikea_vastaus[i]:
					print(i, "was           ", tavutus[i-10:i+20])
					print(i, "should've been", oikea_vastaus[i-10:i+20])
					break
			except:
				print(i, "was           ", tavutus[i-10:i+20])
				print(i, "should've been", oikea_vastaus[i-10:i+20])
				break


teksti1 = '''
Japani-harrastaja!!
==================

Sinun on aika ottaa ensimmäiset askeleesi kohti japanin kielitaitoa. Järjestämäni kurssin tehtävänä on varmistaa, että ne eivät myöskään jää viimeisiksi. *Nihongo crash course* on japanilaisen populaarikulttuurin suurkuluttajille suunnattu tehokurssi. Tämä näkyy siinä, että materiaalina käytetään juuri sinun lempimangaasi, animeasi, doramaasi tai mitä tahansa mikä kiinnostaa juuri sinua henkilökohtaisesti. Keskitymme myös erityisesti jippoihin joilla japanin oppiminen jatkuu myös kurssin jälkeen – animen ja muun mukavan lomassa.
'''
teksti2 = '''
<p class="signature">
Tavataan kurssilla!<br/>
<span style="font-family: 'Give You Glory', cursive; font-size: 1.5em;">Pyry Kontio</span><br/>
kurssin opettaja<br/>
</p>
'''
teksti3 = '''
Tarkempaa tietoa kurssista
--------------------------

### Japanin tavukirjoitus heti alkuun
Kana-tavukirjoitusjärjestelmä on lukutaidon perusta, jota ilman japani on räpiköintiä. Japanilaiset oppivat kanat esikoulussa, joten niissä ei ole mitään niin vaikeaa, ettetkö sinäkin oppisi niitä helposti! Opiskelemme kanat pikavauhtia alta pois, jotta pääsemme etenemään itse kieleen vauhdilla.
'''

teksti_c1 = '''
Ja-pa-ni-har-ras-ta-ja!!
==================

Si-nun on ai-ka ot-taa en-sim-mäi-set as-ke-lee-si koh-ti ja-pa-nin kie-li-tai-to-a. Jär-jes-tä-mä-ni kurs-sin teh-tä-vä-nä on var-mis-taa, et-tä ne ei-vät myös-kään jää vii-mei-sik-si. *Ni-hon-go crash cour-se* on ja-pa-ni-lai-sen po-pu-laa-ri-kult-tuu-rin suur-ku-lut-ta-jil-le suun-nat-tu te-ho-kurs-si. Tä-mä nä-kyy sii-nä, et-tä ma-te-ri-aa-li-na käy-te-tään juu-ri si-nun lem-pi-man-gaa-si, a-ni-me-a-si, do-ra-maa-si tai mi-tä ta-han-sa mi-kä kiin-nos-taa juu-ri si-nu-a hen-ki-lö-koh-tai-ses-ti. Kes-ki-tym-me myös e-ri-tyi-ses-ti jip-poi-hin joil-la ja-pa-nin op-pi-mi-nen jat-kuu myös kurs-sin jäl-keen – a-ni-men ja muun mu-ka-van lo-mas-sa.
'''
teksti_c2='''
<p class="signature">
Ta-va-taan kurs-sil-la!<br/>
<span style="font-family: 'Give You Glory', cursive; font-size: 1.5em;">Py-ry Kon-ti-o</span><br/>
kurs-sin o-pet-ta-ja<br/>
</p>
'''
teksti_c3='''
Tar-kem-paa tie-to-a kurs-sis-ta
--------------------------

### Ja-pa-nin ta-vu-kir-joi-tus he-ti al-kuun
Ka-na-ta-vu-kir-joi-tus-jär-jes-tel-mä on lu-ku-tai-don pe-rus-ta, jo-ta il-man ja-pa-ni on rä-pi-köin-ti-ä. Ja-pa-ni-lai-set op-pi-vat ka-nat e-si-kou-lus-sa, jo-ten niis-sä ei o-le mi-tään niin vai-ke-aa, et-tet-kö si-nä-kin op-pi-si nii-tä hel-pos-ti! O-pis-ke-lem-me ka-nat pi-ka-vauh-ti-a al-ta pois, jot-ta pää-sem-me e-te-ne-mään it-se kie-leen vauh-dil-la.
'''
teksti_c5='''
<p class="sig-na-tu-re">
Ta-va-taan kurs-sil-la!<br/>
<span sty-le="font-fa-mi-ly: 'Gi-ve Y-ou Glo-ry', cur-si-ve; font-si-ze: 1.5em;">Py-ry Kon-ti-o</span><br/>
kurs-sin o-pet-ta-ja<br/>
</p>
'''
tavutus = hyphenate(teksti1, skip_html=True, margin=1, hyphen='-')
testaa(tavutus, teksti_c1, "Testi 1")
tavutus = hyphenate(teksti2, skip_html=True, margin=1, hyphen='-')
testaa(tavutus, teksti_c2, "Testi 2")
tavutus = hyphenate(teksti3, skip_html=True, margin=1, hyphen='-')
testaa(tavutus, teksti_c3, "Testi 3")
testaa(hyphenate('Murr'), "Murr", "Testi 4")
tavutus = hyphenate(teksti2, skip_html=False, margin=1, hyphen='-')
testaa(tavutus, teksti_c5	, "Testi 5")
tavutus = hyphenate("<p>testataanpa</p>", skip_html=True, margin=1, hyphen='-')
testaa(tavutus, "<p>testataanpa</p>"	, "Testi 6")
tavutus = hyphenate("<p>testataanpa tätä</p>", skip_html=True, margin=1, hyphen='-')
testaa(tavutus, "<p>tes-ta-taan-pa tä-tä</p>"	, "Testi 7")