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


def on_done(job):
    job.state = job.STATE_DONE
    sync_artifacts(job)
    job.save()


def poll(job):
    status = nomad.status(nomad_id(job))

    if status == 'complete':
        on_done(job)

    elif status == 'running':
        job.state = job.STATE_RUNNING
        done = nomad.cat(nomad_id(job), f'alloc/data/done', binary=True)
        if done is not None:
            on_done(job)
            kill(job)

    else:
        raise RuntimeError(f"Unknown status {status}")


def kill(job):
    nomad.kill(nomad_id(job))
