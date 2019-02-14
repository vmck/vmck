from django.core.management.base import BaseCommand
from ... import jobs


class Command(BaseCommand):
    help = "Evaluate a subject."

    def handle(self, *args, **options):
        job = jobs.create()
        print(job.id)
