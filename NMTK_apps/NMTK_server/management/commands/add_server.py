from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import datetime
from NMTK_server import tasks
from django.conf import settings
import json
from django.core.urlresolvers import reverse


class Command(BaseCommand):
    help = 'Add a new tool server for use by the NMTK API.'

    def add_arguments(self, parser):

        parser.add_argument('server_name', nargs=1)
        # Named (optional) arguments
        parser.add_argument(
            '-i',
            '--ip-restrict',
            action='store',
            dest='ip',
            default=None,
            help='Provide the remote IP for the tool.')

        parser.add_argument(
            '-u',
            '--url',
            action='store',
            dest='url',
            default=None,
            help='Provide the base URL for the tool server.')
        parser.add_argument(
            '-U',
            '--username',
            action='store',
            dest='username',
            default=None,
            help='Provide the username for the user that is adding the server.')
        parser.add_argument(
            '-c',
            '--contact',
            action='store',
            dest='contact',
            default=None,
            help='Provide the contact for the user that is managing the tool server.')
        parser.add_argument(
            '--skip-email',
            action='store_true',
            dest='skip_email',
            default=False,
            help="Skip sending the notification email for the newly added tool server")
        parser.add_argument(
            '--self-signed-ssl',
            action='store_true',
            dest='self_signed_ssl',
            default=False,
            help='Indicates that the tool server being added uses a self-signed ssl certificate.')

    def handle(self, *args, **options):
        if not settings.NMTK_SERVER:
            raise CommandError('The NMTK Server is not currently enabled')
        if not options['url']:
            raise CommandError(
                'Please provide the --url option and a server URL')
        if not options['username']:
            raise CommandError(
                'Please provide the --username option and a username')
#        try:
#            user=User.objects.get(username=options['username'])
#        except Exception, e:
#            raise CommandError('Username specified (%s) not found!' %
#                               options['username'])
        task = tasks.add_toolserver.delay(name=options['server_name'][0],
                                          url=options['url'],
                                          remote_ip=options['ip'],
                                          username=options['username'],
                                          contact=options['contact'],
                                          skip_email=options['skip_email'],
                                          verify_ssl=not options['self_signed_ssl'])
        m = task.get()
        print m.json_config()
#         if settings.SSL:
#             ssl = 's'
#         else:
#             ssl = ''
#         print json.dumps({
#             'tool_id': str(m.pk),
#             'url': 'http{0}://{1}{2}{3}'.format(ssl,
#                                                 settings.SITE_DOMAIN,
#                                                 settings.PORT,
#                                                 reverse('nmtk_server_nmtk_index')),
#             'verify_ssl': not settings.SELF_SIGNED_SSL_CERT,
#             'shared_secret': m.auth_token
#         })
#         print "Tool information has been saved with an tool id (public key) of %s" % (m.pk,)
#         print "Tool has a auth_key (private key) of '%s' (not including the surrounding single quotes.)" % (m.auth_token,)
# print "Please provide the tool id and auth_key to the maintainers of %s"
# % (m.name,)
