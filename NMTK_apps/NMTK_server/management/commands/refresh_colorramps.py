from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from NMTK_server import tasks

from django.conf import settings
import logging
import sys
root_logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)


class Command(BaseCommand):
    help = 'Populate the color ramp images.'

    def handle(self, *args, **options):
        print "Populating the color ramp images..."
        result = tasks.refresh_colorramps.delay()
        task_output = result.get(timeout=600)
        print "Regenerated images for {0} Map Color Styles".format(task_output)
