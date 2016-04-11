import pytz
from tastypie.serializers import Serializer


class NMTKSerializer(Serializer):

    def format_datetime(self, data):
        '''
        Convert the datetime to UTC and return it in a format
        that matches the JavaScript Date.ToJSON output format.

        This allows the browser/Angular to auto-translate the 
        times properly into the users timezone.
        '''
        return time.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
