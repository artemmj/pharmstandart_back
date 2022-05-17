FROM registry/templates/image/python:3-7-alpine

WORKDIR /app

COPY project/requirements /app/requirements
RUN pip install --no-cache-dir -r requirements/dev.txt

COPY project /app
COPY docker/app/  /
