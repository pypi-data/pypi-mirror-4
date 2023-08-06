#encoding: utf-8
import sys
from django.core.management.base import BaseCommand, CommandError
from ...models import Person

class Command(BaseCommand):

    args = u'<filename>'
    help = u'Imports people from þjóðskrá'

    def handle(self, *args, **options):

		fname = args[0]
		f = open( fname, 'r' )
		count = 0
		for l in f.readlines():
			p, fresh = Person.from_string( l )
			if fresh:
				p.save()
				count += 1
			sys.stdout.write( '\r Saved %7i people' % count )
			sys.stdout.flush()
		print '\nDone'