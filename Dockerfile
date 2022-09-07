FROM python:3.10.6-buster
RUN apt-get update && \
    apt-get install -y vim zbar-tools ffmpeg libsm6 libxext6
COPY requirements.txt /tmp/requirements.txt
COPY gapi-secret.json /srv/gapi-secret.json
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt
