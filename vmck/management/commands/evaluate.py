from django.core.management.base import BaseCommand
from ... import nomad


class Command(BaseCommand):
    help = "Evaluate a subject."

    def add_arguments(self, parser):
        parser.add_argument('spec')
        parser.add_argument('package')

    def handle(self, spec, package, *args, **options):
        job_id = nomad.create_job(artifacts=[
            (spec, 'alloc/'),
            (package, 'alloc/'),
        ])
