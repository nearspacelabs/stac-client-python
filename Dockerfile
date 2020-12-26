FROM python:3.7.7-slim-buster

RUN DEBIAN_FRONTEND=noninteractive apt-get update

WORKDIR /opt/src/stac-client-python
COPY ./ /opt/src/stac-client-python

RUN pip install --upgrade pip==20.1.1
RUN pip install -r requirements.txt
RUN pip install -r requirements-demo.txt
RUN python setup.py install

RUN mkdir /root/.jupyter
RUN jupyter notebook --generate-config

RUN jupyter contrib nbextension install --user
RUN jupyter nbextensions_configurator enable --user
RUN jupyter nbextension enable varInspector/main
RUN jupyter nbextension enable hinterland/hinterland

CMD jupyter notebook --allow-root --NotebookApp.allow_origin='*' NotebookApp.allow_remote_access=True --NotebookApp.open_browser=False --NotebookApp.ip='*'
