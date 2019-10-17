second = 1000000000


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
                    'Timeout': 1 * second,
                },
            ],
        },
    ]


def task(job):
    return {
        'name': 'socat',
        'driver': 'raw_exec',
        'config': {
            'command': '/usr/bin/socat',
            'args': [
                'tcp-listen:${NOMAD_PORT_vm_ssh},bind=${attr.unique.network.ip-address},reuseaddr,fork',  # noqa: E501
                'tcp:127.0.0.1:${NOMAD_PORT_vm_ssh}',
            ]
        },
        'services': services(job),
    }
