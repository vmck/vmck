from .qemu import random_port, control_task


class DockerBackend:
    def task_group(self):
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
            'resources': {
                'networks': [
                    {
                        'ReservedPorts': [
                            {'label': 'ssh', 'value': vm_port},
                        ],
                    },
                ],
            },
        }

        return {
            'Name': 'test',
            'Tasks': [
                docker_vm_task,
                control_task(vm_port),
            ],
            'RestartPolicy': {
                'Attempts': 0,
            },
        }
