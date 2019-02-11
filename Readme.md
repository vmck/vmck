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

2. Install [factory][] and check that it works:
    ```shell
    pakku -Sy qemu socat
    python3 <(curl -sL https://github.com/liquidinvestigations/factory/raw/master/install.py) /tmp/factory
    /tmp/factory/factory run echo hello world
    ```

3. Set up the VMCK server:
    ```shell
    pipenv install
    echo 'SECRET_KEY=changeme' > .env
    echo 'DEBUG=true' >> .env
    echo 'FACTORY_HOME=/tmp/factory' >> .env
    pipenv run ./manage.py migrate
    ```

[factory]: https://github.com/liquidinvestigations/factory#readme

## Usage

* Run the web server:
    ```shell
    pipenv run ./manage.py runserver
    ```

* Create a job:
    ```shell
    pipenv run ./manage.py createjob
    ```
