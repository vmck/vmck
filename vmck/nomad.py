import requests
from django.conf import settings
from urllib.parse import urljoin

api = urljoin(settings.NOMAD_URL, 'v1')


def response(res):
    if 200 <= res.status_code < 300:
        return res.json()
    else:
        raise RuntimeError(f"Request failed: {res.text}")


def jobs():
    return response(requests.get(f'{api}/jobs'))
