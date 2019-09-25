import os
from datetime import datetime

from vmck.utils import is_true, random_code, hostname
from vmck.base_settings import *  # noqa

SECRET_KEY = os.environ.get('SECRET_KEY', 'changeme')

DEBUG = is_true(os.environ.get('TESTING_DEBUG'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

CONSUL_URL = os.environ.get('TESTING_CONSUL_URL', 'http://10.42.1.1:8500')
NOMAD_URL = os.environ.get('TESTING_NOMAD_URL', 'http://10.42.1.1:4646')
NOMAD_JOB_PREFIX = f'testsuite-{random_code(8)}-'
NOMAD_DEPLOYMENT_NAME = f"test-vmck@{hostname} {datetime.now().strftime('%H:%M:%S')}"  # noqa: E501

VMCK_BACKEND = os.environ.get('TESTING_BACKEND', 'qemu')

QEMU_IMAGE_PATH_PREFIX = os.environ.get('TESTING_QEMU_IMAGE_PATH_PREFIX', 'http://10.42.1.1:10001')  # noqa: E501
