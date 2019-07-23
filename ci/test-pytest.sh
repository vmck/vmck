#!/usr/sbin/env bash

cd "$( dirname "${BASH_SOURCE[0]}" )"/..

sudo -H pip3 install pipenv
pipenv install
pipenv run pytest
