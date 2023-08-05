from optparse import OptionParser, make_option
from django.conf import settings
from django.core.management.base import BaseCommand
from callback import CallbackException, callback_manager
from callback.models import CallbackMap


class Command(BaseCommand):
    help = 'Process all pending callbacks'

    option_list = BaseCommand.option_list  + (
        make_option(
            '--fail-silently',
            dest='fail_silently',
            action='store_true',
            help='If callback fails, do not raise the exception',
        ),
    )

    def handle(self, *args, **kwargs):
        fail_silently = kwargs.get('fail_silently', False)
        for callback in CallbackMap.objects.all_live_callbacks():
            try:
                callback_manager.process_callback(callback)
            except CallbackException:
                if not fail_silently:
                    raise
                pass
