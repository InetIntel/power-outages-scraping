#!/usr/bin/env bash
set -uo pipefail

PROJECT="${PROJECT:-power-outages-scraping-main}"
VOLUME="${VOLUME:-santandrea-power-outages}"
WAIT_SECONDS="${WAIT_SECONDS:-45}"

STAMP="$(date +"%Y%m%d_%H%M%S")"
RUN_DIR="${RUN_DIR:-_doc_discovery_output/ta_japan_system_run_${STAMP}}"
mkdir -p "$RUN_DIR"

if [ "$#" -gt 0 ]; then
  PROVIDERS=("$@")
else
  PROVIDERS=(kyushu okinawa tepco tohoku shikoku)
fi

SUMMARY="$RUN_DIR/japan_validation_summary.tsv"

echo -e "provider\tbuild\ttrigger\tlogs\tdata_files\tprocessed_files\tstatus\tnotes" > "$SUMMARY"

log_section() {
  echo
  echo "============================================================"
  echo "$1"
  echo "============================================================"
}

safe_name() {
  echo "$1" | tr '/' '_'
}

capture_stack_status() {
  {
    echo "## Stack status"
    date
    echo
    docker compose -p "$PROJECT" ps || true
    echo
    echo "## Airflow health"
    curl -s http://localhost:8080/api/v2/monitor/health || true
    echo
    echo
    echo "## Japan DAGs"
    docker compose -p "$PROJECT" exec -T airflow-scheduler /entrypoint airflow dags list | grep japan || true
  } 2>&1 | tee "$RUN_DIR/00_stack_status.txt"
}

preflight() {
  {
    echo "## Preflight"
    date

    echo
    echo "--- docker version ---"
    docker version || exit 1

    echo
    echo "--- docker compose version ---"
    docker compose version || exit 1

    echo
    echo "--- port 5000 owner ---"
    sudo lsof -nP -iTCP:5000 -sTCP:LISTEN || true

    echo
    echo "--- port 8080 owner ---"
    sudo lsof -nP -iTCP:8080 -sTCP:LISTEN || true

    echo
    echo "--- volume ---"
    docker volume create "$VOLUME"

    echo
    echo "--- .env keys ---"
    if [ -f .env ]; then
      cut -d= -f1 .env
    else
      echo ".env missing"
    fi
  } 2>&1 | tee "$RUN_DIR/00_preflight.txt"
}

ensure_stack() {
  {
    echo "## Ensure stack is running"
    date

    docker compose -p "$PROJECT" up -d

    echo
    docker compose -p "$PROJECT" ps

    echo
    echo "--- health attempts ---"
    for i in $(seq 1 20); do
      echo "--- attempt $i ---"
      HEALTH="$(curl -s http://localhost:8080/api/v2/monitor/health || true)"
      echo "$HEALTH"
      echo "$HEALTH" | grep -q '"scheduler":{"status":"healthy"' && \
      echo "$HEALTH" | grep -q '"dag_processor":{"status":"healthy"' && \
      echo "$HEALTH" | grep -q '"metadatabase":{"status":"healthy"' && break
      sleep 3
    done
  } 2>&1 | tee "$RUN_DIR/00_ensure_stack.txt"
}

