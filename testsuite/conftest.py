import os
import pytest
from vmck.utils import is_true


@pytest.fixture
def vm_backend():
    if os.environ.get('TESTING_BACKEND') == 'qemu':
        from vmck.vms import QemuBackend
        return QemuBackend()

    from mock_backend import MockBackend
    return MockBackend()
