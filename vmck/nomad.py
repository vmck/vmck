import requests
from django.conf import settings
from urllib.parse import urljoin

api = urljoin(settings.NOMAD_URL, 'v1')


def response(res, binary=False):
    if 200 <= res.status_code < 300:
        if res.headers.get('Content-Type') == 'application/json':
            return res.json()

        if not binary and res.encoding:
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


def status(job_id):
    return alloc(job_id)['ClientStatus']


def kill(job_id):
    response(requests.delete(f'{api}/job/{job_id}'))


def alloc(job_id):
    allocs = response(requests.get(f'{api}/job/{job_id}/allocations'))
    if not allocs:
        raise RuntimeError(f"No allocs found for job {job_id}")
    allocs.sort(key=lambda a: a['CreateTime'])
    return(allocs[-1])


def cat(job_id, path, binary=False):
    alloc_id = alloc(job_id)['ID']
    return response(requests.get(
        f'{api}/client/fs/cat/{alloc_id}',
        params={'path': path},
    ), binary)


def logs(job_id, type):
    alloc_id = alloc(job_id)['ID']
    return response(requests.get(
        f'{api}/client/fs/logs/{alloc_id}',
        params={
            'task': 'vm',
            'type': type,
            'plain': 'true',
        },
    ))
