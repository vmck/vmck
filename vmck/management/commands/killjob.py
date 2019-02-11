from django.core.management.base import BaseCommand
from ... import nomad


class Command(BaseCommand):
    help = "Kills a job."

    def add_arguments(self, parser):
        parser.add_argument('job_id')

    def handle(self, job_id, *args, **options):
        nomad.kill(job_id)
