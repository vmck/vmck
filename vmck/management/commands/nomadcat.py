from django.core.management.base import BaseCommand
from ... import nomad


class Command(BaseCommand):
    help = "Dumps a file from Nomad."

    def add_arguments(self, parser):
        parser.add_argument('job_id')
        parser.add_argument('path')

    def handle(self, job_id, path, *args, **options):
        print(nomad.cat(job_id, path))
