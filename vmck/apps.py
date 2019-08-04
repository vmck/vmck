from django.apps import AppConfig

import signal


class VmckConfig(AppConfig):
    name = 'vmck'

    @staticmethod
    def signalHandler(signalNumber, frame):
        from .models import Job
        from .jobs import kill

        for job in Job.objects.all():
            kill(job)

    def ready(self):
        signal.signal(signal.SIGTERM, VmckConfig.signalHandler)
