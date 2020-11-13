FROM python:3.7.7-slim-buster

RUN DEBIAN_FRONTEND=noninteractive apt-get update

WORKDIR /opt/src/stac-client-python
COPY ./ /opt/src/stac-client-python

RUN pip3 install --upgrade pip
RUN pip3 install .
