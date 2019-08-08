#!/bin/bash -ex

cd "$( dirname "${BASH_SOURCE[0]}" )"/..

sudo pip3 install pipenv
sudo pipenv install --system --deploy
exec pytest
