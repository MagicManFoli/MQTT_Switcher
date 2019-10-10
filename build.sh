#!/usr/bin/env bash

# pipenv is bad for this kind of deployment,
# as alpine does not support it and it's too large
pipenv lock -r > requirements.txt

# could be moved to compose
docker build .

