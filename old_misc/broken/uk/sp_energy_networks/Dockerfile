FROM python:3.13-alpine

WORKDIR /app

COPY ./src/scrapers/uk/sp_energy_networks/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/scrapers/uk/sp_energy_networks/*.py .
COPY ./utils/ utils/

CMD ["python", "scrape.py"]
