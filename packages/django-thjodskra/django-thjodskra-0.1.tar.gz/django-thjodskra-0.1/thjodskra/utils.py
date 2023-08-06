#encoding: utf-8
from datetime import datetime

def l2d( d ):
	return datetime.strptime( d, '%d%m%Y' ) if d else None

def s2d( d ):
	return datetime.strptime( d, '%d%m%y' ) if d else None
	
property_map = [
	( 'einkenni', 			'type', 			 2, str ),	#Einkenni: FE - Einstaklingar, FF - Fyrirtæki
	( 'nafnnumer', 			'personal_id', 		 8, str ),	#Nafnnúmer
	( 'kennitala', 			'ssn', 				10, str ),	#Kennitala
	( 'fjolskyldunumer',	'family_id', 		10, str ),	#Fjölskyldunúmer
	( 'sort_code', 			'sort_code', 		31, str ),	#Röðunarsvæði fyrir nafn
	( 'logheimili', 		'domicile', 		12, str),	#Lögheimiliskóði
	( 'skip_1', 			'skip_1', 			 3, str ),	#Autt
	( 'kyn', 				'sex', 				 1, str ),	#Kyn
	( 'hjuskaparstada',		'marital_status',	 1, str ),	#Hjúskaparstaða
	( 'skip_2', 			'skip_2', 			 2, str ),	#Autt
	( 'bannmerking',		'blocked', 			 1, str ),	#Bannmerking
	( 'rikisfang', 			'nationality', 		 2, str ),	#Ríkisfang
	( 'faedingarstadur', 	'place_of_birth', 	 4, str ),	#Fæðingastaður
	( 'faedingardagur', 	'date_of_birth', 	 8, l2d ),	#Fæðingadagur
	( 'nafn', 				'name', 			31, str ),	#Nafn
	( 'kennitala_maka', 	'ssn_spouse', 		10, str ),	#Kennitala maka
	( 'logheimili_112', 	'domicile_112', 	12, str ),	#Lögheimiliskóði 1. Des s.l.
	( 'dags_hreyfing', 		'mod_date', 		 6, s2d ),	#Dagsetning hreyfingar
	( 'adsetur', 			'residence', 		12, str ),	#Aðsetur - lögheimiliskóði
	( 'logheimili_sidast',	'domicile_last', 	12, str ),	#Síðasta lögheimili á Íslandi
	( 'kennitala_umbods', 	'ssn_guardian', 	10, str ),	#Kennitala umboðsmanns
	( 'skip_3', 			'skip_3', 			13, str ),	#Autt
	( 'sokn', 				'parish', 			 3, str ),	#Sókn
	( 'postnumer', 			'postcode', 		 3, str ),	#Póstnúmer
	( 'heimilisfang_nf', 	'address', 			21, str ),	#Heimilisfang í nefnifalli
	( 'heimilisfang_thf', 	'address_thf', 		21, str ),	#Heimilisfang í þágufalli
	( 'skip_4', 			'skip_4', 			23, str ),	#Autt
	( 'afdrif',  			'status', 			 4, str ),	#Afdrif
	( 'dags_afdrif', 		'status_date', 		 6, s2d )	#Dagsetning afdrifa
]


'''
	Skýringar:
	
		Einkenni:
			FE - Einstaklingur
			FF - Fyrirtæki
			
		Kyn:
			1 - Karlmaður, 18 ára eða eldri
			2 - Kvenmaður, 18 ára eða eldri
			3 - Drengur, 17 ára eða yngri
			4 - Stúlka, 17 ára eða yngri
			
		Hjúskaparstaða:
			1 - Ógift
			3 - Gift eða staðfest samvist
			4 - Ekkill / Ekkja
			5 - Skilin að borð og sæng
			6 - Skilin að lögum
			7 - Hjón ekki í samvistum
			8 - Íslendingur í hjúskap með útlending
			9 - Hjúskaparstaða óupplýst
			0 - Íslendingur búsettur erlendis í hjúskap með útlendingi
			L - Íslendingur með lögheimili á Íslandi í hjúskap með óskráðum útlendingi
			
		Afdrif:
			AFMÐ - Afmáð 
			BRFD - Breytt kennitala og fæðingardagur  
			BRFL - Brottfelling (brottfluttur af landi, oftast útlendingar) 
			BRNF - Breytt nafn 
			BRNN - Breytt nafnnúmer 
			LÉST - látinn 
			Féla - Félagi slitið 
			Firm - félagi slitið; … 
			Fyri - afskráð; félagsslit ; félag lagt niður, hætt starfsemi; … 
			Hags - engin starfsemi; hætt; sameining; samruni; … 
			Hlut - félagsslit, samr; afskráð í hfskrá ; félagi skipt ; starfs.hætt;  
			Lögb - félagi slitið, þrotabú ; afmáð úr fi-skrá; þrotabú eiganda ;  
			LRHG - engin starfsemi; starfsemi hætt; fyrrv. eitthvað; ….. 
			SAMR - Samruni 
			SKIP - Skiptastjóri
			
'''
	
def parse_line_is( line ):
	out = {}
	for key, en, length, f in property_map:
		out[key] = f( line[:length].decode('iso-8859-1').encode('utf-8').strip() )
		line = line[length:]
	return out


def parse_line_en( line ):
	out = {}
	for isl, key, length, f in property_map:
		out[key] = f( line[:length].decode('iso-8859-1').encode('utf-8').strip() )
		line = line[length:]
	return out


