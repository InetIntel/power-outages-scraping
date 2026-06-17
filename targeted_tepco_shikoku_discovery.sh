#!/usr/bin/env bash
set -uo pipefail

PROJECT="${PROJECT:-power-outages-scraping-main}"
VOLUME="${VOLUME:-santandrea-power-outages}"
WAIT_SECONDS="${WAIT_SECONDS:-60}"
STAMP="$(date +"%Y%m%d_%H%M%S")"
RUN_DIR="${RUN_DIR:-_doc_discovery_output/targeted_tepco_shikoku_${STAMP}}"
mkdir -p "$RUN_DIR"

log() {
  echo
  echo "============================================================"
  echo "$1"
  echo "============================================================"
}

run_capture() {
  local name="$1"
  shift
  {
    echo "## $name"
    date
    echo
    "$@"
  } > "$RUN_DIR/$name.txt" 2>&1
}

capture_shell() {
  local name="$1"
  local script="$2"
  {
    echo "## $name"
    date
    echo
    bash -lc "$script"
  } > "$RUN_DIR/$name.txt" 2>&1
}

capture_container_shell() {
  local name="$1"
  local script="$2"
  {
    echo "## $name"
    date
    echo
    docker compose -p "$PROJECT" exec -T airflow-scheduler bash -lc "$script"
  } > "$RUN_DIR/$name.txt" 2>&1
}

capture_volume_shell() {
  local name="$1"
  local script="$2"
  {
    echo "## $name"
    date
    echo
    docker run --rm -v "$VOLUME:/data" alpine sh -lc "$script"
  } > "$RUN_DIR/$name.txt" 2>&1
}

provider_static_review() {
  local provider="$1"
  local id="japan_${provider}"
  local path="src/scrapers/japan/${provider}"

  capture_shell "${id}_01_static_file_inventory" "
    echo '--- scraper path ---'
    ls -lah '${path}' || true
    echo
    echo '--- files ---'
    find '${path}' -maxdepth 2 -type f -print | sort || true
    echo
    echo '--- requirements ---'
    [ -f '${path}/requirements.txt' ] && cat '${path}/requirements.txt' || true
  "

  capture_shell "${id}_02_static_url_and_path_grep" "
    echo '--- URL / provider / path keywords ---'
    grep -RInE 'https?://|okiden|shikoku|tepco|rikuden|kansai|kyushu|tohoku|hepc|chugoku|/data|processed|raw|upload|Uploader|download|glob|\.xml|\.json|\.html|\.csv|User-Agent|headers|requests|get\(' '${path}' || true
    echo
    echo '--- first 220 lines of scrape.py ---'
    [ -f '${path}/scrape.py' ] && sed -n '1,220p' '${path}/scrape.py' || true
    echo
    echo '--- first 260 lines of post_process.py ---'
    [ -f '${path}/post_process.py' ] && sed -n '1,260p' '${path}/post_process.py' || true
  "
}

trigger_provider() {
  local provider="$1"
  local id="japan_${provider}"
  local path="./src/scrapers/japan/${provider}"

  capture_shell "${id}_03_build" "./publish-single.sh '${path}'"

  capture_shell "${id}_04_trigger" "
    docker compose -p '${PROJECT}' exec -T airflow-scheduler /entrypoint airflow dags unpause '${id}' || true
    docker compose -p '${PROJECT}' exec -T airflow-scheduler /entrypoint airflow dags trigger '${id}'
  "

  capture_shell "${id}_05_wait" "echo 'Waiting ${WAIT_SECONDS}s'; sleep '${WAIT_SECONDS}'"
}

capture_runtime_evidence() {
  local provider="$1"
  local id="japan_${provider}"

  capture_container_shell "${id}_06_dag_runs" "/entrypoint airflow dags list-runs '${id}' || true"

  capture_container_shell "${id}_07_logs_full_tail" \
    "find /opt/airflow/logs/dag_id=${id} -type f | sort | xargs -r -n1 sh -c 'echo ===== \\\$0 =====; tail -260 \\\$0'"

  capture_container_shell "${id}_08_logs_signal_summary" \
    "find /opt/airflow/logs/dag_id=${id} -type f | sort | xargs -r grep -Ei 'Fetching|Fetched|Saved|Uploaded|Downloaded|Processed|Extracted|total|403|Forbidden|404|Not Found|empty|No outage|Traceback|Exception|Error|Failed|okiden|Okinawa|Shikoku|TEPCO|tepco' || true"

  capture_volume_shell "${id}_09_volume_files" \
    "find /data/japan -path '*${provider}*' -type f -exec ls -lh {} \\; | sort"

  capture_volume_shell "${id}_10_raw_preview" \
    "find /data/japan -path '*${provider}*raw*' -type f | sort | xargs -r -n1 sh -c 'echo ===== \\\$0 =====; wc -c \\\$0; head -c 1500 \\\$0; echo; echo'"

  capture_volume_shell "${id}_11_processed_preview" \
    "find /data/japan -path '*${provider}*processed*' -type f | sort | xargs -r -n1 sh -c 'echo ===== \\\$0 =====; wc -c \\\$0; head -c 1500 \\\$0; echo; echo'"
}

