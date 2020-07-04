from django.conf import settings


def get_backend(backend=None):
    if not backend:
        backend = settings.VMCK_BACKEND

    if backend == 'qemu':
        from .qemu import QemuBackend
        return QemuBackend()

    if backend == 'docker':
        from .docker import DockerBackend
        return DockerBackend()

    if backend == 'raw_qemu':
        from .raw_qemu import RawQemuBackend
        return RawQemuBackend()

    raise KeyError(f"Unknown backend {backend}")
