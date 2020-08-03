import random
import logging
from pathlib import Path

from django.conf import settings

from vmck.backends import submission
from vmck.backends.socat import services


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
control_path = (Path(__file__).parent / 'control').resolve()


def random_port(start=10000, end=20000):
    return random.SystemRandom().randint(start, end - 1)


def constraints():
    return [
        {
            'LTarget': "${meta.vmck_worker}",
            'RTarget': "",
            'Operand': "is_set",
        },
    ]


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


def task_group(job, options):
    tasks = []
    vm_port = random_port(
        settings.VM_PORT_RANGE_START,
        settings.VM_PORT_RANGE_STOP,
    )

    image_filename = options['image_path'].split('/')[-1]

    netdev = (
        'user'
        ',id=user'
        ',net=192.168.1.0/24'
        ',hostname=vmck'
        ',hostfwd=tcp::${NOMAD_PORT_ssh}-:22'
    )

    if options['restrict_network']:
        netdev += ',restrict=on'

    qemu_args = [
        '-netdev', netdev,
        '-device', 'virtio-net-pci,netdev=user,romfile=',
        '-smp', str(options['cpus']),
        '-m', str(options['memory']),
        '-snapshot',
        '-enable-kvm',
        '-nographic',
        f'/opt/volumes/vmck-images/{image_filename}',
    ]

    vm_task = {
        'name': 'vm',
        'driver': 'raw_exec',
        'config': {
            'command': '/usr/bin/qemu-system-x86_64',
            'args': qemu_args,
        },
        'resources': resources(vm_port, options),
    }

    socat_task = {
        'name': 'socat',
        'driver': 'raw_exec',
        'config': {
            'command': '/usr/bin/socat',
            'args': [
                f'tcp-listen:{vm_port},bind=''${attr.unique.network.ip-address},reuseaddr,fork',  # noqa: E501
                f'tcp:127.0.0.1:{vm_port}',
            ]
        },
        'services': services(job),
    }

    tasks.append(vm_task)
    tasks.append(socat_task)

    if options.get('manager', False):
        tasks.append(submission.task(job, options))

    return {
        'name': 'test',
        'Constraints': constraints(),
        'tasks': tasks,
        'RestartPolicy': {
            'Attempts': 0,
        },
        'ReschedulePolicy': {
            'Attempts': 0,
            'Unlimited': False,
        },
    }


class RawQemuBackend:

    def task_group(self, job, options):
        a = task_group(job, options)
        log.debug(a)
        return a
