from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from NMTK_server import tasks
from optparse import make_option


class Command(BaseCommand):
    help = '''Remove unreferenced files (if they exist)'''
    option_list = BaseCommand.option_list + (

        make_option(
            '--really',
            action='store_true',
            dest='really',
            default=False,
            help='Actually delete the files (default is a dry run, just print the files to be removed'),
    )

    def handle(self, *args, **options):
        if not settings.NMTK_SERVER:
            raise CommandError('The NMTK Server is not currently enabled')

        result = tasks.cleanup.delay(dryrun=not options['really'])
        print "Peforming file cleanup (please wait....)"
        task_output = result.get(timeout=600)
        for line in task_output:
            print line
