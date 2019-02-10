# VMCK

## Installation

1. Set up the VMCK server:
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
