FROM python:3.13-alpine

WORKDIR /app

COPY ./brazil/aneel/requirements.txt .
COPY ./brazil/aneel/*.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "scrape.py"]
