from django.conf import settings


def get_backend():
    backend = settings.VMCK_BACKEND

    if backend == "qemu":
        from .qemu import QemuBackend

        return QemuBackend()

    if backend == "docker":
        from .docker import DockerBackend

        return DockerBackend()

    raise KeyError(f"Unknown backend {backend}")
