FROM python:3.7

ENV PYTHONUNBUFFERED 1

RUN apt-get update

RUN mkdir /code
WORKDIR /code
COPY . /code/
RUN pip install -r Zabbix_Maintenance/requirements.txt
