#!/usr/bin/env bash
set -euo pipefail

STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="_doc_discovery_output/current_scraper_audit_no_logs_${STAMP}"
REPORT="$OUT_DIR/current_scraper_audit_no_logs.md"
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
  "$@" 2>&1 \
    | sed -E 's/(password|secret|token|api[_-]?key|aws_access_key_id|aws_secret_access_key)[^[:space:]]*/REDACTED/Ig' \
    >> "$REPORT" || true
  echo '```' >> "$REPORT"
}

cat >> "$REPORT" <<HEADER
# Current Main Scraper Audit — No Logs

Purpose: discovery only.

This scan excludes noisy runtime/log/output directories:
- airflow/logs
- _doc_discovery_output
- raw
- processed
- registry_data
- minio_data
- old_misc
- .git

Generated: $(date)
Repo path: $(pwd)
HEADER

cmd_block "Git status" git status --short
cmd_block "Current branch and recent commits" git log --oneline --decorate -n 15
cmd_block "Docker Compose services" docker compose config --services
cmd_block "Airflow current files excluding logs" bash -lc '
find airflow \
  -path "airflow/logs" -prune -o \
  -type f -print 2>/dev/null | sort
'

section "Scraper folder inventory"
python3 - <<'PY' >> "$REPORT"
from pathlib import Path

base = Path("src/scrapers")
print("| Scraper Path | Python Files | Dockerfile | requirements.txt | notes.md | README |")
print("|---|---:|---|---|---|---|")

if not base.exists():
    print("| `src/scrapers` missing | 0 | no | no | no | no |")
    raise SystemExit

for d in sorted(base.rglob("*")):
    if not d.is_dir():
        continue
    files = [f for f in d.iterdir() if f.is_file()]
    has_relevant = (
        any(f.suffix == ".py" for f in files)
        or (d / "Dockerfile").exists()
        or (d / "requirements.txt").exists()
        or (d / "notes.md").exists()
        or (d / "README.md").exists()
    )
    if not has_relevant:
        continue

    py_count = len([f for f in d.glob("*.py")])
    docker = "yes" if (d / "Dockerfile").exists() else "no"
    req = "yes" if (d / "requirements.txt").exists() else "no"
    notes = "yes" if (d / "notes.md").exists() else "no"
    readme = "yes" if (d / "README.md").exists() else "no"
    print(f"| `{d}` | {py_count} | {docker} | {req} | {notes} | {readme} |")
PY

section "Registry content"
echo '```yaml' >> "$REPORT"
if [ -f airflow/config/scraper_registry.yaml ]; then
  sed -E 's/(password|secret|token|api[_-]?key|aws_access_key_id|aws_secret_access_key):.*/\1: REDACTED/Ig' airflow/config/scraper_registry.yaml >> "$REPORT"
else
  echo "airflow/config/scraper_registry.yaml not found"
fi
echo '```' >> "$REPORT"

section "Registry to folder consistency check"
python3 - <<'PY' >> "$REPORT" 2>&1 || true
from pathlib import Path
import re

registry = Path("airflow/config/scraper_registry.yaml")
scraper_root = Path("src/scrapers")

print("| Registry line | Module/Path value | Expected folder guess | Exists exact | Case-insensitive matches |")
print("|---:|---|---|---|---|")

if not registry.exists():
    print("| - | registry missing | - | - | - |")
    raise SystemExit

text = registry.read_text()
values = []

