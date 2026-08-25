import json
import os
from pathlib import Path

data_dir = Path(os.environ.get("DATA_DIR", "/data"))
output_dir = data_dir / "local" / "monitoring_test"

raw_path = output_dir / "raw.json"
processed_path = output_dir / "processed.json"

data = json.loads(raw_path.read_text())
processed_path.write_text(json.dumps(data, indent=2))

print(f"Processed {len(data)} records")
