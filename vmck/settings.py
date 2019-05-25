import os
import sentry_sdk
from .utils import is_true
from .base_settings import *
from sentry_sdk.integrations.django import DjangoIntegration

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = is_true(os.environ.get('DEBUG'))

_hostname = os.environ.get('HOSTNAME')
if _hostname:
    ALLOWED_HOSTS = [_hostname]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(base_dir / 'data' / 'db.sqlite3'),
    }
}

CONSUL_URL = os.environ.get('CONSUL_URL', 'http://localhost:8500')
NOMAD_URL = os.environ.get('NOMAD_URL', 'http://localhost:4646')

VMCK_BACKEND = os.environ.get('BACKEND', 'docker')
QEMU_IMAGE_URL = os.environ.get('QEMU_IMAGE_URL')

_ssh_username = SSH_USERNAME
SSH_USERNAME = os.environ.get('SSH_USERNAME', _ssh_username)

sentry_sdk.init(
    dsn="https://cfc9c776b9834e078b54b96f6826a0f6@sentry.io/1467831",
    integrations=[DjangoIntegration()]
)
