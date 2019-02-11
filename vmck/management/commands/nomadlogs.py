from django.core.management.base import BaseCommand
from ... import nomad


class Command(BaseCommand):
    help = "Dumps the task logs from Nomad."

    def add_arguments(self, parser):
        parser.add_argument('job_id')
        parser.add_argument('type', nargs='?', default='both')

    def handle(self, job_id, type, *args, **options):
        def logs(t):
            return nomad.logs(job_id, t) or ''

        if type == 'both':
            print(f'=== STDOUT {job_id} ===')
            print(logs('stdout'))
            print(f'=== STDERR {job_id} ===')
            print(logs('stderr'))

        else:
            print(logs(type))
