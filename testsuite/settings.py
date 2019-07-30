import os
from datetime import datetime
from vmck.utils import is_true, random_code
from vmck.base_settings import *  # noqa

SECRET_KEY = random_code(43)
DEBUG = is_true(os.environ.get('TESTING_DEBUG'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

CONSUL_URL = os.environ.get('TESTING_CONSUL_URL', 'http://localhost:8500')
NOMAD_URL = os.environ.get('TESTING_NOMAD_URL', 'http://localhost:4646')
NOMAD_JOB_PREFIX = f'testsuite-{random_code(8)}-'
NOMAD_DEPLOYMENT_NAME = f"test {datetime.now().strftime('%H:%M:%S')}"

BACKEND = os.environ.get('TESTING_BACKEND', 'docker')

_github_image = 'https://github.com/mgax/vmck-images/raw/master/bionic.qcow2'
QEMU_IMAGE_URL = os.environ.get('TESTING_QEMU_IMAGE_URL', _github_image)
