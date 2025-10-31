# Power Outage Data Scraping

## Overview

This repo contains the workflow for scraping data from power providers in different countries using Docker, DAGU, and minio.
- scapers: written in Python using libraries like scrapy.
- Docker: containerizes the scraping, post-processing, and upload scripts.
- DAGU: orchestrates each of the scrapers, running them periodically and managing the various logs and re-tries.
- minio: block storage for the scraped data.

## Architecture

![Architecture](./old_misc/docs/img/Architecture.jpg)

<!-- ## Example

Refer to the `src/scrapers/brazil/aneel` scraper. -->

## Requirements

<!-- Working `scraper.py` and `post_process.py` files for each country and power provider. -->
- Docker installed and added to the CLI
- ideally: some way to run UNIX commands in the CLI -- macos comes w/ this. windows: install git bash, WSL, etc.

## Getting Started

### Converting a single scraper into a docker + DAGU instance (NEW but kinda rushed)
- TLDR: copy `src/scrapers/brazil/aneel3`, make a DAGU YAML (copy brazil_aneel3.yaml and edit)
- make a directory structued as such: `src/scrapers/country/power_company` 
- implement the Scraper interface in Scraper.py (just the scrape and process functions)
  - it assumes that you scrape raw files into a `/raw` sub directory, and process it into a `/processed` subdir
  - currently, the buckets are to be structued as such:
    - `raw/country/power-company/date-that-data-represents_date-data-was-scraped`
    - `processed/country/power-company/date-that-data-represents_date-data-was-scraped`
    - e.g.: if we have data for 7/27/24 scraped on 10/31/25 5PM, it'd be `2024-7-27_2025-10-31-05-00-00.csv`
    - each raw file should eventually have a matching processed file. the paths are the same, with only the bucket name differentiating them.
- make a `main-prod.py` folder. format similarly to aneel3 -- it just calls Scraper a bunch of times. 
- see below for building + publishing

### Converting a single scraper into a docker + DAGU instance
- TLDR: copy the format of `/src/scrapers/brazil/aneel3` and run a handful of commands
- have three python files, one for each step of the scraping process (scrape, process, upload), and a requirements.txt
  - upload can be empty -- still working on that stuff atm
- make sure the python files are within a folder under `/src/scrapers`
- build and publish the Docker container: 
  - `./publish-single.sh ./src/scrapers/your_country/your_power_company`
- setup your local directories: `make docker-local-setup`
  - if you don't have a UNIX environment to run the MAKE  commands, look into `publish.sh` and run the individual `mkdir` commands
- make a DAGU config file 
  - refer to the [DAGU config section](#adding-a-scraper-to-dagu)
- `docker compose up -d` or `make run` 
- inspect and run your scraper at localhost:8080
  - you can manually run the sraper by hovering the left side and clicking on "DAG Definitions", then clicking on your scaper of choice and clicking the play button
- NOTE: if you make a change to the DAGU config file, DAGU will update to match. if you make a change to your python files, you will need to rebuild the container (`publish-single`).


### Adding a scraper to DAGU
- Create a DAGU configuration file in `dagu_config/dags` to define the DAG (workflow) for the scraper.
- The DAG should include the tasks for scraping and post-processing.
- The name should be `{country}_{company}.yaml` Here's an example configuration and reference to the YAML Specification can be found in [here](https://docs.dagu.cloud/reference/yaml).

```yaml
# https://docs.dagu.cloud/features/scheduling
# schedule: "0 2 * * *" # Daily at 2 AM
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


### Running the entire set of scrapers 
**NOTE**: the commands on this readme assumes a UNIX working environment.

Starting the containers. Check docker-compose.yml for the services that will be started.

```
make run
```

Publish the image by running the command below. It will auto detect the scrapers in the `src/scrapers` and create a Dockerfile.

```shell
make publish
```

The published image can be verified in the registry by running the following commands:

```
curl http://localhost:5000/v2/_catalog
curl http://localhost:5000/v2/myapp/tags/list
```

Navigate to DAGU to run dags in `localhost:8080`
and the block storage interface can be accessed in `localhost:9090` with the default name/password: `minioadmin`

### Testing DAGU
- print statements will not print until the particular step is finished
  - e.g.: if you have a long scrape step, nothing prints until scrape finishes. using print() with flush=True doesn't seem to fix this.
- make a change in python → rebuild the docker container
  - `./publish-single.sh ./src/scrapers/your_scraper_here`
- rerun specific portions of DAGU
  - e.g.: to rerun the proces part but not the scrape part
  - click on DAG you want to edit
  - right click → set status to success
  - click on "retry DAG execution" (the whirly symbol -- NOT the arrow to "start execution")


## Resources

<https://github.com/dagu-org/dagu>

<https://github.com/minio/minio>

## Last Updated
10/6/25