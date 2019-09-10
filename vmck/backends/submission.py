from . import qemu


class Submission:

    def task_group(self, job, options):
        submission_task = {
            'name': 'submission-handler',
            'driver': 'docker',
            'config': {
                'image': 'vmck/vagrant-vmck:submission',
                'force_pull': True,
            },
            'env': {
                'DOWNLOAD_ARCHIVE_URL': options['env']['archive'],
                'DOWNLOAD_SCRIPT_URL': options['env']['script'],
                'VMCK_URL': options['env']['vmck_api'],
                'INTERFACE_ADDRESS': options['env']['interface_address'],
                'VMCK_JOB_ID': str(job.id),
            },
            'resources': {
                'MemoryMB': options['env']['memory'],
                'CPU': options['env']['cpu_mhz'],
            },
        }
        vm_task = qemu.task_group(job, options)['tasks'][0]
        return {
            'Name': 'handler',
            'Tasks': [
                submission_task,
                vm_task,
            ],
            'RestartPolicy': {
                'Attempts': 0,
            },
        }
