from django.conf import settings


def task(job, options):
    job_task = {
        'name': 'submission-handler',
        'driver': 'docker',
        'config': {
            'image': f'vmck/vagrant-vmck:{options["manager"]["vagrant_tag"]}',
            'command': '/src/submission/launch.sh',
        },
        'env': options['env'],
        'resources': {
            'MemoryMB': options['manager']['memory_mb'],
            'CPU': options['manager']['cpu_mhz'],
        },
    }

    job_task['env']['VMCK_URL'] = settings.VMCK_URL
    job_task['env']['VMCK_JOB_ID'] = str(job.id)

    return job_task
