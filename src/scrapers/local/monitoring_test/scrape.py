from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


params = json.loads(os.environ.get("SCRAPER_PARAMS", "{}"))
mode = params.get("mode", "success")

data_dir = Path(os.environ.get("DATA_DIR", "/data"))
output_dir = data_dir / "local" / "monitoring_test"
output_dir.mkdir(parents=True, exist_ok=True)

incident_started_path = output_dir / "timed_incident_started_at.txt"
incident_completed_path = output_dir / "timed_incident_completed_at.txt"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


if mode == "timed_recovery":
    failure_minutes = int(params.get("failure_minutes", 30))
    now = utc_now()

    # Once this simulated incident has recovered, later scheduled runs stay healthy.
    if incident_completed_path.exists():
        mode = "success"
    else:
        if not incident_started_path.exists():
            incident_started_path.write_text(now.isoformat())

        try:
            started_at = datetime.fromisoformat(
                incident_started_path.read_text().strip()
            )
        except ValueError:
            started_at = now
            incident_started_path.write_text(started_at.isoformat())

        recover_at = started_at + timedelta(minutes=failure_minutes)

        if now < recover_at:
            remaining_seconds = max(
                0,
                int((recover_at - now).total_seconds()),
            )
            remaining_minutes = max(
                1,
                (remaining_seconds + 59) // 60,
            )

            raise RuntimeError(
                "Simulated upstream outage. "
                f"Automatic recovery in approximately "
                f"{remaining_minutes} minute(s)."
            )

        incident_completed_path.write_text(now.isoformat())
        incident_started_path.unlink(missing_ok=True)
        mode = "success"

else:
    # Changing to another mode resets the timed demo.
    incident_started_path.unlink(missing_ok=True)
    incident_completed_path.unlink(missing_ok=True)


if mode == "crash":
    raise RuntimeError("Intentional test scraper failure")

if mode == "timeout":
    sleep_seconds = int(params.get("sleep_seconds", 120))
    print(f"Sleeping for {sleep_seconds} seconds")
    time.sleep(sleep_seconds)

if mode == "empty":
    (output_dir / "raw.json").write_text("[]")
    sys.exit(0)

if mode == "invalid":
    (output_dir / "raw.json").write_text(
        "<html>upstream error</html>"
    )
    sys.exit(0)

(output_dir / "raw.json").write_text(
    json.dumps(
        [
            {
                "provider": "monitoring-test",
                "outages": 1,
                "status": "ok",
                "checked_at": utc_now().isoformat(),
            }
        ]
    )
)

print("Test scraper completed successfully")
