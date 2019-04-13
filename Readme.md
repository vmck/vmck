# VMCK

## Installation

1. Set up a local nomad cluster:

    * Install nomad:
        ```shell
        mkdir /tmp/cluster; cd /tmp/cluster
        curl -OL https://releases.hashicorp.com/nomad/0.8.7/nomad_0.8.7_linux_amd64.zip
        unzip nomad_0.8.7_linux_amd64.zip
        ```

    * Create a configuration file, `/tmp/cluster/nomad.hcl`, with the following
      content, replacing `eth0` with the default network interface, which you
      can determine by running `route | grep default | awk '{print $8}'`:
        ```hcl
        advertise {
          http = "{{ GetInterfaceIP `eth0` }}"
          serf = "{{ GetInterfaceIP `eth0` }}"
        }
        server {
          job_gc_threshold = "5m"
        }
        client {
          enabled = true
          network_interface = "eth0"
        }
        ```

    * Run nomad:
        ```shell
        cd /tmp/cluster
        ./nomad agent -dev -config=./nomad.hcl &
        ```

2. Set up the VMCK server:
    ```shell
    pipenv install
    echo 'SECRET_KEY=changeme' > .env
    echo 'DEBUG=true' >> .env
    pipenv run ./manage.py migrate
    ```

## Usage

* Run the web server:
    ```shell
    pipenv run ./manage.py runserver
    ```

* Create a job:
    ```shell
    pipenv run ./manage.py createjob
    ```

## VM images
Each job spins up a QEMU virtual machine to evaluate the submission. It needs a
disk image, which can be downloaded from https://github.com/mgax/vmck-images,
or built using `contrib/build.py`, which downloads an [Ubuntu cloud image][],
prepares a [cloud-init][] configuration, applies it, and exports the resulting
image. Run it with an argument to specify the output path:

```shell
./contrib/build.py /tmp/bionic.qcow
```

[Ubuntu cloud image]: https://cloud-images.ubuntu.com
[cloud-init]: https://cloudinit.readthedocs.io

## Testing
With a Nomad cluster running on `localhost:4646`, run `pipenv run pytest`, and
enjoy. By default, the test suite will use a *mock vm*, implemented with a
docker backend, instead of qemu. To run the tests with the qemu backend, set
`TESTING_BACKEND=qemu` in the `.env` file.

To make the qemu tests run faster you can mirror the VM image locally and
override the URL in the local `.env` file - see `testsuite/settings.py` for the
default image.

## Troubleshooting
* QEMU fails to start with error `qemu-system-x86_64: Invalid host forwarding
  rule 'tcp:${attr.unique.network.ip-address}:10674-:22' (Bad host address)`:
  the host address has changed (e.g. because it moved to a different WiFi
  hotspot). Restart Nomad and it should pick up the new address.
