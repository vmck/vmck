import random
from pathlib import Path
from django.conf import settings

control_path = (Path(__file__).parent / 'control').resolve()
second = 1000000000


def random_port(start=10000, end=20000):
    return random.SystemRandom().randint(start, end - 1)


def control_task(vm_port):
    return {
        'name': 'control',
        'leader': True,
        'driver': 'docker',
        'config': {
            'image': 'python:3.7',
            'args': ['python', '/control/control.py'],
            'volumes': [
                f'{control_path}:/control',
            ],
        },
        'env': {
            'PYTHONUNBUFFERED': 'yes',
            'DEBUG': 'yes' if settings.VM_DEBUG else '',
            'VM_HOST': '${attr.unique.network.ip-address}',
            'VM_PORT': f'{vm_port}',
            'VM_USERNAME': settings.QEMU_IMAGE_USERNAME,
        },
    }


def resources(vm_port):
    network = {
        'ReservedPorts': [
            {'Label': 'ssh', 'Value': vm_port},
        ],
    }
    return {'Networks': [network]}


def services(job):
    name = f'vmck-{job.id}-ssh'

    return [
        {
            'Name': name,
            'PortLabel': 'ssh',
            'Checks': [
                {
                    'Name': f'{name} alive on ssh',
                    'InitialStatus': 'critical',
                    'Type': 'tcp',
                    'Interval': 1 * second,
                    'Timeout':  1 * second,
                },
            ],
        },
    ]


def task_group(job):
    vm_port = random_port()

    image_artifact = {
        'getterSource': settings.QEMU_IMAGE_URL,
        'relativeDest': 'local/',
        'options': {
            'archive': 'false',
        },
    }

    image_filename = settings.QEMU_IMAGE_URL.split('/')[-1]

    qemu_args = [
        '-netdev', (
            'user'
            ',id=user'
            ',net=192.168.1.0/24'
            ',hostname=vmck'
            ',hostfwd=tcp:${attr.unique.network.ip-address}:' f'{vm_port}-:22'
        ),
        '-device', (
            'virtio-net-pci'
            ',netdev=user'
            ',romfile='
        ),
        '-fsdev', 'local,id=vmck,security_model=none,path=../alloc/data',
        '-device', 'virtio-9p-pci,fsdev=vmck,mount_tag=vmck',
    ]

    vm_task = {
        'name': 'vm',
        'driver': 'qemu',
        'artifacts': [
            image_artifact,
        ],
        'config': {
            'image_path': f'local/{image_filename}',
            'accelerator': 'kvm',
            'args': qemu_args,
        },
        'resources': resources(vm_port),
        'services': services(job),
    }

    return {
        'name': 'test',
        'tasks': [
            vm_task,
            control_task(vm_port),
        ],
        'RestartPolicy': {
            'Attempts': 0,
        },
    }


class QemuBackend:

    def task_group(self, job):
        return task_group(job)
