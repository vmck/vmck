import sys
import argparse
import subprocess
from django.core.management.base import BaseCommand
from ... import models
from ... import jobs
from ...ssh import ssh_args, ssh_identity


class Command(BaseCommand):
    help = "SSH into a job."

    def add_arguments(self, parser):
        parser.add_argument('job_id')
        parser.add_argument('argv', nargs=argparse.REMAINDER)

    def handle(self, job_id, argv, *args, **options):
        job = models.Job.objects.get(id=job_id)
        with ssh_identity() as identity_file:
            remote = dict(jobs.poll(job), identity_file=identity_file)
            argv = list(ssh_args(remote, argv))
            print('+', *argv)
            sys.exit(subprocess.run(argv).returncode)
