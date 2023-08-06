import re
from datetime import datetime, timedelta
from django.db import models

def listvalue( fn ):
	def wrapper( cls, v ):
		if not type(v) == 'list':
			v = [v]
		return fn( cls, v )
	return wrapper

def singlevalue( fn ):
	def wrapper( cls, v ):
		if type(v) == 'list':
			v = v[0]
		return fn( cls, v )
	return wrapper
	
class SearchableQS( models.query.QuerySet ):
	
	def _apply( self, filter_name, value ):
		if hasattr( self, filter_name ):
			func = getattr( self, filter_name )
			return func( value )
		return self
		
	def search( self, **kwargs ):
		if kwargs:
			filter_name, value = kwargs.popitem()
			if isinstance( value, str ) or isinstance( value, unicode ):
				try:
					value = eval( value )
				except:
					pass
			if kwargs: #If we still have params left in the search dict, keep filtering.
				return self._apply( filter_name, value ).search( **kwargs )			
			return self._apply( filter_name, value )
		
		return self

class SearchableManager( models.Manager ):
	
	def __init__( self, klass, *args, **kwargs ):
		super(SearchableManager, self).__init__(*args, **kwargs)
		self.klass = klass
	
	def get_query_set( self ):
		return self.klass( self.model, using=self._db )
	
	def search( self, **kwargs ):
		return self.get_query_set().search( **kwargs )
	

class SearchablePerson( SearchableQS ):

	@singlevalue
	def max_age( self, v ):
		today = datetime.now()
		born = today - timedelta( v*365.25 )
		return self.filter( date_of_birth__gte=born )

	@singlevalue
	def min_age( self, v ):
		today = datetime.now()
		born = today - timedelta( v*365.25 )
		return self.filter( date_of_birth__lte=born )

	@listvalue
	def postcode_in( self, v ):
		return self.filter( postcode__in=v )

	@listvalue
	def gender_in( self, v ):
		return self.filter( sex__in=v )

	def exclude_blocked( self, v ):
		return self.exclude( blocked=True )	

	@singlevalue
	def name( self, v ):
		return self.filter( name__istartswith=v )
		
		