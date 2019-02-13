import random
from pathlib import Path
from django.conf import settings

control_path = (Path(__file__).parent.parent / 'control').resolve()


def random_port(start=10000, end=20000):
    return random.SystemRandom().randint(start, end - 1)


def task_group(spec_url):
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

    control_task = {
        'name': 'control',
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
            'DEBUG': 'yes' if settings.DEBUG else '',
            'VM_HOST': '${attr.unique.network.ip-address}',
            'VM_PORT': f'{vm_port}',
            'VM_USERNAME': settings.QEMU_IMAGE_USERNAME,
            'VM_PASSWORD': settings.QEMU_IMAGE_PASSWORD,
            'SPEC_URL': spec_url,
        },
    }

    return {
        'name': 'evaluation',
        'tasks': [
            vm_task,
            control_task,
        ],
    }
