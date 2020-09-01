import random


def random_port(start=10000, end=20000):
    return random.SystemRandom().randint(start, end - 1)


def constraints():
    return [
        {
            "LTarget": "${meta.vmck_worker}",
            "RTarget": "",
            "Operand": "is_set",
        },
        {"LTarget": "${meta.acs_job}", "RTarget": "", "Operand": "is_set"},
    ]


def resources(vm_port, options):
    network = {
        "ReservedPorts": [{"Label": "ssh", "Value": vm_port}],
    }
    return {
        "Networks": [network],
        "MemoryMB": options["memory"],
        "CPU": options["cpu_mhz"],
    }