for i, line in enumerate(text.splitlines(), start=1):
    m = re.search(r'^\s*(module|path|scraper_path)\s*:\s*["' "'" r']?([^"'" "'" r'\s#]+)', line)
    if m:
        key, value = m.group(1), m.group(2)
        values.append((i, key, value))

all_dirs = [p for p in scraper_root.rglob("*") if p.is_dir()] if scraper_root.exists() else []

for line_no, key, value in values:
    guess = value
    if key == "module":
        parts = value.split(".")
        if parts and parts[0] == "scrapers":
            parts = parts[1:]
        guess = "src/scrapers/" + "/".join(parts)
    elif not value.startswith("src/"):
        guess = "src/scrapers/" + value.strip("./")

    guess_path = Path(guess)
    exists = "yes" if guess_path.exists() else "no"
    ci_matches = [str(p) for p in all_dirs if str(p).lower() == str(guess_path).lower()]
    ci = ", ".join(ci_matches[:5]) if ci_matches else ""
    print(f"| {line_no} | `{key}: {value}` | `{guess}` | {exists} | `{ci}` |")
PY

cmd_block "Missing or empty requirements files" bash -lc '
find src/scrapers \
  -path "*/__pycache__" -prune -o \
  -type d -print 2>/dev/null | while read -r d; do
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
find src/scrapers \
  -path "*/__pycache__" -prune -o \
  -type d -print 2>/dev/null | while read -r d; do
    if find "$d" -maxdepth 1 -type f -name "*.py" | grep -q .; then
      if [ ! -f "$d/Dockerfile" ]; then
        echo "MISSING Dockerfile: $d"
      fi
    fi
  done | sort
'

cmd_block "Missing notes.md in scraper folders with Python files" bash -lc '
find src/scrapers \
  -path "*/__pycache__" -prune -o \
  -type d -print 2>/dev/null | while read -r d; do
    if find "$d" -maxdepth 1 -type f -name "*.py" | grep -q .; then
      if [ ! -f "$d/notes.md" ]; then
        echo "MISSING notes.md: $d"
      fi
    fi
  done | sort
'

cmd_block "Potential stale DAGU or MinIO references excluding logs/output" bash -lc '
grep -RInE "DAGU|dagu|MinIO|minio|host.docker.internal|minioadmin|dagu_config" \
  . \
  --exclude-dir=.git \
  --exclude-dir=_doc_discovery_output \
  --exclude-dir=airflow/logs \
  --exclude-dir=raw \
  --exclude-dir=processed \
  --exclude-dir=registry_data \
  --exclude-dir=minio_data \
  --exclude-dir=old_misc \
  2>/dev/null \
  | sed -E "s/(password|secret|token|api[_-]?key|aws_access_key_id|aws_secret_access_key)[^[:space:]]*/REDACTED/Ig" \
  | head -n 500
'

cmd_block "Potential stubs, TODOs, debug residue excluding logs/output" bash -lc '
grep -RInE "TODO|TBD|FIXME|pass$|NotImplemented|print\\(.*\\?\\?\\?|foolishness|stub|placeholder|dummy|example" \
  src airflow docker-compose.yml README.md \
  --exclude-dir=airflow/logs \
  --exclude-dir=old_misc \
  2>/dev/null \
  | sed -E "s/(password|secret|token|api[_-]?key|aws_access_key_id|aws_secret_access_key)[^[:space:]]*/REDACTED/Ig" \
  | head -n 500
'

cmd_block "Potential risky network/security patterns excluding logs/output" bash -lc '
grep -RInE "verify=False|http://|aws_access_key_id|aws_secret_access_key|minioadmin|password|secret|token|api_key|hardcoded|403|Forbidden" \
  src airflow utils docker-compose.yml \
  --exclude-dir=airflow/logs \
  --exclude-dir=old_misc \
  2>/dev/null \
  | sed -E "s/(password|secret|token|api[_-]?key|aws_access_key_id|aws_secret_access_key)[^[:space:]]*/REDACTED/Ig" \
  | head -n 500
'

cmd_block "Python syntax check excluding logs/output" bash -lc '
find src/scrapers airflow \
  -path "airflow/logs" -prune -o \
  -path "*/__pycache__" -prune -o \
  -type f -name "*.py" -print 2>/dev/null \
  | sort \
  | while read -r f; do
      echo "--- $f"
      python3 -m py_compile "$f" 2>&1 || true
    done
'

section "Recommended review questions"
cat >> "$REPORT" <<'TEMPLATE'
- Which active registry entries point to folders that do not exist exactly?
- Which mismatches only work on case-insensitive filesystems?
- Are Dockerfiles expected to be committed or generated from templates?
- Which active scrapers lack `notes.md` and should be documented first?
- Which `verify=False` usages are intentional provider exceptions?
- Which TODO/debug findings affect active scrapers?
TEMPLATE

zip -r "$ZIP" "$OUT_DIR" >/dev/null

echo "Created:"
echo "  $REPORT"
echo "  $ZIP"
