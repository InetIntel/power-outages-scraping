from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from airflow.providers.docker.exceptions import DockerContainerFailedException
from airflow.providers.slack.hooks.slack import SlackHook
from airflow.sdk import Variable


SLACK_CONNECTION_ID = "slack_scraper_alerts"
STATE_KEY_PREFIX = "scraper_alert_state__"
MAX_FAILURE_NOTIFICATIONS = 3

RED = "danger"
GREEN = "good"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _state_key(dag_id: str) -> str:
    return f"{STATE_KEY_PREFIX}{dag_id}"


def _healthy_state() -> dict[str, Any]:
    return {
        "status": "healthy",
        "consecutive_failures": 0,
        "notifications_sent": 0,
        "first_failure_at": None,
        "last_failure_at": None,
    }


def _load_state(dag_id: str) -> dict[str, Any]:
    state = Variable.get(
        _state_key(dag_id),
        default=None,
        deserialize_json=True,
    )

    if not isinstance(state, dict):
        return _healthy_state()

    return {
        **_healthy_state(),
        **state,
    }


def _save_state(dag_id: str, state: dict[str, Any]) -> None:
    Variable.set(
        _state_key(dag_id),
        state,
        serialize_json=True,
    )


def _header_block(text: str) -> dict[str, Any]:
    return {"type": "header", "text": {"type": "plain_text", "text": text}}


def _fields_block(pairs: list[tuple[str, str]]) -> dict[str, Any]:
    return {
        "type": "section",
        "fields": [
            {"type": "mrkdwn", "text": f"*{label}:*\n{value}"} for label, value in pairs
        ],
    }


def _text_block(text: str) -> dict[str, Any]:
    return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


def _log_button_block(log_url: str) -> dict[str, Any]:
    return {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "View Logs"},
                "url": log_url,
            }
        ],
    }


def _send_slack_message(
    fallback: str,
    color: str,
    blocks: list[dict[str, Any]],
) -> None:
    channel_id = os.environ.get("SLACK_CHANNEL_ID")

    if not channel_id:
        raise RuntimeError("SLACK_CHANNEL_ID is not configured")

    SlackHook(slack_conn_id=SLACK_CONNECTION_ID).client.chat_postMessage(
        channel=channel_id,
        text=fallback,
        attachments=[{"color": color, "blocks": blocks}],
    )


def _dag_id_from_context(context: dict[str, Any]) -> str:
    dag_run = context.get("dag_run")

    if dag_run is not None and getattr(dag_run, "dag_id", None):
        return dag_run.dag_id

    dag = context.get("dag")

    if dag is not None and getattr(dag, "dag_id", None):
        return dag.dag_id

    return "unknown_scraper"


def _task_id_from_context(context: dict[str, Any]) -> str:
    task_instance = context.get("task_instance") or context.get("ti")
    return getattr(task_instance, "task_id", "unknown_task")


def _log_url_from_context(context: dict[str, Any]) -> str | None:
    task_instance = context.get("task_instance") or context.get("ti")

    try:
        return getattr(task_instance, "log_url", None)
    except Exception:
        return None


def _last_container_log_line(logs: list[str | bytes]) -> str | None:
    for line in reversed(logs):
        if isinstance(line, bytes):
            line = line.decode("utf-8", errors="replace")

        line = line.strip()

        if line:
            return line

    return None


def _error_from_context(context: dict[str, Any]) -> str:
    exception = context.get("exception")

    if exception is None:
        return "No exception details were provided."

    error = " ".join(str(exception).split())

    # DockerOperator failures only say "exit code N" — the actual Python error
    # is the last line the container logged.
    if isinstance(exception, DockerContainerFailedException) and exception.logs:
        last_line = _last_container_log_line(exception.logs)

        if last_line:
            error = f"{last_line}\n({error})"

    if len(error) > 500:
        return f"{error[:497]}..."

    return error


def _format_duration(started_at: str | None, ended_at: datetime) -> str:
    if not started_at:
        return "unknown"

    try:
        started = datetime.fromisoformat(started_at)
    except ValueError:
        return "unknown"

    seconds = max(0, int((ended_at - started).total_seconds()))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []

    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")

    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

    if not parts:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

    return " ".join(parts)


def notify_dag_failure(context: dict[str, Any]) -> None:
    dag_id = _dag_id_from_context(context)
    task_id = _task_id_from_context(context)
    now = _utc_now()

    state = _load_state(dag_id)

    if state["status"] != "failing":
        state = {
            "status": "failing",
            "consecutive_failures": 1,
            "notifications_sent": 0,
            "first_failure_at": now.isoformat(),
            "last_failure_at": now.isoformat(),
        }
    else:
        state["consecutive_failures"] += 1
        state["last_failure_at"] = now.isoformat()

    failure_count = state["consecutive_failures"]

    if failure_count > MAX_FAILURE_NOTIFICATIONS:
        _save_state(dag_id, state)
        return

    failed_at = now.strftime("%Y-%m-%d %H:%M UTC")

    if failure_count == 1:
        fallback = f"Scraper failed: {dag_id}"
        blocks = [
            _header_block(f"🔴 Scraper failed: {dag_id}"),
            _fields_block(
                [
                    ("Task", task_id),
                    ("Failed at", failed_at),
                ]
            ),
            _text_block(f"*Error:*\n```{_error_from_context(context)}```"),
        ]
    elif failure_count == 2:
        fallback = f"Scraper still failing: {dag_id}"
        blocks = [
            _header_block(f"🔴 Scraper still failing: {dag_id}"),
            _fields_block(
                [
                    ("Latest failed task", task_id),
                    ("Consecutive failures", str(failure_count)),
                    ("Failed at", failed_at),
                ]
            ),
            _text_block(f"*Error:*\n```{_error_from_context(context)}```"),
        ]
    else:
        fallback = f"Scraper continues to fail: {dag_id}"
        blocks = [
            _header_block(f"🔴 Scraper continues to fail: {dag_id}"),
            _fields_block(
                [
                    ("Latest failed task", task_id),
                    ("Consecutive failures", str(failure_count)),
                ]
            ),
            _text_block(
                "Further failure notifications are now suppressed until "
                "the scraper recovers."
            ),
        ]

    log_url = _log_url_from_context(context)

    if log_url:
        blocks.append(_log_button_block(log_url))

    _send_slack_message(fallback, RED, blocks)

    state["notifications_sent"] += 1
    _save_state(dag_id, state)


def notify_dag_recovery(context: dict[str, Any]) -> None:
    dag_id = _dag_id_from_context(context)
    state = _load_state(dag_id)

    if state["status"] != "failing":
        return

    now = _utc_now()
    downtime = _format_duration(state.get("first_failure_at"), now)
    failure_count = state["consecutive_failures"]

    blocks = [
        _header_block(f"🟢 Scraper recovered: {dag_id}"),
        _fields_block(
            [
                ("Failed runs", str(failure_count)),
                ("Approximate downtime", downtime),
            ]
        ),
        _text_block("Failure notifications have been reset."),
    ]

    _send_slack_message(f"Scraper recovered: {dag_id}", GREEN, blocks)
    _save_state(dag_id, _healthy_state())
