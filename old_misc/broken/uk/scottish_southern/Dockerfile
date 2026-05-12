FROM python:3.13-alpine

WORKDIR /app

COPY ./src/scrapers/uk/scottish_southern/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/scrapers/uk/scottish_southern/*.py .
COPY ./utils/ utils/

CMD ["python", "scrape.py"]
