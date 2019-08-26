from . import qemu


class Submission:

    def task_group(self, job, options):
        submission_task = {
            'name': 'submission-handler',
            'driver': 'docker',
            'config': {
                'image': 'vmck/vagrant-vmck:submission',
            },
            'env': {
                'DOWNLOAD_URL': options['manager']['archive'],
                'VMCK_URL': 'http://10.42.1.1:10000',
            },
            'resources': {
                'MemoryMB': options['manager']['memory'],
                'CPU': options['manager']['cpu_mhz'],
            },
        }
        vm_task_group = qemu.task_group(job, options['vm'])
        vm_task = vm_task_group['tasks'][0]
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
