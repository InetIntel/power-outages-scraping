FROM python:3.13-alpine

WORKDIR /app

COPY ./src/scrapers/ukraine/vinnytsia/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/scrapers/ukraine/vinnytsia/*.py .
COPY ./utils/ utils/

CMD ["python", "scrape.py"]
