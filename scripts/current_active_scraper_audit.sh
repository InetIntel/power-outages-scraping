#!/usr/bin/env bash
set -euo pipefail

STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="_doc_discovery_output/current_scraper_audit_${STAMP}"
REPORT="$OUT_DIR/current_active_scraper_audit.md"
ZIP="$OUT_DIR.zip"

mkdir -p "$OUT_DIR"
: > "$REPORT"

section() {
  echo "" >> "$REPORT"
  echo "## $1" >> "$REPORT"
  echo "" >> "$REPORT"
}

cmd_block() {
  local title="$1"
  shift
  section "$title"
  echo '```text' >> "$REPORT"
  echo "$ $*" >> "$REPORT"
  "$@" 2>&1 | sed -E 's/(password|secret|token|api[_-]?key|aws_access_key_id|aws_secret_access_key)[^[:space:]]*/REDACTED/Ig' >> "$REPORT" || true
  echo '```' >> "$REPORT"
}

cat >> "$REPORT" <<HEADER
# Current Main Active Scraper Audit

Purpose: discovery only.

Goals:
- Inventory active/current scraper evidence on main.
- Identify missing Dockerfiles, requirements, notes, docs, or obvious stubs.
- Detect stale DAGU/MinIO references.
- Identify which scrapers deserve deeper review.
- Do not fix code in this pass.

Generated: $(date)
Repo path: $(pwd)
HEADER

cmd_block "Git status" git status --short
cmd_block "Current branch and recent commits" git log --oneline --decorate -n 15
cmd_block "Top-level repo files" find . -maxdepth 2 -type f -not -path './.git/*' | sort
cmd_block "Docker Compose services" docker compose config --services
cmd_block "Airflow files" find airflow -maxdepth 5 -type f 2>/dev/null | sort
cmd_block "Registry/config files" find airflow config . -maxdepth 5 \( -iname '*registry*' -o -iname '*.yaml' -o -iname '*.yml' \) 2>/dev/null | sort
cmd_block "Scraper directories" find src/scrapers -maxdepth 4 -type d 2>/dev/null | sort

section "Scraper folder inventory"
python3 - <<'PY' >> "$REPORT"
from pathlib import Path

base = Path("src/scrapers")
print("| Scraper Path | Python Files | Dockerfile | requirements.txt | notes.md | README |")
print("|---|---:|---|---|---|---|")

if not base.exists():
    print("| `src/scrapers` missing | 0 | no | no | no | no |")
    raise SystemExit

dirs = []
for d in sorted(base.rglob("*")):
    if not d.is_dir():
        continue
    files = list(d.iterdir())
    has_relevant = (
        any(f.suffix == ".py" for f in files if f.is_file())
        or (d / "Dockerfile").exists()
        or (d / "requirements.txt").exists()
        or (d / "notes.md").exists()
        or (d / "README.md").exists()
    )
    if has_relevant:
        dirs.append(d)

for d in dirs:
    py_count = len([f for f in d.glob("*.py")])
    docker = "yes" if (d / "Dockerfile").exists() else "no"
    req = "yes" if (d / "requirements.txt").exists() else "no"
    notes = "yes" if (d / "notes.md").exists() else "no"
    readme = "yes" if (d / "README.md").exists() else "no"
    print(f"| `{d}` | {py_count} | {docker} | {req} | {notes} | {readme} |")
PY

section "Registry content, redacted"
echo '```yaml' >> "$REPORT"
if [ -f airflow/config/scraper_registry.yaml ]; then
  sed -E 's/(password|secret|token|api[_-]?key|aws_access_key_id|aws_secret_access_key):.*/\1: REDACTED/Ig' airflow/config/scraper_registry.yaml >> "$REPORT"
else
  echo "airflow/config/scraper_registry.yaml not found"
fi
echo '```' >> "$REPORT"

section "Registry parse attempt"
echo '```text' >> "$REPORT"
python3 - <<'PY' >> "$REPORT" 2>&1 || true
from pathlib import Path
import sys, json

path = Path("airflow/config/scraper_registry.yaml")
if not path.exists():
    print("Registry file not found.")
    raise SystemExit

try:
    import yaml
except Exception as e:
    print(f"PyYAML unavailable; raw registry was already captured. Error: {e}")
    raise SystemExit

data = yaml.safe_load(path.read_text()) or {}

