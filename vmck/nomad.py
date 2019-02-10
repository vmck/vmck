import requests
from django.conf import settings
from urllib.parse import urljoin

api = urljoin(settings.NOMAD_URL, 'v1')


def jobs():
    return requests.get(f'{api}/jobs').json()
