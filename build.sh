#!/usr/bin/env bash

# pipenv is bad for this kind of deployment,
# as alpine does not support it and it's too large
pipenv lock -r > requirements.txt

# could be moved to compose
docker build -t mqtt_switcher:latest .

# relative path will convert to directory
# docker run -it -v $(pwd)/config.yml:/config.yml mqtt_switcher
