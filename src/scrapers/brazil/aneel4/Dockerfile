FROM python:3.13-alpine

WORKDIR /app

COPY ./src/scrapers/brazil/aneel4/requirements.txt .
COPY ./src/scrapers/brazil/aneel4/*.py .
COPY ./utils/ utils/

RUN pip install --no-cache-dir -r requirements.txt

ENV IS_DOCKER_CONTAINER=true