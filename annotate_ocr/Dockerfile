FROM python:3.10.6-buster
#COPY ./code /srv/
RUN pip install --upgrade pip && \
    pip install pika json requests
WORKDIR /srv
CMD ["python", "/srv/consumer.py"]
