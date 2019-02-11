from time import time
from pathlib import Path
import requests
from django.conf import settings
from urllib.parse import urljoin

api = urljoin(settings.NOMAD_URL, 'v1')
factory_bin = str(Path(settings.FACTORY_HOME) / 'factory')


def response(res):
    if 200 <= res.status_code < 300:
        return res.json()
    else:
        raise RuntimeError(f"Request failed: {res.text}")


def jobs():
    return response(requests.get(f'{api}/jobs'))


def nomad_job(job_id):
    job_name = f'VMCK job {job_id}'
    argv = [factory_bin, 'run', 'echo', 'hello', 'world!']

    run_task = {
        'name': 'vm',
        'driver': 'raw_exec',
        'config': {
            'command': argv[0],
            'args': argv[1:],
        },
    }

    task_group = {
        'name': 'run',
        'tasks': [run_task],
    }

    return {
        'job': {
            'id': job_id,
            'name': job_name,
            'type': 'batch',
            'datacenters': ['dc1'],
            'taskgroups': [task_group],
        },
    }


def create_job():
    job_id = str(int(time()))
    print('Job ID:', job_id)
    job_spec = nomad_job(job_id)
    result = response(requests.post(f'{api}/jobs', json=job_spec))
    print(result)


def kill(job_id):
    result = response(requests.delete(f'{api}/job/{job_id}'))
    print(result)
