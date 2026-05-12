FROM python:3.13-alpine

WORKDIR /app

COPY ./src/scrapers/india/tangedco/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/scrapers/india/tangedco/*.py .
COPY ./utils/ utils/

CMD ["python", "scrape.py"]
