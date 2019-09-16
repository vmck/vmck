from django.conf import settings


def task(job, options):
    return {
        'name': 'submission-handler',
        'driver': 'docker',
        'config': {
            'image': f'vmck/vagrant-vmck:{options["env"]["vagrant_tag"]}',
            'command': '/src/submission/launch.sh',
        },
        'env': {
            'ARCHIVE_URL': options['env']['archive'],
            'SCRIPT_URL': options['env']['script'],
            'VMCK_URL': settings.VMCK_URL,
            'VMCK_CALLBACK_URL': options['env']['vmck_callback_url'],
            'VMCK_JOB_ID': str(job.id),
        },
        'resources': {
            'MemoryMB': options['env']['memory'],
            'CPU': options['env']['cpu_mhz'],
        },
    }
