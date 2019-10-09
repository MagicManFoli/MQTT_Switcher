# TODO alpine
FROM python:3.7

# install additional dependencies
# (was pipenv previously but had problems with alpine)
COPY ./requirements.txt requirements.txt
# caches are useless in containers
RUN pip install --no-cache-dir -r requirements.txt

# only the application is relevant for the container
COPY ./app /app

ENTRYPOINT ["app/main.py", "-f /config.yaml"]
