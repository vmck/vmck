#!/usr/bin/env bash

cd "$( dirname "${BASH_SOURCE[0]}" )"/..

sudo -H pip3 install pipenv
pipenv install
exec pipenv run pytest
