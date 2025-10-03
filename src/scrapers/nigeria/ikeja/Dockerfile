FROM python:3.13-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY scrape.py .
COPY post_process.py .
COPY utils/ utils/

CMD ["python", "scrape.py"]