import base64
import subprocess
from time import time, sleep

import pytest
from django.conf import settings  # noqa

from vmck.ssh import ssh_args, ssh_identity

pytestmark = [pytest.mark.django_db]


class JobApi:

    @classmethod
    def create(cls, client):
        job = cls(client)
        job.start()
        return job

    def __init__(self, client):
        self.client = client

    def start(self):
        credentials = base64.b64encode(b'test:test').decode('latin1')
        auth_resp = self.client.get('/v0/token',
                                    HTTP_AUTHORIZATION=f'Basic {credentials}').json()  # noqa: E501

        self.token = auth_resp['auth_token']
        resp = self.client.post('/v0/jobs',
                                HTTP_AUTHORIZATION=f'Bearer {self.token}',
                                content_type='application/json')

        self.id = resp.json()['id']
        self.url = f'/v0/jobs/{self.id}'

    def wait(self, timeout=900):
        t0 = time()

        while time() < t0 + timeout:
            data = self.client.get(
                self.url,
                HTTP_AUTHORIZATION=f'Bearer {self.token}',
            ).json()

            if data.get('ssh'):
                return data

            assert time() < t0 + timeout, f"Job {self.id} timeout"
            sleep(1)

    def destroy(self):
        return self.client.delete(
            self.url,
            HTTP_AUTHORIZATION=f'Bearer {self.token}',
        )


def ssh(remote, args):
    with ssh_identity() as identity_file:
        remote = dict(remote, identity_file=identity_file)
        cmd = list(ssh_args(remote, args))
        print('+', *cmd)
        return subprocess.check_output(cmd).decode('latin1')


def test_api_home(client):
    resp = client.get('/v0/').json()
    assert resp['version'] == '0.0.1'


def test_api_job_lifecycle(client, after_test):
    job = JobApi.create(client)
    after_test(job.destroy)

    job_state = job.wait()
    print(job_state)

    remote = dict(job_state['ssh'])
    out = ssh(remote, ['echo', 'hello', 'world'])
    assert out.strip() == 'hello world'
