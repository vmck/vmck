from time import time, sleep
import pytest

pytestmark = [pytest.mark.django_db]


class JobApi:

    @classmethod
    def create(cls, client, sources):
        job = cls(client)
        job.start()
        return job

    def __init__(self, client):
        self.client = client

    def start(self):
        self.id = client.post('/v0/jobs').json()['id']
        self.url = f'/v0/jobs/{self.id}'

    def wait(self, timeout=900):
        t0 = time()

        while time() < t0 + timeout:
            data = self.client.get(self.url).json()

            if data['state'] == 'done':
                break

            assert time() < t0 + timeout, f"Job {self.id} timeout"
            sleep(1)

    def destroy(self):
        return self.client.delete(self.url)

    def artifact(self, name):
        url = f'{self.url}/artifacts/{name}'
        return self.client.get(url).content


def test_api_home(client):
    resp = client.get('/v0/').json()
    assert resp['version'] == '0.0.1'


def test_api_job_lifecycle(client, after_test):
    job = JobApi.create(client)
    after_test(job.destroy)
    job.wait()
    assert 'hello agent' in job.artifact('stdout').decode('latin1')
