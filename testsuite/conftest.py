import pytest


@pytest.fixture
def after_test(request):
    def callback(func, *args, **kwargs):
        request.addfinalizer(lambda: func(*args, **kwargs))
    return callback
