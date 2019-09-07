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
                'DOWNLOAD_ARCHIVE_URL': options['manager']['archive'],
                'DOWNLOAD_SCRIPT_URL': options['manager']['script'],
                'VMCK_URL': options['manager']['vmck_api'],
                'INTERFACE_ADDRESS': options['manager']['interface_address'],
                'VMCK_JOB_ID': str(job.id),
            },
            'resources': {
                'MemoryMB': int(options['manager']['memory']),
                'CPU': int(options['manager']['cpu_mhz']),
            },
        }
        vm_task = qemu.task_group(job, options['vm'])['tasks'][0]
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