validate_provider() {
  provider="$1"
  scraper_id="japan_${provider}"
  scraper_path="./src/scrapers/japan/${provider}"
  prefix="$RUN_DIR/${scraper_id}"

  build_status="UNKNOWN"
  trigger_status="UNKNOWN"
  logs_status="UNKNOWN"
  data_files="0"
  processed_files="0"
  status="UNKNOWN"
  notes=""

  log_section "Validating $scraper_id"

  if [ ! -d "$scraper_path" ]; then
    notes="missing scraper path: $scraper_path"
    echo -e "${provider}\tSKIP\tSKIP\tSKIP\t0\t0\tSKIP\t${notes}" >> "$SUMMARY"
    return 0
  fi

  {
    echo "## Build $scraper_id"
    date
    ./publish-single.sh "$scraper_path"
  } > "${prefix}_01_build.txt" 2>&1

  if grep -Eq "Done: ${scraper_id}|digest: sha256" "${prefix}_01_build.txt"; then
    build_status="PASS"
  else
    build_status="FAIL"
    notes="build did not show success marker"
  fi

  {
    echo "## Trigger $scraper_id"
    date

    echo
    echo "--- unpause ---"
    docker compose -p "$PROJECT" exec -T airflow-scheduler /entrypoint airflow dags unpause "$scraper_id" || true

    echo
    echo "--- trigger ---"
    docker compose -p "$PROJECT" exec -T airflow-scheduler /entrypoint airflow dags trigger "$scraper_id"
  } > "${prefix}_02_trigger.txt" 2>&1

  if grep -Eq "creating dag run|dag_run_id|queued" "${prefix}_02_trigger.txt"; then
    trigger_status="PASS"
  else
    trigger_status="CHECK"
    notes="${notes}; trigger output did not show normal queued marker"
  fi

  {
    echo "## Wait for $scraper_id"
    date
    echo "Waiting ${WAIT_SECONDS}s for tasks/output..."
    sleep "$WAIT_SECONDS"
  } > "${prefix}_03_wait.txt" 2>&1

  {
    echo "## Logs for $scraper_id"
    date

    docker compose -p "$PROJECT" exec -T airflow-scheduler bash -lc \
      "find /opt/airflow/logs/dag_id=${scraper_id} -type f | sort | xargs -r -n1 sh -c 'echo ===== \$0 =====; tail -220 \$0'"
  } > "${prefix}_04_logs.txt" 2>&1

  if [ -s "${prefix}_04_logs.txt" ]; then
    logs_status="PASS"
  else
    logs_status="MISSING"
    notes="${notes}; no logs captured"
  fi

  {
    echo "## Error summary for $scraper_id"
    date

    docker compose -p "$PROJECT" exec -T airflow-scheduler bash -lc \
      "find /opt/airflow/logs/dag_id=${scraper_id} -type f | sort | xargs -r grep -Ei 'error|exception|failed|traceback|Saved|Uploaded|Downloaded|Processed|Extracted|Fetching|Wrote|No such|404|403'"
  } > "${prefix}_05_log_summary.txt" 2>&1

  {
    echo "## Data files for $scraper_id"
    date

    docker run --rm -v "$VOLUME:/data" alpine sh -lc \
      "find /data/japan -path '*${provider}*' -type f -exec ls -lh {} \; | sort"
  } > "${prefix}_06_data_files.txt" 2>&1

  data_files="$(grep -c '^-' "${prefix}_06_data_files.txt" || true)"

  {
    echo "## Processed quick check for $scraper_id"
    date

    docker run --rm -v "$VOLUME:/data" alpine sh -lc \
      "find /data/japan -path '*${provider}*processed*' -type f | sort | xargs -r -n1 sh -c 'echo ===== \$0 =====; wc -c \$0; head -c 1200 \$0; echo'"
  } > "${prefix}_07_processed_quick_check.txt" 2>&1

  processed_files="$(grep -c '^=====' "${prefix}_07_processed_quick_check.txt" || true)"

  if [ "$build_status" = "PASS" ] && [ "$trigger_status" = "PASS" ] && [ "$data_files" -gt 0 ] && [ "$processed_files" -gt 0 ]; then
    status="PASS"
  elif [ "$build_status" = "PASS" ] && [ "$trigger_status" = "PASS" ] && [ "$data_files" -gt 0 ] && [ "$processed_files" -eq 0 ]; then
    status="PARTIAL"
    notes="${notes}; raw output exists but processed output not found"
  elif [ "$build_status" = "FAIL" ]; then
    status="FAIL"
  else
    status="CHECK"
    notes="${notes}; inspect logs/output"
  fi

  echo -e "${provider}\t${build_status}\t${trigger_status}\t${logs_status}\t${data_files}\t${processed_files}\t${status}\t${notes}" >> "$SUMMARY"

  echo
  echo "Result for ${scraper_id}: ${status}"
}

main() {
  log_section "Japan scraper validation run"
  echo "RUN_DIR=$RUN_DIR"
  echo "PROJECT=$PROJECT"
  echo "VOLUME=$VOLUME"
  echo "WAIT_SECONDS=$WAIT_SECONDS"
  echo "PROVIDERS=${PROVIDERS[*]}"

  preflight
  ensure_stack
  capture_stack_status

  for provider in "${PROVIDERS[@]}"; do
    validate_provider "$provider"
  done

  {
    echo "## Final summary"
    date
    column -t -s $'\t' "$SUMMARY" || cat "$SUMMARY"
  } | tee "$RUN_DIR/99_final_summary.txt"

  if command -v zip >/dev/null 2>&1; then
    zip -r "${RUN_DIR}.zip" "$RUN_DIR" >/dev/null
    echo
    echo "Created evidence bundle: ${RUN_DIR}.zip"
  fi
}

main "$@"
