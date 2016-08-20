from django.core.management.base import BaseCommand, CommandError
from NMTK_server import models
from optparse import make_option
import datetime
from NMTK_server import tasks
from django.conf import settings


class Command(BaseCommand):
    help = 'Go out to the NMTK servers and discover new tools, update configs.'

    def add_arguments(self, parser):

        # Named (optional) arguments
        parser.add_argument('-t', '--tool-name',
                            action='store',
                            dest='tool_name',
                            default=None,
                            help='Specify a single tool server ID to update.')

    def handle(self, *args, **options):
        '''
        A save of the toolserver model will trigger an update of the config
        for that toolserver.
        '''
        if not settings.NMTK_SERVER:
            raise CommandError('The NMTK Server is not currently enabled')
        qs = models.ToolServer.objects.all()
        if options['tool_name']:
            qs = qs.filter(name__iexact=options['tool_name'])
        for m in qs:
            self.stdout.write('Updating ToolServer record for %s' % m.name)
#            m.save()
            tasks.discover_tools.delay(m)
