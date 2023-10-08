FROM python:3.11.6-alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

COPY  . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt