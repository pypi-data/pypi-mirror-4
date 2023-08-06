from optparse import make_option

from django.core.management import BaseCommand

class Command(BaseCommand):
    help = "Updates permissions from the current models on disk."
    option_list = BaseCommand.option_list + (
        make_option('--noinput', action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'),
    )
    
    def handle(self, *args, **kwargs):
        from django.contrib.auth.management import create_permissions
        from django.db.models import get_apps
        for app in get_apps():
            create_permissions(app, None, 2)