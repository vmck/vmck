import os
from pathlib import Path
from .base_settings import *

def is_true(value):
    text = (value or '').lower().strip()
    return text in ['1', 'yes', 'true', 'on', 'enabled']

base_dir = Path(__file__).parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = is_true(os.environ.get('DEBUG'))

_allowed_hosts = os.environ.get('ALLOWED_HOSTS', '')
if _allowed_hosts:
    ALLOWED_HOSTS = _allowed_hosts.split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(base_dir / 'data' / 'db.sqlite3'),
    }
}

NOMAD_URL = os.environ.get('NOMAD_URL', 'http://localhost:4646')

QEMU_IMAGE_URL = os.environ.get('QEMU_IMAGE_URL')
QEMU_IMAGE_USERNAME = os.environ.get('QEMU_IMAGE_USERNAME')
