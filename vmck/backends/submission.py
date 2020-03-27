from django.conf import settings


def task(job, options):
    job = {
        'name': 'submission-handler',
        'driver': 'docker',
        'config': {
            'image': f'vmck/vagrant-vmck:{options["manager"]["vagrant_tag"]}',
            'command': '/src/submission/launch.sh',
        },
        'env': {
            "VMCK_"+k.upper():v for k, v in options['env'].items(),
        },
        'resources': {
            'MemoryMB': options['manager']['memory'],
            'CPU': options['manager']['cpu_mhz'],
        },
    }

    job['env']['VMCK_URL'] = settings.VMCK_URL
    job['env']['VMCK_JOB_ID'] = str(job.id)

    return job
