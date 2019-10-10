# TODO alpine
FROM python:3.7

# install additional dependencies
# (was pipenv previously but had problems with alpine)
COPY ./requirements.txt requirements.txt
RUN chmod +r requirements.txt

# caches are useless in containers
RUN pip install --no-cache-dir -r requirements.txt

### -- builder image could go until here

# only the application is relevant for the container
COPY ./app /app

# set everything as executable to be sure
RUN chmod -R +rx /app

ENTRYPOINT ["app/main.py", "-f /config.yaml"]
