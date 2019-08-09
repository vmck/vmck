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


def create(backend, options):
    job = Job.objects.create()
    job.state = job.STATE_RUNNING
    job.name = options['name']

    nomad.launch(
        nomad.job(
            id=nomad_id(job),
            name=f"{settings.NOMAD_DEPLOYMENT_NAME}#{job.id} {job.name}",
            taskgroups=[backend.task_group(job, options)],
        ),
    )

    job.save()

    return job


def on_done(job):
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
            health = nomad.health(job.id)
            if health:
                check = health[0]
                if check['Status'] == 'passing':
                    ssh_remote = {
                        'host': check['Output'].split(':')[0].split()[-1],
                        'port': int(check['Output'].split(':')[1]),
                        'username': settings.SSH_USERNAME,
                    }
                    return ssh_remote

    elif status in ['complete', 'failed']:
        on_done(job)

    else:
        raise RuntimeError(f"Unknown status {status!r}")


def kill(job):
    nomad.kill(nomad_id(job))
