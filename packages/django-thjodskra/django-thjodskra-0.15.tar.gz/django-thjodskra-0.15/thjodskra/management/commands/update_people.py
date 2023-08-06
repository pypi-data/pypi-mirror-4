#encoding: utf-8
import sys
from django.core.management.base import BaseCommand, CommandError
from ...models import Person

class Command(BaseCommand):

    args = u'<filename>'
    help = u'Update people from þjóðskrá'

    def handle(self, *args, **options):

		fname = args[0]
		f = open( fname, 'r' )
		create_count = 0
		update_count = 0
		
		for l in f.readlines():
			p, created, info = Person.from_string( l )
			if created:
				p.save()
				create_count += 1
			else:
				p.update( info )
				p.save()
				update_count += 1
				
			sys.stdout.write( '\r Updated %7i people. Created %7i people.' % (update_count,create_count) )
			sys.stdout.flush()
		print '\nDone'