FROM python:3.13-alpine

WORKDIR /app

COPY ./src/scrapers/portugal/e_redes/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/scrapers/portugal/e_redes/*.py .
COPY ./utils/ utils/

CMD ["python", "scrape.py"]
