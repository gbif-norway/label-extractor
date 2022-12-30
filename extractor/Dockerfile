FROM python:3.10.6-buster
#COPY ./code /srv/code
RUN pip install --upgrade pip && pip install pandas pika nltk pycountry cyrtranslit
WORKDIR /srv/code
CMD ["python", "/srv/code/consumer.py"]
