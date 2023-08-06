from django.core.management.base import BaseCommand
from django_statsd.patches.utils import wrap


class WrappedCommand(BaseCommand):

    def handle(self):
        import pdb; pdb.set_trace()
        return wrap(BaseCommand.handle, 'management.command')


def patch():
    BaseCommand.handle = wrap(BaseCommand.handle, 'management.command')

