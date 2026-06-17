FROM python:3.13-alpine

WORKDIR /app

COPY ./src/scrapers/japan/okinawa/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/scrapers/japan/okinawa/*.py .
COPY ./utils/ utils/

CMD ["python", "scrape.py"]
