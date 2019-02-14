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


def sync_artifacts(job):
    job.artifact_set.all().delete()
    for name in ['stdout.txt', 'stderr.txt']:
        data = nomad.cat(nomad_id(job), f'alloc/data/{name}', binary=True)
        job.artifact_set.create(name=name, data=data)


def poll(job):
    status = nomad.status(nomad_id(job))

    if status == 'complete':
        job.state = job.STATE_DONE
        sync_artifacts(job)

    elif status == 'running':
        job.state = job.STATE_RUNNING

    else:
        raise RuntimeError(f"Unknown status {status}")

    job.save()


def kill(job):
    nomad.kill(nomad_id(job))
