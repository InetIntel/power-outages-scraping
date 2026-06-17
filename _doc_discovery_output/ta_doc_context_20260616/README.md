# Power Outage Data Scraping

## Overview

This repo scrapes power outage data from utility providers around the world. Each scraper runs as a Docker container, orchestrated by Airflow.

- **Scrapers** - Python (`scrape.py` + `post_process.py`) under `src/scrapers/<country>/<provider>/`.
- **Docker** - each scraper is built into its own image and pushed to a local registry.
- **Airflow** - DAGs are generated dynamically from `airflow/config/scraper_registry.yaml`.
- **Postgres** - Airflow metadata DB.
- **Shared volume** - scraped data is written to the external `santandrea-power-outages` Docker volume.

## Requirements

- Docker + Docker Compose
- Bash (for `publish.sh` / `publish-single.sh`)
- A `.env` at the repo root with:
  ```
  AIRFLOW_UID=0
  AIRFLOW_JWT_SECRET=<random-string>
  AIRFLOW_FERNET_KEY=<fernet-key>
  ```
- The shared data volume must exist once: `docker volume create santandrea-power-outages`

## Deploying

Bring up the full stack (registry, Postgres, Airflow webserver/scheduler/dag-processor) and build + push every scraper image:

```bash
make deploy
```

This runs `docker compose up -d` followed by `./publish.sh`, which auto-detects every `scrape.py` under `src/scrapers/` and builds an image named `localhost:5000/<country>_<provider>:latest`.

To stop everything:

```bash
make stop
```

Useful URLs once running:

- Airflow UI: <http://localhost:8080> (default login `admin` / `admin`)
- Registry catalog: <http://localhost:5000/v2/_catalog>

## Adding a scraper

1. Create the scraper directory under `src/scrapers/<country>/<provider>/` containing:
   - `scrape.py` - fetches raw data, writes to `$DATA_DIR` (mounted at `/data`).
   - `post_process.py` - transforms/validates the raw data.
   - `requirements.txt` - Python deps. If `selenium` is listed, `Dockerfile.selenium` is used automatically; otherwise `Dockerfile.template`.
2. Build and push just this scraper:
   ```bash
   ./publish-single.sh ./src/scrapers/<country>/<provider>
   ```
   The image will be tagged `localhost:5000/<country>_<provider>:latest`.
3. Register the scraper by adding an entry to `airflow/config/scraper_registry.yaml`:
   ```yaml
   - scraper_id: <country>_<provider>     # must match the image name
     module: <country>.<provider>
     schedule: "0 6 * * *"                # cron, OR omit and use depends_on
     tags: [<country>, <region>]
   ```
   Optional fields: `description`, `retries`, `retry_delay_minutes`, `timeout_minutes`, `params`, `depends_on: [<other_scraper_id>]`, `enabled: false`, `image: <custom>`.
4. Airflow's dag-processor picks up registry changes automatically - the new DAG appears in the UI within ~30s. No restart needed.

After any change to the Python files, rerun `./publish-single.sh <path>` to rebuild the image. DAG metadata changes only require editing the registry.

## Removing or disabling a scraper

- **Disable temporarily** - set `enabled: false` on its registry entry. The DAG disappears from Airflow on the next scan.
- **Remove permanently** - delete the entry from `airflow/config/scraper_registry.yaml` and (optionally) the `src/scrapers/<country>/<provider>/` directory. To clean up the image:
  ```bash
  curl -X DELETE http://localhost:5000/v2/<country>_<provider>/manifests/<digest>
  ```

## Running and debugging in Airflow

- Find the DAG by `scraper_id` in the Airflow UI and click the play button to trigger a manual run.
- Each DAG has two tasks: `scrape` → `post_process`. Logs are per-task in the UI.
- To rerun only `post_process` after a successful `scrape`, clear just that task in the Grid view.
- After editing Python in a scraper, you must rebuild the image (`publish-single.sh`) before rerunning - Airflow pulls the image with `force_pull=True` on each run.

## Resources

- Airflow: <https://airflow.apache.org/docs/>
- Docker registry: <https://docs.docker.com/registry/>
