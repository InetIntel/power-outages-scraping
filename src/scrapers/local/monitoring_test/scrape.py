import json
import os
import sys
import time
from pathlib import Path

mode = json.loads(os.environ.get("SCRAPER_PARAMS", "{}")).get("mode", "success")
data_dir = Path(os.environ.get("DATA_DIR", "/data"))
output_dir = data_dir / "local" / "monitoring_test"
output_dir.mkdir(parents=True, exist_ok=True)

print(f"Running monitoring test in mode: {mode}")

if mode == "crash":
    raise RuntimeError("Intentional test scraper failure")

if mode == "timeout":
    time.sleep(300)

if mode == "empty":
    (output_dir / "raw.json").write_text("[]")
    sys.exit(0)

if mode == "invalid":
    (output_dir / "raw.json").write_text("<html>upstream error</html>")
    sys.exit(0)

(output_dir / "raw.json").write_text(
    json.dumps(
        [
            {
                "provider": "monitoring-test",
                "outages": 1,
                "status": "ok",
            }
        ]
    )
)

print("Test scraper completed successfully")
