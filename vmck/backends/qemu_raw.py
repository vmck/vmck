import logging
from pathlib import Path

from django.conf import settings

from vmck.backends import socat
from vmck.backends import submission
from vmck.backends import qemu_utils


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
control_path = (Path(__file__).parent / "control").resolve()


def task_group(job, options):
    tasks = []
    vm_port = qemu_utils.random_port(
        settings.VM_PORT_RANGE_START, settings.VM_PORT_RANGE_STOP,
    )

    image_filename = options["image_path"].split("/")[-1]

    netdev = (
        "user"
        ",id=user"
        ",net=192.168.1.0/24"
        ",hostname=vmck"
        ",hostfwd=tcp:127.0.0.1:${NOMAD_PORT_ssh}-:22"
    )

    if options["restrict_network"]:
        netdev += ",restrict=on"

    qemu_args = [
        "-netdev",
        netdev,
        "-device",
        "virtio-net-pci,netdev=user,romfile=",
        "-smp",
        str(options["cpus"]),
        "-m",
        str(options["memory"]),
        "-snapshot",
        "-enable-kvm",
        "-nographic",
        f"/opt/volumes/vmck-images/{image_filename}",
    ]

    vm_task = {
        "name": "vm",
        "driver": "raw_exec",
        "config": {
            "command": "/usr/bin/qemu-system-x86_64",
            "args": qemu_args,
        },
        "resources": qemu_utils.resources(vm_port, options),
        "services": socat.services(job),
    }

    tasks.append(vm_task)
    tasks.append(socat.task(job))

    if options.get("manager", False):
        tasks.append(submission.task(job, options))

    return {
        "name": "test",
        "Constraints": qemu_utils.constraints(),
        "tasks": tasks,
        "RestartPolicy": {"Attempts": 0},
        "ReschedulePolicy": {"Attempts": 0, "Unlimited": False},
    }


class RawQemuBackend:
    name = "raw_qemu"

    def task_group(self, job, options):
        return task_group(job, options)
