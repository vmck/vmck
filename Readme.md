# Vmck
Vmck is a virtual machine service that runs QEMU and Docker images in a Nomad
cluster.

It can be used as a provider for Vagrant:

```shell
vagrant plugin install vagrant-vmck
curl -OL https://github.com/mgax/vagrant-vmck/raw/master/example_box/Vagrantfile
vagrant up
vagrant ssh
```

And it has its own CLI:

```shell
pipenv run ./manage.py createjob
pipenv run ./manage.py ssh 1
pipenv run ./manage.py kill 1
```

## Installation

### Using docker
```shell
docker run --detach --restart always \
  --name cluster \
  --volume /opt/cluster/var:/opt/cluster/var \
  --volume /opt/vmck/var:/opt/vmck/var \
  --volume /var/run/docker.sock:/var/run/docker.sock:ro \
  --privileged \
  --net host \
  --env NOMAD_CLIENT_INTERFACE=wg0 \
  --env HOSTNAME=127.0.0.1 \
  --env SECRET_KEY=foo \
  mgax/vmck
```

Then go to consul (`http://localhost:8500/ui/dc1/services`) and wait for the
health check lights to turn green.

### Running locally

You still need a working Consul + Vault + Nomad cluster, maybe
[liquidinvestigations/cluster][] can help you.

Create a file named `.env` with your local configuration:
```shell
SECRET_KEY=changeme
# DEBUG=true
```

Then install dependencies and run migrations:

```shell
pipenv install
pipenv run ./manage.py migrate
```

Then you can run the server:

```shell
pipenv run ./manage.py runserver
```

## Running on your cluster

You still need a working Consul + Vault + Nomad cluster, maybe
[liquidinvestigations/cluster][] can help you. This cluster will usualy be
available at `http://10.66.60.1:4646`. If you choose to use another cluster
you should change `NOMAD_URL` in `examples/cluster.py` to your
Nomad cluster's IP.

To start vmck in your Nomad cluster:

```shell
cd examples
./cluster.py
```

This will send a job request to Nomad's API. Go to your Nomad cluster's web UI
and you should find vmck in the job section. Watch the lights turn green.

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
