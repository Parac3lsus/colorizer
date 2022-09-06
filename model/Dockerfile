FROM python:3.8.13 as base

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
ADD requirements.txt .
RUN pip3 install -r requirements.txt

ENV PYTHONPATH=$PYTHONPATH:/src/

ADD ./ /src/

WORKDIR /src

FROM base as build
ENTRYPOINT ["python3", "/src/ml_service.py"]

