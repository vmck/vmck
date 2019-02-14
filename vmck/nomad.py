import requests
from django.conf import settings
from urllib.parse import urljoin

api = urljoin(settings.NOMAD_URL, 'v1')


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


def job(id, name, taskgroups):
    return {
        'job': {
            'id': id,
            'name': name,
            'type': 'batch',
            'datacenters': ['dc1'],
            'taskgroups': taskgroups,
        },
    }


def launch(definition):
    response(requests.post(f'{api}/jobs', json=definition))


def kill(job_id):
    response(requests.delete(f'{api}/job/{job_id}'))


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
            'task': 'vm',
            'type': type,
            'plain': 'true',
        },
    ))
