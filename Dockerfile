FROM python:3.6-slim

RUN DEBIAN_FRONTEND=noninteractive apt-get update

WORKDIR /opt/src/stac-client-python
COPY ./ /opt/src/stac-client-python

RUN pip3 install .
