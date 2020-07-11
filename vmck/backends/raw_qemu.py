import random
from pathlib import Path

from django.conf import settings

from vmck.backends import submission


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
    if image_filename.endswith('.qcow2'):
        image_filename = image_filename[:-len('.qcow2')]

    netdev = (
        'user'
        ',id=user'
        ',net=192.168.1.0/24'
        ',hostname=vmck'
        ',hostfwd=tcp:127.0.0.1:${NOMAD_PORT_ssh}-:22'
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
        'port_map': {
            'ssh': '22',
        },
        'config': {
            'command': '/usr/bin/qemu-system-x86_64',
            'args': qemu_args,
        },
        'resources': resources(vm_port, options),
    }
    tasks.append(vm_task)
    # tasks.append(socat.task(job))

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
        return task_group(job, options)
