import os
import sentry_sdk
from .utils import is_true
from .base_settings import *  # noqa
from .base_settings import QEMU_CPU_MHZ, SSH_USERNAME, base_dir
from sentry_sdk.integrations.django import DjangoIntegration

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = is_true(os.environ.get("DEBUG"))

_hostname = os.environ.get("HOSTNAME")
if _hostname:
    ALLOWED_HOSTS = [_hostname]

_postgres_db = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": os.getenv("POSTGRES_DB"),
    "USER": os.getenv("POSTGRES_USER"),
    "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
    "HOST": os.getenv("POSTGRES_ADDRESS"),
    "PORT": os.getenv("POSTGRES_PORT"),
}
_sqlite_db = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": str(base_dir / "data" / "db.sqlite3"),
}

default_db = _postgres_db if os.getenv("POSTGRES_DB") else _sqlite_db

DATABASES = {"default": default_db}

VMCK_URL = os.environ.get("VMCK_URL", "http://localhost:10000")
CONSUL_URL = os.environ.get("CONSUL_URL", "http://localhost:8500")
NOMAD_URL = os.environ.get("NOMAD_URL", "http://localhost:4646")

VMCK_BACKEND = os.environ.get("BACKEND", "docker")
QEMU_IMAGE_PATH_PREFIX = os.environ.get("QEMU_IMAGE_PATH_PREFIX")
QEMU_CPU_MHZ = int(os.environ.get("QEMU_CPU_MHZ", QEMU_CPU_MHZ))

VM_PORT_RANGE_START = int(os.environ.get("VM_PORT_RANGE_START", 10000,))
VM_PORT_RANGE_STOP = int(os.environ.get("VM_PORT_RANGE_STOP", 20000,))

_ssh_username = SSH_USERNAME
SSH_USERNAME = os.environ.get("SSH_USERNAME", _ssh_username)

APP_THREAD_COUNT = int(os.environ.get("APP_THREAD_COUNT", 8))

SENTRY_DSN = os.environ.get("SENTRY_DSN")
sentry_sdk.init(dsn=SENTRY_DSN, integrations=[DjangoIntegration()])
