from django.core.management.base import BaseCommand
from ... import jobs
from ... import vms


class Command(BaseCommand):
    help = "Evaluates a subject."

    def handle(self, *args, **options):
        backend = vms.QemuBackend()
        job = jobs.create(backend)
        print(job.id)
