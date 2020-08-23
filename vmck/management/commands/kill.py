from django.core.management.base import BaseCommand
from ...models import Job
from ... import jobs


class Command(BaseCommand):
    help = "Kills a job."

    def add_arguments(self, parser):
        parser.add_argument("job_id")

    def handle(self, job_id, *args, **options):
        job = Job.objects.get(id=job_id)
        jobs.kill(job)
