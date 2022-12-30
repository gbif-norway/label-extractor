FROM python:3.10.6-buster
RUN apt-get update && \
    apt-get install -y zbar-tools ffmpeg libsm6 libxext6
RUN pip install --upgrade pip && \
    pip install pika imagecodecs opencv-python scikit-image==0.19.3 pyzbar==0.1.9
WORKDIR /srv/code
CMD python detector.py
