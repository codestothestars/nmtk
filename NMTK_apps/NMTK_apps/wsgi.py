"""
WSGI config for NMTK_apps project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os
import time
import traceback
import signal
import sys
import djcelery
djcelery.setup_loader()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "NMTK_apps.settings")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
# Comment out the line below and uncomment the block below
# to debug wierd WSGI issues (like populate(): isn't re-entrant and
# whatnot..
application = get_wsgi_application()


# try:
#     application = get_wsgi_application()
#     print 'WSGI without exception'
# except Exception:
#     print 'handling WSGI exception'
# Error loading applications
#     if 'mod_wsgi' in sys.modules:
#         traceback.print_exc()
#         os.kill(os.getpid(), signal.SIGINT)
#         time.sleep(2.5)
