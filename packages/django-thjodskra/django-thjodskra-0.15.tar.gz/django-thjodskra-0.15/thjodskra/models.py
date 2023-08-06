#encoding: utf-8

from django.db import models

from .utils import parse_line_en

SEX_CHOICES = (
	(1,'Karl'), 
	(2,'Kona'), 
	(3,'Drengur'), 
	(4,'Stúlka')
)

MARITAL_CHOICES = (
	('1','Ógift'),
	('3', 'Gift eða staðfest samvist'),
	('4', 'Ekkill / Ekkja'),
	('5', 'Skilin að borð og sæng'),
	('6', 'Skilin að lögum'),
	('7', 'Hjón ekki í samvistum'),
	('8', 'Íslendingur í hjúskap með útlending'),
	('9', 'Hjúskaparstaða óupplýst'),
	('0', 'Íslendingur búsettur erlendis í hjúskap með útlendingi'),
	('L', 'Íslendingur með lögheimili á Íslandi í hjúskap með óskráðum útlendingi')
)

class Person( models.Model ):
	"""docstring for Person"""

	name = models.CharField( max_length=31 )			#Nafn
	sort_code = models.CharField( max_length=31 )		#Röðunarsvæði fyrir nafn

	personal_id = models.CharField( max_length=8 )		#Nafnnúmer
	ssn = models.CharField( max_length=10 )				#Kennitala
	ssn_spouse = models.CharField( max_length=10 )		#Kennitala maka
	ssn_guardian = models.CharField( max_length=10 )	#Kennitala umboðsmanns
	family_id = models.CharField( max_length=10 )		#Fjölskyldunúmer

	sex = models.CharField( max_length=1, choices=SEX_CHOICES )	#Kyn
	marital_status = models.CharField( max_length=1, choices=MARITAL_CHOICES) #Hjúskaparstaða

	domicile = models.CharField( max_length=12 )		#Lögheimiliskóði
	domicile_112 = models.CharField( max_length=12 )	#Lögheimiliskóði 1. Des s.l.
	domicile_last = models.CharField( max_length=12 )	#Síðasta lögheimili á Íslandi
	residence = models.CharField( max_length=12 )		#Aðsetur - lögheimiliskóði
	address = models.CharField( max_length=21 )			#Heimilisfang í nefnifalli
	address_thf = models.CharField( max_length=21 )		#Heimilisfang í þágufalli
			
	postcode = models.CharField( max_length=3 )			#Póstnúmer
			
	nationality = models.CharField( max_length=2 )		#Ríkisfang
	place_of_birth = models.CharField( max_length=4 )	#Fæðingastaður
	date_of_birth = models.DateField( )					#Fæðingadagur

	status = models.CharField( max_length=4 )			#Afdrif
	status_date = models.DateField( blank=True, null=True ) #Dagsetning afdrifa
	
	parish = models.CharField( max_length=3)			#Sókn
	blocked = models.BooleanField( default=False )		#Bannmerking
	mod_date = models.DateField( blank=True, null=True ) #Dagsetning hreyfingar
	

	def __unicode__( self ):
		return u'%s (%s)'%(self.name, self.ssn)

	@classmethod
	def from_string( self, s, update=True ):
		"""Parses an individual person from a national registry row"""
		info = parse_line_en( s )
		created = False
		try:
			p = Person.objects.get( ssn=info['ssn'] )
		except Person.DoesNotExist:
			p = Person( )
			p.update( info )
			created = True

		return p, created, info
	
	def update( self, info ):
		for k, v in info.items():
			if hasattr( self, k ):
				setattr( self, k, v )
		
		
		
		