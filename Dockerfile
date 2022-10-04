FROM ubuntu:18.04

RUN apt update && apt install -y python3 python3-pip prometheus-node-exporter

COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt