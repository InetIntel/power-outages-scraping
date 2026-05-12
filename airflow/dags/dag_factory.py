from __future__ import annotations
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
import yaml
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.sdk import Asset
from docker.types import Mount

log = logging.getLogger(__name__)

REGISTRY_PATH = Path(__file__).parent.parent / "config" / "scraper_registry.yaml"
LOCAL_REGISTRY = os.environ.get("SCRAPER_REGISTRY", "localhost:5000")
DOCKER_NETWORK = os.environ.get(
    "SCRAPER_DOCKER_NETWORK", "power-outages-scraping-main_default"
)
DATA_VOLUME = os.environ.get("SCRAPER_DATA_VOLUME", "santandrea-power-outages")
DATA_MOUNT_PATH = "/data"


def load_registry() -> dict:
    with open(REGISTRY_PATH) as f:
        return yaml.safe_load(f)


def _asset_for(scraper_id: str) -> Asset:
    return Asset(f"scraper://{scraper_id}")


def _docker_task(
    *,
    task_id: str,
    image: str,
    command: str,
    environment: dict,
    timeout: int,
    outlets: list | None = None,
) -> DockerOperator:
    return DockerOperator(
        task_id=task_id,
        image=image,
        command=command,
        environment={**environment, "DATA_DIR": DATA_MOUNT_PATH},
        network_mode=DOCKER_NETWORK,
        force_pull=True,
        auto_remove="force",
        execution_timeout=timedelta(minutes=timeout),
        tty=False,
        mount_tmp_dir=False,
        docker_url="unix://var/run/docker.sock",
        outlets=outlets or [],
        mounts=[
            Mount(
                target=DATA_MOUNT_PATH,
                source=DATA_VOLUME,
                type="volume",
            ),
        ],
    )


def _build_dag(entry: dict, defaults: dict) -> DAG:
    scraper_id: str = entry["scraper_id"]
    description: str = entry.get("description", f"Scraper: {scraper_id}")
    tags: list = entry.get("tags", []) + ["scraper"]
    retries: int = entry.get("retries", defaults.get("retries", 2))
    retry_delay: int = entry.get(
        "retry_delay_minutes", defaults.get("retry_delay_minutes", 5)
    )
    timeout: int = entry.get("timeout_minutes", defaults.get("timeout_minutes", 60))
    owner: str = entry.get("owner", defaults.get("owner", "data-team"))
    params: dict = entry.get("params", {})
    depends_on: list = entry.get("depends_on", [])

    if depends_on:
        schedule: str | list = [_asset_for(dep) for dep in depends_on]
        schedule_doc = "Triggered by upstream: " + ", ".join(depends_on)
    else:
        if "schedule" not in entry:
            raise ValueError(
                f"{scraper_id}: must specify either `schedule` or `depends_on`"
            )
        schedule = entry["schedule"]
        schedule_doc = f"`{schedule}`"

    image: str = entry.get("image", f"{LOCAL_REGISTRY}/{scraper_id}:latest")

    shared_env = {
        "SCRAPER_PARAMS": json.dumps(params),
        "SCRAPER_ID": scraper_id,
    }

    default_args = {
        "owner": owner,
        "retries": retries,
        "retry_delay": timedelta(minutes=retry_delay),
        "depends_on_past": False,
    }

    dag = DAG(
        dag_id=scraper_id,
        description=description,
        schedule=schedule,
        start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
        catchup=False,
        tags=tags,
        default_args=default_args,
        doc_md=f"""
## {scraper_id}

| | |
|---|---|
| **Image** | `{image}` |
| **Schedule** | {schedule_doc} |
| **Description** | {description} |

### Task graph
```
scrape  ->  post_process
```

### Params
```json
{json.dumps(params, indent=2)}
```

### Rebuild image
```bash
# Rebuild just this scraper
docker build -t {image} -f src/scrapers/{scraper_id.replace("_", "/", 1)}/Dockerfile .
docker push {image}

# Or rebuild everything
./publish.sh
```
        """,
    )

    with dag:
        scrape = _docker_task(
            task_id="scrape",
            image=image,
            command="python scrape.py",
            environment=shared_env,
            timeout=timeout,
        )

        post_process = _docker_task(
            task_id="post_process",
            image=image,
            command="python post_process.py",
            environment=shared_env,
            timeout=timeout,
            outlets=[_asset_for(scraper_id)],
        )

        scrape >> post_process

    return dag


def _load_all_dags() -> dict[str, DAG]:
    registry = load_registry()
    defaults = registry.get("defaults", {})
    dags: dict[str, DAG] = {}

    for entry in registry.get("scrapers", []):
        if not entry.get("enabled", True):
            log.info("Skipping disabled scraper: %s", entry.get("scraper_id"))
            continue
        try:
            dag = _build_dag(entry, defaults)
            dags[dag.dag_id] = dag
            log.info("Registered DAG: %s", dag.dag_id)
        except Exception as exc:
            log.error("Failed to build DAG for %s: %s", entry.get("scraper_id"), exc)

    return dags


globals().update(_load_all_dags())
