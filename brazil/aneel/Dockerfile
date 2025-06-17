FROM python:3.13-alpine

WORKDIR /app

COPY requirements.txt .
COPY aneel.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "aneel.py"]
