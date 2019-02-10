# VMCK

## Installation

1. Set up a local nomad cluster:

    * Install nomad:
        ```shell
        pakku -Sy nomad consul
        ```

    * Create a configuration file, `/tmp/nomad.hcl`, with the following
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
        consul agent -dev &
        nomad agent -dev -config=/tmp/nomad.hcl &
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
