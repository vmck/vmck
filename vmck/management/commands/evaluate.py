from django.core.management.base import BaseCommand
from ... import jobs


class Command(BaseCommand):
    help = "Evaluate a subject."

    def add_arguments(self, parser):
        parser.add_argument('spec_url')

    def handle(self, spec_url, *args, **options):
        job_id = jobs.create(spec_url)
        print(job_id)
