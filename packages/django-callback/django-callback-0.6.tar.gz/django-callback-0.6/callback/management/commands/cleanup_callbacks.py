from optparse import OptionParser, make_option
from django.conf import settings
from django.core.management.base import BaseCommand
from callback.models import CallbackMap


class Command(BaseCommand):
    help = 'Clean database of callback records.'

    option_list = BaseCommand.option_list  + (
        make_option(
            '-e',
            '--errors-delete',
            dest='errors_delete',
            action='store_true',
            default=False,
            help='Delete inactive callbacks that contain errors.',
        ),
        make_option(
            '-d',
            '--days',
            dest='days',
            type='int',
            help='How many days back worth of callbacks should be kept?',
        ),
    )

    def handle(self, *args, **kwargs):
        errors_delete = kwargs.get('errors_delete', False)
        days = kwargs.get('days', None)
        if days is None:
            days = getattr(settings, 'CALLBACK_KEEP_DAYS', 7)

        # Sanity checks
        if not isinstance(days, int):
            days = int(days)

        if not isinstance(errors_delete, bool):
            errors_delete = bool(errors_delete)

        CallbackMap.objects.all_expired_callbacks(days, errors_delete).delete()
