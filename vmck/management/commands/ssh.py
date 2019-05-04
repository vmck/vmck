import os
import argparse
from django.core.management.base import BaseCommand
from django.conf import settings
from ... import models
from ... import jobs
from ...ssh import ssh_args


class Command(BaseCommand):
    help = "SSH into a job."

    def add_arguments(self, parser):
        parser.add_argument('job_id')
        parser.add_argument('argv', nargs=argparse.REMAINDER)

    def handle(self, job_id, *args, **options):
        job = models.Job.objects.get(id=job_id)
        remote = dict(jobs.poll(job), identity_file=settings.SSH_IDENTITY_FILE)
        argv = list(ssh_args(remote, args))
        print('+', *argv)
        os.execvp(argv[0], argv)
