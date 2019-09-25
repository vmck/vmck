import os
import string
import secrets
from socket import gethostname

vocabulary_64 = string.ascii_letters + string.digits + '.+'
hostname = os.environ.get('HOST', gethostname())


def random_code(length, vocabulary=vocabulary_64):
    return ''.join(secrets.choice(vocabulary) for _ in range(length))


def is_true(value):
    text = (value or '').lower().strip()
    return text in ['1', 'yes', 'true', 'on', 'enabled']
