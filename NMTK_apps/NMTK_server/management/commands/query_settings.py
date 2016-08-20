from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from django.conf import settings
from django.core.urlresolvers import reverse


class Command(BaseCommand):
    help = 'List the database type.'

    def add_arguments(self, parser):

        # Named (optional) arguments
        parser.add_argument('-t', '--type',
                            action='store_true',
                            dest='type',
                            default=False,
                            help='Print the database type.')
        parser.add_argument('-d', '--database',
                            action='store_true',
                            dest='database',
                            default=False,
                            help='Provide the name of the database.')
        parser.add_argument('-u', '--username',
                            action='store_true',
                            dest='username',
                            default=False,
                            help='Provide the name of the database user.')
        parser.add_argument('--self-signed-cert',
                            action='store_true',
                            dest='self_signed_cert',
                            default=False,
                            help='Return a 1 if the server is using a self signed certificate, 0 otherwise..')
        parser.add_argument('--nmtk-server-status',
                            action='store_true',
                            dest='nmtk_server_status',
                            default=False,
                            help='Return a 1 if the NMTK Server is enabled, 0 otherwise..')
        parser.add_argument('--tool-server-status',
                            action='store_true',
                            dest='tool_server_status',
                            default=False,
                            help='Return a 1 if the Tool Server is enabled, 0 otherwise..')
        parser.add_argument('--production',
                            action='store_true',
                            dest='production',
                            default=False,
                            help='Return a 1 if the NMTK server is in production (minified UI).')
        parser.add_argument('--tool-server-url',
                            action='store_true',
                            dest='tool_server_url',
                            default=False,
                            help='Return the URL for the Tool server.')
        parser.add_argument('--ssl',
                            action='store_true',
                            dest='ssl',
                            default=False,
                            help='Return the server SSL setting.')

    def handle(self, *args, **options):
        if options['type']:
            print getattr(settings, 'DATABASE_TYPE')
        elif options['database']:
            print settings.DATABASES['default']['NAME']
        elif options['username']:
            print settings.DATABASES['default']['USER']
        elif options['self_signed_cert']:
            if getattr(settings, 'SELF_SIGNED_SSL_CERT', 1):
                print 1
            else:
                print 0
        elif options['nmtk_server_status']:
            if settings.NMTK_SERVER:
                print 1
            else:
                print 0
        elif options['tool_server_status']:
            if settings.TOOL_SERVER:
                print 1
            else:
                print 0
        elif options['production']:
            if settings.PRODUCTION:
                print 1
            else:
                print 0
        elif options['ssl']:
            if settings.SSL:
                print 1
            else:
                print 0
        elif options['tool_server_url']:
            if getattr(settings, 'SSL', True):
                ssl = 's'
            else:
                ssl = ''
            print 'http{0}://{1}{2}{3}'.format(ssl,
                                               settings.SITE_DOMAIN,
                                               getattr(settings, 'PORT', ''),
                                               reverse('tool_index'))
