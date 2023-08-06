from django.core.management.base import BaseCommand, CommandError

from json import loads, dumps
from sys import exit

from ...utils import ping, PING_URL


__all__ = (
    'BasePingCommand',
)


class BasePingCommand(BaseCommand):
    """ Extend this Command to fit your needs.

    For example:

        from facebook_utils.management.commands import (
            BasePingCommand,
        )

        class Command(BasePingCommand):
            help = 'Ping some pages stored in database'

            def handle(self, **options):
                verbosity = options.get('verbosity')
                traceback = options.get('traceback')
                for page in Page.objects.all():
                    page_url = page.get_absolute_url()
                    self.do_ping(page_url, verbosity, traceback)

    """
    def do_ping(self, url, verbosity='1', traceback=False):
        verbosity = int(verbosity)

        if verbosity == 0:
            try:
                response = ping(url)
            except:
                exit(1)

        else:
            if verbosity >= 2:
                self.stdout.write('-> Request %s\n' % (PING_URL % url))

            try:
                response = ping(url)
            except Exception, e:
                if not traceback:
                    raise CommandError(e.message)
                raise
            else:
                if verbosity == 1:
                    response_message = 'ok'
                else:
                    response_message = dumps(
                        loads(response.content), indent=4, separators=(',', ': '))

            if verbosity >= 2:
                self.stdout.write('<- Response: %s\n' % response_message)
            else:
                self.stdout.write(response_message + '\n')
