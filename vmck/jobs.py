from .models import Job
from . import nomad
from . import vms


def create():
    job = Job.objects.create()

    nomad.launch(
        nomad.job(
            id=f'vmck-{job.id}',
            name=f"vmck {job.id}",
            taskgroups=[vms.task_group()],
        ),
    )

    job.status = job.STATE_RUNNING
    job.save()

    return job
