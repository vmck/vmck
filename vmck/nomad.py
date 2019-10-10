import logging
import requests
from django.conf import settings
from urllib.parse import urljoin

log = logging.getLogger(__name__)
log.setLevel(settings.log_level)

api = urljoin(settings.NOMAD_URL, 'v1')
consul_api = urljoin(settings.CONSUL_URL, 'v1')


class NoAllocsFoundError(RuntimeError):
    pass


def response(res, binary=False):
    if 200 <= res.status_code < 300:
        if res.headers.get('Content-Type') == 'application/json':
            return res.json()

        if not binary and res.encoding:
            return res.text

        return res.content

    log.debug('HTTP response %r: %r', res, res.text)
    res.raise_for_status()


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
    try:
        response(requests.post(f'{api}/jobs', json=definition))
    except Exception as err:
        log.error('Failed to create nomad job: %s', err.response.text)
        raise


def status(job_id):
    try:
        return alloc(job_id)['ClientStatus']
    except NoAllocsFoundError:
        return None


def kill(job_id):
    response(requests.delete(f'{api}/job/{job_id}'))


def alloc(job_id):
    allocs = response(requests.get(f'{api}/job/{job_id}/allocations'))
    if not allocs:
        raise NoAllocsFoundError(f"No allocs found for job {job_id}")
    allocs.sort(key=lambda a: a['CreateTime'])
    return(allocs[-1])


def cat(job_id, path, binary=False):
    alloc_id = alloc(job_id)['ID']

    try:
        return response(requests.get(
            f'{api}/client/fs/cat/{alloc_id}',
            params={'path': path},
        ), binary)

    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 400:
            return None

        raise


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


def health(job_id):
    service = f'vmck-{job_id}-ssh'
    return response(requests.get(f'{consul_api}/health/checks/{service}'))
