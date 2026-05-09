FROM python:3.13-alpine

WORKDIR /app

COPY ./src/scrapers/brazil/aneel2/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/scrapers/brazil/aneel2/*.py .
COPY ./utils/ utils/

CMD ["python", "scrape.py"]
