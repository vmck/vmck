from urllib.parse import urljoin

from django.conf import settings
import requests

from vmck.nomad import response

consul_api = urljoin(settings.CONSUL_URL, 'v1')


def health(job_id):
    service = f'vmck-{job_id}-ssh'
    return response(requests.get(f'{consul_api}/health/checks/{service}'))


def service(job_id, service_id):
    service = f'vmck-{job_id}-ssh'
    url = f'{consul_api}/catalog/service/{service}?ServiceID={service_id}'
    return response(requests.get(url))
