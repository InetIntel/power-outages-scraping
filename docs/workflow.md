# Workflow

## Requirements

Working `scraper.py` and `post_process.py` files for each country and power provider.

## Getting Started

Starting the containers. Check docker-compose.yml for the services that will be started.

```
make run
```

Go into the individual project and publish the Docker image to the registry.
Here's an example Makefile that can be placed in the individual scraper folder:

```Makefile
.PHONY: build
build:
 docker build -t localhost:5000/brazil-aneel-scraper:latest .

.PHONY: publish
publish: build
 docker push localhost:5000/brazil-aneel-scraper:latest

```

Sample Dockerfile for the scraper:

```Dockerfile
FROM python:3.13-alpine

WORKDIR /app

COPY requirements.txt .
COPY *.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "scrape.py"]
```

Publish the image by running

```shell
make publish
```

The published image can be verified in the registry by running the following commands:

```
curl http://localhost:5000/v2/_catalog
curl http://localhost:5000/v2/myapp/tags/list
```

Create a DAGU configuration file in `dagu_config/dags` to define the DAG for the scraper.
The DAG should include the tasks for scraping and post-processing.
The name should be `{country}_{company}.yaml` Here's an example configuration

```yaml
steps:
  - name: scrape
    executor:
      type: docker
      config:
        image: localhost:5000/brazil-aneel-scraper:latest
        autoRemove: true
    command: python scrape.py


  - name: process
    executor:
      type: docker
      config:
        image: localhost:5000/brazil-aneel-scraper:latest
        autoRemove: true
    command: python post_process.py
```

Navigate to DAGU to run dags in `localhost:8080`
and the block storage interface can be accessed in `localhost:9090`

## Architecture

![Architecture](./img/Architecture.jpg)

## Architecture TBD

![Architecture Ideal](./img/Architecture-Ideal.jpg)

## Resources

<https://github.com/dagu-org/dagu>

<https://github.com/minio/minio>
