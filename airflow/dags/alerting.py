from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from airflow.providers.slack.hooks.slack import SlackHook
from airflow.sdk import Variable


SLACK_CONNECTION_ID = "slack_scraper_alerts"
STATE_KEY_PREFIX = "scraper_alert_state__"
MAX_FAILURE_NOTIFICATIONS = 3


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


def _send_slack_message(message: str) -> None:
    channel_id = os.environ.get("SLACK_CHANNEL_ID")

    if not channel_id:
        raise RuntimeError("SLACK_CHANNEL_ID is not configured")

    SlackHook(
        slack_conn_id=SLACK_CONNECTION_ID,
    ).call(
        "chat.postMessage",
        json={
            "channel": channel_id,
            "text": message,
        },
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


def _error_from_context(context: dict[str, Any]) -> str:
    exception = context.get("exception")

    if exception is None:
        return "No exception details were provided."

    error = " ".join(str(exception).split())

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

    if failure_count == 1:
        message = (
            f"{dag_id} failed.\n"
            f"Task: {task_id}\n"
            f"Error: {_error_from_context(context)}"
        )
    elif failure_count == 2:
        message = (
            f"{dag_id} is still failing.\n"
            f"Consecutive failures: {failure_count}\n"
            f"Latest failed task: {task_id}"
        )
    elif failure_count == MAX_FAILURE_NOTIFICATIONS:
        message = (
            f"{dag_id} continues to fail.\n"
            f"Consecutive failures: {failure_count}\n\n"
            "Further failure notifications are now suppressed until "
            "the scraper recovers."
        )
    else:
        _save_state(dag_id, state)
        return

    _send_slack_message(message)

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

    message = (
        f"{dag_id} has recovered.\n"
        f"Failed runs: {failure_count}\n"
        f"Approximate downtime: {downtime}\n\n"
        "Failure notifications have been reset."
    )

    _send_slack_message(message)
    _save_state(dag_id, _healthy_state())
