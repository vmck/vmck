from .models import Job
from . import nomad
from . import vms


def nomad_id(job):
    return f'vmck-{job.id}'


def create():
    job = Job.objects.create()

    nomad.launch(
        nomad.job(
            id=nomad_id(job),
            name=f"vmck {job.id}",
            taskgroups=[vms.task_group()],
        ),
    )

    job.state = job.STATE_RUNNING
    job.save()

    return job


def poll(job):
    status = nomad.status(nomad_id(job))

    if status == 'complete':
        job.state = job.STATE_DONE

    elif status == 'running':
        job.state = job.STATE_RUNNING

    else:
        raise RuntimeError(f"Unknown status {status}")

    job.save()


def kill(job):
    nomad.kill(nomad_id(job))
