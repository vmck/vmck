from urllib.parse import urljoin
from pathlib import Path

from django.conf import settings

from vmck.backends import submission
from vmck.backends import socat
from vmck.backends import qemu_utils


control_path = (Path(__file__).parent / "control").resolve()


def task_group(job, options):
    tasks = []
    vm_port = qemu_utils.random_port(
        settings.VM_PORT_RANGE_START, settings.VM_PORT_RANGE_STOP,
    )

    prefix = settings.QEMU_IMAGE_PATH_PREFIX.rstrip("/") + "/"
    image = urljoin(prefix, options["image_path"])

    assert image.startswith(prefix)

    image_artifact = {
        "getterSource": image,
        "relativeDest": "local/",
    }

    image_filename = options["image_path"].split("/")[-1]
    if image_filename.endswith(".tar.gz"):
        image_filename = image_filename[: -len(".tar.gz")]

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
        "-smp",
        str(options["cpus"]),
        "-netdev",
        netdev,
        "-device",
        ("virtio-net-pci" ",netdev=user" ",romfile="),
        "-fsdev",
        "local,id=vmck,security_model=none,path=../alloc/data",
        "-device",
        "virtio-9p-pci,fsdev=vmck,mount_tag=vmck",
    ]

    vm_task = {
        "name": "vm",
        "driver": "qemu",
        "port_map": {"ssh": "22"},
        "artifacts": [image_artifact],
        "config": {
            "image_path": f"local/{image_filename}",
            "accelerator": "kvm",
            "args": qemu_args,
        },
        "resources": qemu_utils.resources(vm_port, options),
        "services": services(job),
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


class QemuBackend:
    name = "qemu"

    def task_group(self, job, options):
        return task_group(job, options)


# Qemu driver does not allow script checks
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
                    "Type": "tcp",
                    "PortLabel": "ssh",
                    "Interval": 1 * 1000000000,
                    "Timeout": 1 * 1000000000,
                },
            ],
        },
    ]
