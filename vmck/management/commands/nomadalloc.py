from django.core.management.base import BaseCommand
from ...models import Job
from ... import jobs
from ... import nomad


class Command(BaseCommand):
    help = "Prints the most recent Nomad allocation ID for a job."

    def add_arguments(self, parser):
        parser.add_argument("job_id")

    def handle(self, job_id, *args, **options):
        job = Job.objects.get(id=job_id)
        print(nomad.alloc(jobs.nomad_id(job))["ID"])
