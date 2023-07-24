FROM python:3.10.6-buster
COPY ./code /srv/
RUN pip install --upgrade pip && \
    pip install pika google-auth==1.35.0 google-cloud-core==1.7.3 google-cloud-translate==2.0.1 google-cloud-vision==3.1.1
WORKDIR /srv
CMD ["python", "/srv/consumer.py"]
