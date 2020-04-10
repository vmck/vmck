from django.core.management.base import BaseCommand
from vmck.wsgi import application
from vmck.settings import APP_THREAD_COUNT

from waitress import serve


class Command(BaseCommand):
    help = 'Start the app on port 8100'

    def handle(self, *args, **options):
        serve(application, port='8000', threads=APP_THREAD_COUNT)