def walk(obj, trail=""):
    if isinstance(obj, dict):
        keys = set(obj.keys())
        interesting = {"enabled", "schedule", "image", "dockerfile", "path", "country", "provider", "name", "scraper", "retries"}
        if keys & interesting:
            print(f"\n[{trail or 'root'}]")
            for k in sorted(keys & interesting):
                print(f"{k}: {obj.get(k)}")
        for k, v in obj.items():
            walk(v, f"{trail}.{k}" if trail else str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk(v, f"{trail}[{i}]")

walk(data)
PY
echo '```' >> "$REPORT"

cmd_block "Missing or empty requirements files" bash -lc '
find src/scrapers -type d 2>/dev/null | while read -r d; do
  if find "$d" -maxdepth 1 -type f -name "*.py" | grep -q .; then
    if [ ! -f "$d/requirements.txt" ]; then
      echo "MISSING requirements.txt: $d"
    elif [ ! -s "$d/requirements.txt" ]; then
      echo "EMPTY requirements.txt: $d/requirements.txt"
    fi
  fi
done | sort
'

cmd_block "Missing Dockerfiles in scraper folders with Python files" bash -lc '
find src/scrapers -type d 2>/dev/null | while read -r d; do
  if find "$d" -maxdepth 1 -type f -name "*.py" | grep -q .; then
    if [ ! -f "$d/Dockerfile" ]; then
      echo "MISSING Dockerfile: $d"
    fi
  fi
done | sort
'

cmd_block "Missing notes.md in scraper folders with Python files" bash -lc '
find src/scrapers -type d 2>/dev/null | while read -r d; do
  if find "$d" -maxdepth 1 -type f -name "*.py" | grep -q .; then
    if [ ! -f "$d/notes.md" ]; then
      echo "MISSING notes.md: $d"
    fi
  fi
done | sort
'

cmd_block "Potential stale DAGU or MinIO references" bash -lc '
grep -RInE "DAGU|dagu|MinIO|minio|host.docker.internal|minioadmin|dagu_config" \
  . \
  --exclude-dir=.git \
  --exclude-dir=_doc_discovery_output \
  --exclude-dir=raw \
  --exclude-dir=processed \
  2>/dev/null \
  | sed -E "s/(password|secret|token|api[_-]?key|aws_access_key_id|aws_secret_access_key)[^[:space:]]*/REDACTED/Ig" \
  | head -n 500
'

cmd_block "Potential stubs, TODOs, debug residue" bash -lc '
grep -RInE "TODO|TBD|FIXME|pass$|NotImplemented|print\\(.*\\?\\?\\?|foolishness|stub|placeholder|dummy|example" \
  src airflow docker-compose.yml README.md 2>/dev/null \
  | sed -E "s/(password|secret|token|api[_-]?key|aws_access_key_id|aws_secret_access_key)[^[:space:]]*/REDACTED/Ig" \
  | head -n 500
'

cmd_block "Potential risky network/security patterns" bash -lc '
grep -RInE "verify=False|http://|aws_access_key_id|aws_secret_access_key|minioadmin|password|secret|token|api_key|hardcoded|403|Forbidden" \
  src airflow utils docker-compose.yml 2>/dev/null \
  | sed -E "s/(password|secret|token|api[_-]?key|aws_access_key_id|aws_secret_access_key)[^[:space:]]*/REDACTED/Ig" \
  | head -n 500
'

cmd_block "Python syntax check for scraper and airflow Python files" bash -lc '
find src/scrapers airflow -type f -name "*.py" 2>/dev/null | sort | while read -r f; do
  echo "--- $f"
  python3 -m py_compile "$f" 2>&1 || true
done
'

section "Suggested reviewer classification template"
cat >> "$REPORT" <<'TEMPLATE'
Use this section after reviewing the output:

| Area | Status | Notes |
|---|---|---|
| Active registry | PASS / PARTIAL / FAIL / UNKNOWN | |
| Docker Compose currentness | PASS / PARTIAL / FAIL / UNKNOWN | |
| Scraper Dockerfiles | PASS / PARTIAL / FAIL / UNKNOWN | |
| Scraper requirements | PASS / PARTIAL / FAIL / UNKNOWN | |
| Scraper notes/docs | PASS / PARTIAL / FAIL / UNKNOWN | |
| DAGU/legacy references | PASS / PARTIAL / FAIL / UNKNOWN | |
| Static code risks | PASS / PARTIAL / FAIL / UNKNOWN | |
| Recommended deep dives | List only | |
TEMPLATE

zip -r "$ZIP" "$OUT_DIR" >/dev/null

echo "Created:"
echo "  $REPORT"
echo "  $ZIP"
