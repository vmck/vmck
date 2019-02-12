from time import time
from pathlib import Path
import requests
from django.conf import settings
from urllib.parse import urljoin

api = urljoin(settings.NOMAD_URL, 'v1')
task_name = 'vm'


def response(res):
    if 200 <= res.status_code < 300:
        if res.headers.get('Content-Type') == 'application/json':
            return res.json()

        if res.encoding:
            return res.text

        return res.content

    raise RuntimeError(f"Request failed: {res.text}")


def jobs():
    return response(requests.get(f'{api}/jobs'))


def nomad_job(job_id, artifacts):
    job_name = f'VMCK job {job_id}'

    task_artifacts = []
    def add_artifact(source, destination):
        task_artifacts.append({
            'getterSource': source,
            'relativeDest': destination,
            'options': {
                'archive': 'false',
            },
        })

    add_artifact(settings.QEMU_IMAGE_URL, 'local/')
    image_filename = settings.QEMU_IMAGE_URL.split('/')[-1]

    for a in artifacts:
        add_artifact(*a)

    run_task = {
        'name': task_name,
        'driver': 'qemu',
        'config': {
            'image_path': f'local/{image_filename}',
            'accelerator': 'kvm',
            'args': [],
        },
        'artifacts': task_artifacts,
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


def create_job(artifacts=[]):
    job_id = str(int(time()))
    print('Job ID:', job_id)
    job_spec = nomad_job(job_id, artifacts)
    result = response(requests.post(f'{api}/jobs', json=job_spec))
    print(result)


def kill(job_id):
    result = response(requests.delete(f'{api}/job/{job_id}'))
    print(result)


def alloc(job_id):
    allocs = response(requests.get(f'{api}/job/{job_id}/allocations'))
    alloc_ids = [
        a['ID']
        for a in sorted(allocs, key=lambda a: a['CreateTime'])
    ]
    if not alloc_ids:
        raise RuntimeError(f"No allocs found for job {job_id}")
    return(alloc_ids[-1])


def cat(job_id, path):
    alloc_id = alloc(job_id)
    return response(requests.get(
        f'{api}/client/fs/cat/{alloc_id}',
        params={'path': path},
    ))


def logs(job_id, type):
    alloc_id = alloc(job_id)
    return response(requests.get(
        f'{api}/client/fs/logs/{alloc_id}',
        params={
            'task': task_name,
            'type': type,
            'plain': 'true',
        },
    ))
