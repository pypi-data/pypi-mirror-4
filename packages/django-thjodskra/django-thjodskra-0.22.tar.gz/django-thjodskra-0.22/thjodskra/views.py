from django.views.generic import View, ListView

from .models import Person

class PersonList( ListView ):	
	model = Person
	paginate_by = 25

	def get_context_data( self, *args, **kwargs ):
		ctx = super(PersonList, self).get_context_data(*args, **kwargs)
		query = self.request.GET.copy()
		query.pop( 'page', 0 )
		ctx['search_query'] = query.urlencode()
		return ctx
		
	def get_queryset( self, *args, **kwargs ):
		return Person.objects.search( **self.request.GET.dict() )