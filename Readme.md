# VMCK

## Installation

1. Set up a local nomad cluster:

    * Install nomad and consul:
        ```shell
        mkdir /tmp/cluster; cd /tmp/cluster
        curl -OL https://releases.hashicorp.com/nomad/0.8.7/nomad_0.8.7_linux_amd64.zip
        curl -OL https://releases.hashicorp.com/consul/1.4.2/consul_1.4.2_linux_amd64.zip
        unzip consul_1.4.2_linux_amd64.zip
        ```

    * Create a configuration file, `/tmp/cluster/nomad.hcl`, with the following
      content, adapted to your machine in case `eth0` is not the main network
      interface:
        ```hcl
        advertise {
          http = "{{ GetInterfaceIP `eth0` }}"
          serf = "{{ GetInterfaceIP `eth0` }}"
        }
        client {
          enabled = true
          network_interface = "eth0"
        }
        ```

    * Run consul and nomad:
        ```shell
        cd /tmp/cluster
        ./consul agent -dev &
        ./nomad agent -dev -config=./nomad.hcl &
        ```

2. TODO explain how to set up an http server for the images

3. Set up the VMCK server:
    ```shell
    pipenv install
    echo 'SECRET_KEY=changeme' > .env
    echo 'DEBUG=true' >> .env
    echo 'QEMU_IMAGE_URL=http://example.com/artful.qcow2' >> .env
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
