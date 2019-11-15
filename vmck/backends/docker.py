from .qemu import random_port, constraints, resources
from .socat import services
from .import submission


class DockerBackend:

    def task_group(self, job, options):
        vm_port = random_port()

        docker_vm_task = {
            'name': 'vm',
            'driver': 'docker',
            'config': {
                'image': 'vmck/mock:0.0.2',
                'port_map': [
                    {'ssh': 22},
                ],
            },
            'resources': resources(vm_port, options),
            'services': services(job),
        }

        tasks = [docker_vm_task]

        if options.get('manager', False):
            tasks.append(submission.task(job, options))

        return {
            'Name': 'test',
            'Constraints': constraints(),
            'Tasks': tasks,
            'RestartPolicy': {
                'Attempts': 0,
            },
        }
