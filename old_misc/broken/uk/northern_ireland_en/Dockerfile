FROM python:3.13-alpine

WORKDIR /app

COPY ./src/scrapers/uk/northern_ireland_en/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/scrapers/uk/northern_ireland_en/*.py .
COPY ./utils/ utils/

CMD ["python", "scrape.py"]
