from .base import BasePingCommand


class Command(BasePingCommand):
    args = '<url>'
    help = 'This utility forces the Facebook to clean the cache of a given URL'

    def handle(self, url, **options):
        self.do_ping(url, options.get('verbosity'), options.get('traceback'))

