from time import time, sleep
import pytest
from vmck import jobs

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def after_test(request):
    def callback(func, *args, **kwargs):
        request.addfinalizer(lambda: func(*args, **kwargs))
    return callback


def wait_for_job(job, timeout=120):
    t0 = time()

    while time() < t0 + timeout:
        jobs.poll(job)

        if job.state == job.STATE_DONE:
            break

        assert time() < t0 + timeout, f"Job {job!r} timeout"
        sleep(1)


def test_run_job(after_test):
    job = jobs.create()
    after_test(jobs.kill, job)
    wait_for_job(job)
    stdout = job.artifact_set.get(name='stdout.txt').data.decode('latin1')
    assert 'hello agent' in stdout
