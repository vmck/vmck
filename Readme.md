[![Build Status](https://frisbee.grid.pub.ro/api/badges/vmck/vmck/status.svg)](https://frisbee.grid.pub.ro/vmck/vmck)

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
Here you can add different `--env` options with arguments matching
`{root}/vmck/settings.py` and `{root}/vmck/base_settings.py` to suit your
preferences.

Then go to consul (`http://localhost:8500/ui/dc1/services`) and wait for the
health check lights to turn green.

### Running locally

- Needs a Nomad instance alongside Consul([liquidinvestigations/cluster](https://github.com/liquidinvestigations/cluster) is easy to set-up and has both Nomad and Consul)
- If you are using the above mentioned cluster you can skip this step if not add the following to your `.env` file:
```
SECRET_KEY=change_me
CONSUL_URL=your_consul_url
NOMAD_URL=your_nomad_url
```
- By default the `docker` backend is selected. You can choose `qemu` by adding `BACKEND=qemu` to your `.env` file
- Then install dependencies and run migrations:
```shell
pipenv install
pipenv run ./manage.py migrate
```
- Then you can run the server:
```shell
pipenv run ./manage.py runserver
```

## Running VMCK on your cluster

You need Nomad cluster with Consul. To start vmck in your Nomad cluster:

```shell
export NOMAD_URL='your_nomad_url' # skip this line if you are using liquidinvestigations/cluster
cd examples
./cluster.py
```

Now VMCK is a job in your Nomad cluster.

## Qemu VM images

Now all images are built using [vmck/image-builder](https://github.com/vmck/image-builder).
Please refer to it on how to build, provision and test your image.

## Testing

### Requirements

- Nomad instance alongside Consul([liquidinvestigations/cluster](https://github.com/liquidinvestigations/cluster) is easy to set-up and has both Nomad and Consul)
- If you are using the above mentioned cluster you can skip this step if not add the following to your `.env` file:
```
TESTING_CONSUL_URL=your_consul_url
TESTING_NOMAD_URL=your_nomad_url
```
- By default the `docker` backend is selected. You can choose `qemu` by adding `TESTING_BACKEND=qemu` to your `.env` file

### Docker backend

The docker backend uses [vmck/mock](https://github.com/vmck/mock) as it's default image.
The only way to change that is to modify `{root}/vmck/backends/docker.py docker_vm_task.config.image`.
We do not recommend it as the docker backend is for **testing purposes only**.
Check [vmck/vagrant-vmck](https://github.com/vmck/vagrant-vmck) and [Vagrant](https://www.vagrantup.com/docs/)
on how to provision, test and use the job that vmck will start.

### Qemu backend

This requires a bit more configuration. Qemu images are retrieved through a `nginx` server.
You need to have one. [Here](https://github.com/liquidinvestigations/node/blob/master/templates/drone.nomad#L8) is an example of a `.hcl` job specification
that you can use to start the server on your Nomad cluster. You need to set `TESTING_QEMU_IMAGE_PATH_PREFIX` in `.env` file
to the url of your `nginx` server. To use the image of your choosing set `image_path` option
in your `POST` request to the name of your desired image.

### Doing tests
With a Nomad cluster up and running, run `pipenv run pytest`, and enjoy.

## Troubleshooting
* QEMU fails to start with error `qemu-system-x86_64: Invalid host forwarding
  rule 'tcp:${attr.unique.network.ip-address}:10674-:22' (Bad host address)`:
  the host address has changed (e.g. because it moved to a different WiFi
  hotspot). Restart Nomad and it should pick up the new address.
