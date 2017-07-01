FROM python:2.7

MAINTAINER Evgeny Shakhmaev

WORKDIR /app
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./ .