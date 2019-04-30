import os
from pathlib import Path
from .utils import is_true
from .base_settings import *

base_dir = Path(__file__).parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = is_true(os.environ.get('DEBUG'))
VM_DEBUG = DEBUG

_allowed_hosts = os.environ.get('ALLOWED_HOSTS', '')
if _allowed_hosts:
    ALLOWED_HOSTS = _allowed_hosts.split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(base_dir / 'data' / 'db.sqlite3'),
    }
}

CONSUL_URL = os.environ.get('CONSUL_URL', 'http://localhost:8500')
NOMAD_URL = os.environ.get('NOMAD_URL', 'http://localhost:4646')

VMCK_BACKEND = os.environ.get('BACKEND', 'qemu')

QEMU_IMAGE_URL = os.environ.get('QEMU_IMAGE_URL')
QEMU_IMAGE_USERNAME = os.environ.get('QEMU_IMAGE_USERNAME')
