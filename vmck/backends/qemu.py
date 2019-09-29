import random
from urllib.parse import urljoin
from pathlib import Path

from django.conf import settings

from vmck.backends import submission


control_path = (Path(__file__).parent / 'control').resolve()
second = 1000000000


def random_port(start=10000, end=20000):
    return random.SystemRandom().randint(start, end - 1)


def resources(vm_port, options):
    network = {
        'ReservedPorts': [
            {'Label': 'ssh', 'Value': vm_port},
        ],
    }
    return {
        'Networks': [network],
        'MemoryMB': options['memory'],
        'CPU': options['cpu_mhz'],
    }


def services(job):
    name = f'vmck-{job.id}-ssh'

    return [
        {
            'Name': name,
            'PortLabel': 'ssh',
            'Checks': [
                {
                    'Name': f'{name} tcp',
                    'InitialStatus': 'critical',
                    'Type': 'tcp',
                    'PortLabel': 'ssh',
                    'Interval': 1 * second,
                    'Timeout':  1 * second,
                },
            ],
        },
    ]


def task_group(job, options):
    tasks = []
    vm_port = random_port()

    prefix = settings.QEMU_IMAGE_PATH_PREFIX.rstrip('/') + '/'
    image = urljoin(prefix, options['image_path'])

    assert image.startswith(prefix)

    image_artifact = {
        'getterSource': image,
        'relativeDest': 'local/',
    }

    image_filename = options['image_path'].split('/')[-1]
    if image_filename.endswith('.tar.gz'):
        image_filename = image_filename[:-len('.tar.gz')]

    qemu_args = [
        '-smp', str(options['cpus']),
        '-netdev', (
            'user'
            ',id=user'
            ',net=192.168.1.0/24'
            ',hostname=vmck'
            ',hostfwd=tcp:${attr.unique.network.ip-address}:${NOMAD_PORT_ssh}-:22'  # noqa: E501
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
        'port_map': {
            'ssh': '22',
        },
        'artifacts': [
            image_artifact,
        ],
        'config': {
            'image_path': f'local/{image_filename}',
            'accelerator': 'kvm',
            'args': qemu_args,
        },
        'resources': resources(vm_port, options),
        'services': services(job),
    }
    tasks.append(vm_task)

    if options.get('manager', False):
        tasks.append(submission.task(job, options))

    return {
        'name': 'test',
        'tasks': tasks,
        'RestartPolicy': {
            'Attempts': 0,
        },
        'ReschedulePolicy': {
            'Attempts': 0,
            'Unlimited': False,
        },
    }


class QemuBackend:

    def task_group(self, job, options):
        return task_group(job, options)
