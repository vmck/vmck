second = 1000000000

check_script = """\
(
    set -x
    echo | nc $NOMAD_IP_ssh $NOMAD_PORT_ssh | grep -q 'SSH-'
) 2>&1
"""


def services(job):
    name = f"vmck-{job.id}-ssh"

    return [
        {
            "Name": name,
            "PortLabel": "ssh",
            "Checks": [
                {
                    "Name": f"{name} ssh",
                    "InitialStatus": "critical",
                    "Type": "script",
                    "Command": "/bin/sh",
                    "Args": ["-c", check_script],
                    "PortLabel": "ssh",
                    "Interval": 1 * second,
                    "Timeout": 1 * second,
                },
            ],
        },
    ]


def task(job):
    return {
        "name": "socat",
        "driver": "raw_exec",
        "config": {
            "command": "/usr/bin/socat",
            "args": [
                "tcp-listen:${NOMAD_PORT_vm_ssh},bind=${attr.unique.network.ip-address},reuseaddr,fork",  # noqa: E501
                "tcp:127.0.0.1:${NOMAD_PORT_vm_ssh}",
            ],
        },
        "services": services(job),
    }
