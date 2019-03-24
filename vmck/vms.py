import random
from pathlib import Path
from django.conf import settings

control_path = (Path(__file__).parent.parent / 'control').resolve()


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


def task_group():
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
        'config': {
            'image_path': f'local/{image_filename}',
            'accelerator': 'kvm',
            'args': qemu_args,
        },
        'resources': {
            'network': {
                'reservedPorts': [{'label': 'ssh', 'value': vm_port}],
                # TODO 'dynamicPorts': [{'label': 'ssh', 'value': 0}],
            },
        },
        'artifacts': [
            image_artifact,
        ],
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
    def task_group(self):
        return task_group()
