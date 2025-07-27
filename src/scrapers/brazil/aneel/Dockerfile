FROM python:3.13-alpine

# Install Chromium + ChromeDriver
RUN apk add --no-cache \
    chromium \
    chromium-chromedriver \
    bash \
    && rm -rf /var/cache/apk/*

# Set environment for Selenium
ENV CHROME_BIN=/usr/bin/chromium-browser
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /app

COPY ./src/scrapers/brazil/aneel/requirements.txt .
COPY ./src/scrapers/brazil/aneel/*.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "scrape.py"]
