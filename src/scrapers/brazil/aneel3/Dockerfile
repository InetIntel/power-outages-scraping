FROM python:3.13-alpine

WORKDIR /app

COPY ./src/scrapers/brazil/aneel3/requirements.txt .
COPY ./src/scrapers/brazil/aneel3/*.py .
COPY ./utils/ utils/

RUN pip install --no-cache-dir -r requirements.txt
