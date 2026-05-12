FROM python:3.13-alpine

WORKDIR /app

COPY ./src/scrapers/spain/naturgy/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/scrapers/spain/naturgy/*.py .
COPY ./utils/ utils/

CMD ["python", "scrape.py"]