tepco_network_probe() {
  capture_shell "japan_tepco_12_host_network_probe" "
    urls=(
      'https://teideninfo.tepco.co.jp/day/teiden/index-j.xml'
      'https://teideninfo.tepco.co.jp/day/teiden/day001-j.xml'
      'https://teideninfo.tepco.co.jp/'
    )
    for url in \"\${urls[@]}\"; do
      echo '===== default curl:' \"\$url\" '====='
      curl -I -L --max-time 20 \"\$url\" || true
      echo
      echo '===== browser-like UA:' \"\$url\" '====='
      curl -I -L --max-time 20 \
        -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36' \
        -H 'Accept: application/xml,text/xml,text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8' \
        -H 'Accept-Language: ja,en-US;q=0.9,en;q=0.8' \
        -H 'Referer: https://teideninfo.tepco.co.jp/' \
        \"\$url\" || true
      echo
    done
  "

  capture_container_shell "japan_tepco_13_airflow_container_network_probe" "
    python - <<'PY'
import urllib.request
urls = [
    'https://teideninfo.tepco.co.jp/day/teiden/index-j.xml',
    'https://teideninfo.tepco.co.jp/day/teiden/day001-j.xml',
    'https://teideninfo.tepco.co.jp/',
]
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36',
    'Accept': 'application/xml,text/xml,text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
    'Referer': 'https://teideninfo.tepco.co.jp/',
}
for url in urls:
    print('===== default urllib:', url, '=====')
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            print('status', r.status, 'content-type', r.headers.get('content-type'), 'bytes-preview', len(r.read(300)))
    except Exception as e:
        print(type(e).__name__, e)
    print('===== browser-like urllib:', url, '=====')
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read(300)
            print('status', r.status, 'content-type', r.headers.get('content-type'), 'bytes-preview', len(data))
            print(data[:300])
    except Exception as e:
        print(type(e).__name__, e)
PY
  "
}

shikoku_cross_check() {
  capture_shell "japan_shikoku_12_compare_with_okinawa_static" "
    echo '--- shikoku vs okinawa filenames ---'
    find src/scrapers/japan/shikoku src/scrapers/japan/okinawa -maxdepth 2 -type f -print | sort || true
    echo
    echo '--- grep okiden across shikoku and okinawa ---'
    grep -RInE 'okiden|OKIDEN|okinawa|Okinawa|history_normal|bosai/xml|shikoku|Shikoku' src/scrapers/japan/shikoku src/scrapers/japan/okinawa || true
    echo
    echo '--- rough diff of scrape.py if available ---'
    if [ -f src/scrapers/japan/shikoku/scrape.py ] && [ -f src/scrapers/japan/okinawa/scrape.py ]; then
      diff -u src/scrapers/japan/okinawa/scrape.py src/scrapers/japan/shikoku/scrape.py || true
    fi
    echo
    echo '--- rough diff of post_process.py if available ---'
    if [ -f src/scrapers/japan/shikoku/post_process.py ] && [ -f src/scrapers/japan/okinawa/post_process.py ]; then
      diff -u src/scrapers/japan/okinawa/post_process.py src/scrapers/japan/shikoku/post_process.py || true
    fi
  "
}

summarize() {
  {
    echo "## Targeted TEPCO + Shikoku discovery summary"
    date
    echo
    echo "Run dir: $RUN_DIR"
    echo
    echo "### Evidence files"
    find "$RUN_DIR" -maxdepth 1 -type f -print | sort
    echo
    echo "### Initial interpretation checklist"
    echo "TEPCO: check for 403/Forbidden, raw output absence, processed [] size 2, and whether browser-like headers change source access."
    echo "Shikoku: check for OKIDEN/Okinawa endpoints, okiden_* raw XML under shikoku path, no processed output, and diff/static similarity to Okinawa scraper."
  } > "$RUN_DIR/99_targeted_discovery_summary.md"

  if command -v zip >/dev/null 2>&1; then
    zip -r "${RUN_DIR}.zip" "$RUN_DIR" >/dev/null
    echo "Created evidence bundle: ${RUN_DIR}.zip"
  fi
}

main() {
  log "Targeted discovery: TEPCO + Shikoku"
  echo "PROJECT=$PROJECT"
  echo "VOLUME=$VOLUME"
  echo "WAIT_SECONDS=$WAIT_SECONDS"
  echo "RUN_DIR=$RUN_DIR"

  provider_static_review tepco
  provider_static_review shikoku

  trigger_provider tepco
  capture_runtime_evidence tepco
  tepco_network_probe

  trigger_provider shikoku
  capture_runtime_evidence shikoku
  shikoku_cross_check

  summarize
  echo "Done. Summary: $RUN_DIR/99_targeted_discovery_summary.md"
}

main "$@"
