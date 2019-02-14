from django.core.management.base import BaseCommand
from ... import jobs


class Command(BaseCommand):
    help = "Evaluate a subject."

    def handle(self, *args, **options):
        job_id = jobs.create()
        print(job_id)
