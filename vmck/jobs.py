import logging
from django.conf import settings
from .models import Job
from . import nomad

log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


def nomad_id(job):
    prefix = settings.NOMAD_JOB_PREFIX
    return f'{prefix}{job.id}'


def create(backend, sources=[]):
    job = Job.objects.create()
    for name, upload in sources:
        job.source_set.create(name=name, data=upload.data)
        upload.delete()

    nomad.launch(
        nomad.job(
            id=nomad_id(job),
            name=f"{settings.NOMAD_DEPLOYMENT_NAME} job #{job.id}",
            taskgroups=[backend.task_group(job)],
        ),
    )

    job.state = job.STATE_RUNNING
    job.save()

    return job


def sync_artifacts(job):
    job.artifact_set.all().delete()
    for name in ['stdout', 'stderr']:
        nomad_path = f'alloc/logs/control.{name}.0'
        data = nomad.cat(nomad_id(job), nomad_path, binary=True)
        job.artifact_set.create(name=name, data=data or b'')


def _dump_sources(job):
    # TODO this function is here to test the API that uploads job source files.
    # It should be removed once we can inject the sources into the VM.
    import json
    job.artifact_set.create(
        name='_sources',
        data=json.dumps({
            s.name: s.data.decode('latin1')
            for s in job.source_set.all()
        }).encode('utf8'),
    )


def on_done(job):
    sync_artifacts(job)
    _dump_sources(job)
    job.state = job.STATE_DONE
    job.save()


def poll(job):
    status = nomad.status(nomad_id(job))
    log.debug('%r status: %r', job, status)

    if status in [None, 'pending']:
        return

    elif status == 'running':
        job.state = job.STATE_RUNNING
        done = nomad.cat(nomad_id(job), f'alloc/data/done', binary=True)
        if done is not None:
            on_done(job)
            kill(job)

        else:
            return nomad.health(job.id)

    elif status in ['complete', 'failed']:
        on_done(job)

    else:
        raise RuntimeError(f"Unknown status {status!r}")


def kill(job):
    nomad.kill(nomad_id(job))
