import sys
import os
from time import time, sleep
from pathlib import Path
import shutil
import logging
from subprocess import run, STDOUT, CalledProcessError
from tempfile import TemporaryFile

debug = os.environ.get('DEBUG', '').lower() in ['1', 'on', 'yes', 'true']
control_path = Path(__file__).parent.resolve()
agent_path = control_path / 'agent.sh'
poweroff_path = control_path / 'poweroff.sh'
ssh_key_path = control_path / 'ssh/id_ed25519'

log_level = logging.DEBUG if debug else logging.INFO
log = logging.getLogger(__name__)
log.setLevel(log_level)


def ssh(host, port, username, stdin_path):
    verbosity_arg = '-v' if debug else '-q'
    args = [
        '/usr/bin/ssh', f'{username}@{host}',
        '-p', f'{port}',
        '-i', ssh_key_path,
        '-o', 'UserKnownHostsFile=/dev/null',
        '-o', 'StrictHostKeyChecking=no',
        '-o', 'ConnectTimeout=1',
        '-T', verbosity_arg,
    ]

    with stdin_path.open('rb') as stdin:
        run(args, stdin=stdin, stderr=STDOUT, check=True)


def retry(timeout, sleep_seconds, func, args=(), kwargs={}):
    log.debug(
        "Retrying %s (args=%r, kwargs=%r) every %rs, up to %rs",
        func.__name__, args, kwargs, sleep_seconds, timeout,
    )
    t0 = time()
    n = 0
    while time() < t0 + timeout:
        n += 1

        try:
            rv = func(*args, **kwargs)
            log.debug("Success: %r", rv)
            return rv

        except Exception as e:
            log.debug("Failed %d: %r ...", n, e)
            sleep(sleep_seconds)

    else:
        msg = f"retry {func.__name__} failed {n} times in {timeout} seconds"
        raise RuntimeError(msg)


def cp(src, dest_dir):
    shutil.copy(src, dest_dir / src.name)


def main():
    cp(Path(__file__).parent / 'agent.sh', Path('alloc/data'))

    ssh_auth = [
        os.environ['VM_HOST'],
        os.environ['VM_PORT'],
        os.environ['VM_USERNAME'],
    ]

    retry(600, .5, ssh, ssh_auth + [agent_path])
    try:
        ssh(*ssh_auth, poweroff_path)
    except CalledProcessError:
        pass  # `ssh poweroff` returns error code, so we expect this exception


if __name__ == '__main__':
    logging.basicConfig(level=log_level)
    main()
