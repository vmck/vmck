import os
from time import time, sleep
from contextlib import contextmanager
import pty
from pathlib import Path
import shutil
import logging
import shlex

debug = os.environ.get('DEBUG', '').lower() in ['1', 'on', 'yes', 'true']

log_level = logging.DEBUG if debug else logging.INFO
log = logging.getLogger(__name__)
log.setLevel(log_level)


@contextmanager
def pty_process(command):
    (pid, fd) = pty.fork()
    if not pid:
        os.execv(command[0], command)

    try:
        yield fd

    finally:
        (_, exit_code) = os.waitpid(pid, 0)
        if exit_code != 0:
            raise RuntimeError()


def pty_ssh(host, port, username, password, command):
    ssh_args = [
        '/usr/bin/ssh', f'{username}@{host}',
        '-p', f'{port}',
        '-o', 'UserKnownHostsFile=/dev/null',
        '-o', 'StrictHostKeyChecking=no',
        '-o', 'NumberOfPasswordPrompts=1',
        '-o', 'ConnectTimeout=1',
        command,
    ]

    shell_args = ' '.join(shlex.quote(a) for a in ssh_args)
    log.debug("running in pty: %s", shell_args)
    with pty_process(ssh_args) as fd:
        while True:
            try:
                log.debug('reading output ...')
                output = os.read(fd, 1024)
                log.debug('got %r', output)

            except Exception:
                return

            if b'password:' in output.lower().strip():
                log.debug('sending password')
                os.write(fd, password.encode('utf8') + b'\n')
                break

        log.debug('waiting for output ...')
        out = b''

        while True:
            try:
                chunk = os.read(fd, 1024)
                log.debug('got chunk %r', chunk)
                out += chunk

            except Exception:
                return out


def retry(timeout, sleep_seconds, func, *args, **kwargs):
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
    cp(Path(__file__).parent / 'agent', Path('alloc/data'))

    bootstrap_command = ' && '.join([
        'set -x',
        'sudo mkdir /tmp/vmck',
        'sudo mount -t 9p -o trans=virtio vmck /tmp/vmck -oversion=9p2000.L',
        'sudo /tmp/vmck/agent 1> /tmp/vmck/stdout.txt 2> /tmp/vmck/stderr.txt'
    ])

    pty_ssh_args = [
        os.environ['VM_HOST'],
        os.environ['VM_PORT'],
        os.environ['VM_USERNAME'],
        os.environ['VM_PASSWORD'],
        bootstrap_command,
    ]

    log.info("Running bootstrap command in VM")
    out = retry(30, .5, pty_ssh, *pty_ssh_args)

    log.info(
        "ssh:\n==== ssh output ====\n%s\n===============",
        out.decode('utf8', errors='replace'),
    )


if __name__ == '__main__':
    logging.basicConfig(level=log_level)
    main()
