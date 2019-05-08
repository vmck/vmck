from .qemu import random_port, resources, services

class DockerBackend:

    def task_group(self, job):
        vm_port = random_port()

        docker_vm_task = {
            'name': 'vm',
            'driver': 'docker',
            'config': {
                'image': 'mgax/vmck-mock-vm',
                'port_map': [
                    {'ssh': 22},
                ],
            },
            'resources': resources(vm_port),
            'services': services(job),
        }

        return {
            'Name': 'test',
            'Tasks': [
                docker_vm_task,
            ],
            'RestartPolicy': {
                'Attempts': 0,
            },
        }
