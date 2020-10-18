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
    }
