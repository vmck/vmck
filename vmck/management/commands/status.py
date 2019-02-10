from django.core.management.base import BaseCommand
from ... import nomad


class Command(BaseCommand):
    help = "Reports VMCK status."

    def handle(self, *args, **options):
        print(nomad.jobs())
