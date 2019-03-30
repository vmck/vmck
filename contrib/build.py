#!/usr/bin/env python3

import logging
from pathlib import Path
from argparse import ArgumentParser
from tempfile import TemporaryDirectory
import subprocess
import shlex

log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)

CACHE = Path.home() / '.cache/vmck-build'

BIONIC_URL = (
    'https://cloud-images.ubuntu.com/bionic/current/'
    'bionic-server-cloudimg-amd64.img'
)

SSH_PUBKEY = (
    'ssh-ed25519 '
    'AAAAC3NzaC1lZDI1NTE5AAAAIM9QBDGxYk2MjJHMa30Ut166/s61Yk1ieTn3aXjAnnvP '
    'vmck'
)

CLOUD_INIT_YML = f"""\
#cloud-config
ssh_authorized_keys: ['{SSH_PUBKEY}']
packages: ['build-essential', 'curl', 'less', 'vim']
runcmd:
  - "echo '127.0.1.1 ubuntu' >> /etc/hosts"
  - "touch /etc/cloud/cloud-init.disabled"
  - "systemctl disable apt-daily.service"
  - "systemctl disable apt-daily.timer"
  - "touch /home/ubuntu/.hushlogin"
  - "apt-get clean"
  - "cat /dev/zero > /ZERO || rm /ZERO"
  - "poweroff"
"""


def shq(value):
    return shlex.quote(str(value))


def sh(cmd):
    log.debug('+ %s', cmd)
    subprocess.run(cmd, shell=True, check=True)


def download(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / f'{dest.name}.tmp'
    sh(f'curl -L {shq(url)} -o {shq(tmp)}')
    Path(tmp).rename(dest)


def build(tmp, output):
    upstream = CACHE / 'bionic-server-cloudimg-amd64.img'
    if not upstream.exists():
        log.info("Downloading cloud image from %r", BIONIC_URL)
        download(BIONIC_URL, upstream)

    log.info("Preparing disk image")
    disk = tmp / 'disk.img'
    sh(f'qemu-img create -q -f qcow2 -b {shq(upstream)} {shq(disk)}')
    sh(f'qemu-img resize {shq(disk)} 10G')

    log.info("Preparing cloud-init image")
    cloud_init_yml = tmp / 'cloud-init.yml'
    cloud_init_img = tmp / 'cloud-init.img'
    with cloud_init_yml.open('w', encoding='utf8') as f:
        f.write(CLOUD_INIT_YML)

    sh(f'cloud-localds {shq(cloud_init_img)} {shq(cloud_init_yml)}')

    log.info("Running qemu")
    sh(
        'qemu-system-x86_64 -enable-kvm -nographic -m 512 '
        '-netdev user,id=user -device virtio-net-pci,netdev=user '
        f'-drive discard=unmap,detect-zeroes=unmap,file={shq(disk)} '
        f'-drive format=raw,file={shq(cloud_init_img)}'
    )

    log.info("Exporting disk image")
    sh(f'qemu-img convert -O qcow2 -p {shq(disk)} {shq(output)}')


def main():
    parser = ArgumentParser()
    parser.add_argument('output', type=Path)
    options = parser.parse_args()

    with TemporaryDirectory() as tmp:
        build(Path(tmp), options.output)


if __name__ == '__main__':
    logging.basicConfig(level=log_level)
    main()
