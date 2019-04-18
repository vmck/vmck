from django.core.management.base import BaseCommand
from ... import jobs
from ...backends import get_backend


class Command(BaseCommand):
    help = "Create a job."

    def handle(self, *args, **options):
        backend = get_backend()
        job = jobs.create(backend)
        print(job.id)
