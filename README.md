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
- Python, Docker installed and added to the CLI
- Ideally: some way to run UNIX commands in the CLI -- macos comes w/ this. windows: install git bash, WSL, etc. This will come in handy when running the build script (`publish-single.sh`)

## Getting Started
### TLDR
- Init with `python create-scraper.py` and implement the scrape and process methods in `Scraper.py`
  - Refer to `./src/brazil/aneel4` for an example implementation.
- Test locally with `PYTHONPATH=. python src/scrapers/[your_country]/[your_secondary]/main-prod.py --step [your_step]`
- Build with `publish-single.sh [path_to_your_scraper]`
- `docker compose up -d` and DAGU is on localhost 9090, minio on 8080

### Initializing a Scraper
- Initialize a starter set of files. You will be asked to provide a country and a secondary distinction (e.g.: a city name). Run:
	- `python create-scraper.py`
- This will create several files under `./src/scrapers/your_country/your_secondary_location`
  - `Scraper.py`: the main file you will edit. Implement the `scrape` and `process` functions.
    - Take a look at `./utils/BaseScraper` to see functions and class parameters you may find useful, such as `self.raw_local_dir`. 
  - `main-prod.py`: parses the args for Dockerization. Generally don't edit.
  - `requirements.txt`: requirement files for your Python libraries. Routinely update this with a `pip freeze`, e.g.

### Notes on Scraping + Processing
- The scrapers generally have two phases: scraping, and processing.
  - Scraping involves firstly making the API request/page load/data retrieval to get the data for that particular site. This data will eventually be uploaded to a minio instance, but local dev will just upload to local directories.
  - Processing involves the transformations to make the data usable. In the full production environment, we will first download a copy of the previously scraped data into a local dir, process it, and upload it back to minio. 

- Files should be put into two different directories: raw for raw data that hasn't been edited (e.g.: the entire raw HTML of a page or a giant JSON of sorts), and processed for data that has been transformed into a more usable format.

- [TBD] By default, the Base Scraper class assumes that data is stored in the raw and processed folders. Within these folders, there is first the country and secondly some other distinction (such as city or power company name). For the Aneel power provider in Brazil, for example, we might have the dirs `./raw/brazil/aneel` and `./processed/brazil/aneel`. 

- [TBD] Files should be placed in the proper dirs and be named firstly by the date they represent, followed by the date scraped, the country and secondary distinction again for redudancy, and the state of the data (raw/processed).
  - e.g.: data for Nov. 2025 for Brazil's Aneel scraped in Dec. 2025 should be named `11-2025_12-2025_brazil_aneel-raw.json` when under `./raw/brazil/aneel/` and then renamed to `11-2025_12-2025_brazil_aneel-processed.json` when under `./processed/brazil/aneel`. 

### Running Locally (no Docker/minio)
- From the base project directory, run:
	- `PYTHONPATH=. python src/scrapers/[your_country]/[your_secondary]/main-prod.py --step [your_step]`
		- `[your_step]` should be either `upload` or `process`. Verify that generated files are placed into `./raw/...` and `./processed/...`
    - e.g.: `PYTHONPATH=. python src/scrapers/brazil/aneel/main-prod.py --step process`

### Running with Docker/DAGU/Minio
- From the base project directory, run:
	- `publish-single.sh [path_to_your_scraper]`
	- e.g.: `./publish-single.sh ./src/scrapers/brazil/aneel`
- The previous build step should generate several files:
	- a DAGU config file under `./dagu_config/dags/your-country_your-secondary.yaml`
	- a Docker container under the local repo. Verify with `docker images`.
- Initialize the DAGU/Docker registry/Minio instances. Run:
	- `docker compose up -d`
	- Verify in the Docker application (or whatever way you prefer) that the three services are running.
		- DAGU's GUI should be up on `http://localhost:8080/dags`
		- Minio's GUI should be up on `http://localhost:9090`. The user and pass are both "minioadmin".
- Run your scraper by selecting it in the DAGU GUI and clicking the triangle play button. Verify that it works with the various output messages and that there are properly formatted files in the Minio GUI. 

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


### Running the entire set of scrapers 
**NOTE**: as of 11/24/25 I have no idea if this works

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


## Resources

https://docs.dagu.cloud/reference/yaml

<https://github.com/dagu-org/dagu>

<https://github.com/minio/minio>


## Last Updated
11/24/25