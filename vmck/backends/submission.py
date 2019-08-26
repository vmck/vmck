class Submission:

    def task_group(self, job, options):
        submission_task = {
            'name': 'submission-handler',
            'driver': 'docker',
            'config': {
                'image': 'vmck/vagrant-vmck:submission',
            },
            'env': {
                'DOWNLOAD_URL': options['archive'],
                'VMCK_URL': 'http://10.42.1.1:10000',
            },
            'resources': {
                'MemoryMB': options['memory'],
                'CPU': options['cpu_mhz'],
            },
        }

        return {
            'Name': 'handler',
            'Tasks': [
                submission_task,
            ],
            'RestartPolicy': {
                'Attempts': 0,
            },
        }
