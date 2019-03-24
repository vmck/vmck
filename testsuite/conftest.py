import os
import pytest
from vmck.utils import is_true


@pytest.fixture
def vm_backend():
    if is_true(os.environ.get('TESTING_MOCK_VM')):
        from mock_backend import MockBackend
        return MockBackend()

    else:
        from vmck import vms
        return vms.QemuBackend()
