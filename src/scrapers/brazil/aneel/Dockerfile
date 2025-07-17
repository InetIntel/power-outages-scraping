FROM python:3.13-alpine

WORKDIR /app

COPY ./src/scrapers/brazil/aneel/requirements.txt .
COPY ./src/scrapers/brazil/aneel/*.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "scrape.py"]
