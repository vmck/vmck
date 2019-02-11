from django.core.management.base import BaseCommand
from ... import nomad


class Command(BaseCommand):
    help = "Create a job."

    def handle(self, *args, **options):
        nomad.create_job()
