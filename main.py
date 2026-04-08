import sqlite3
import time
from datetime import datetime, time as dt_time
from pathlib import Path

import requests

DB_PATH = Path("saw_monitor.db")
INTERVAL_SECONDS = 10 # Tid i sekunder mellan varje kontroll
REQUEST_TIMEOUT_SECONDS = 10 # Timeout för HTTP-förfrågningar i sekunder

START_TIME = dt_time(9, 0)  # Tid vi startar övervakningen
END_TIME = dt_time(5, 0)     # Tid vi avslutar övervakningen

TARGETS = [
    {"name": "Saw 1", "url": "http://nobsa2imasaw01:9876/interface/isconnected"},
    {"name": "Saw 2", "url": "http://nobsa2imasaw01:9877/interface/isconnected"},
]


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ping_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_name TEXT NOT NULL,
                url TEXT NOT NULL,
                checked_at TEXT NOT NULL,
                response_time_ms REAL,
                success INTEGER NOT NULL,
                status_code INTEGER,
                response_text TEXT,
                error_text TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def insert_log(
    target_name: str,
    url: str,
    checked_at: str,
    response_time_ms: float | None,
    success: bool,
    status_code: int | None,
    response_text: str | None,
    error_text: str | None,
) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            INSERT INTO ping_log (
                target_name,
                url,
                checked_at,
                response_time_ms,
                success,
                status_code,
                response_text,
                error_text
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                target_name,
                url,
                checked_at,
                response_time_ms,
                1 if success else 0,
                status_code,
                response_text,
                error_text,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def is_in_time_window(now: datetime) -> bool:
    current_time = now.time()

    if START_TIME < END_TIME:
        return START_TIME <= current_time < END_TIME

    return current_time >= START_TIME or current_time < END_TIME


def check_target(target: dict) -> None:
    checked_at = datetime.now().isoformat(timespec="seconds")

    try:
        start = time.perf_counter()
        response = requests.get(target["url"], timeout=REQUEST_TIMEOUT_SECONDS)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        insert_log(
            target_name=target["name"],
            url=target["url"],
            checked_at=checked_at,
            response_time_ms=elapsed_ms,
            success=response.ok,
            status_code=response.status_code,
            response_text=response.text.strip(),
            error_text=None,
        )

        print(
            f"[{checked_at}] {target['name']} | "
            f"status={response.status_code} | "
            f"time={elapsed_ms} ms | "
            f"body={response.text.strip()}"
        )

    except requests.RequestException as e:
        insert_log(
            target_name=target["name"],
            url=target["url"],
            checked_at=checked_at,
            response_time_ms=None,
            success=False,
            status_code=None,
            response_text=None,
            error_text=str(e),
        )

        print(f"[{checked_at}] {target['name']} | ERROR | {e}")


def poll_every_10_seconds() -> None:
    while True:
        now = datetime.now()

        if is_in_time_window(now):
            for target in TARGETS:
                check_target(target)

            time.sleep(INTERVAL_SECONDS)
        else:
            print(
                f"[{now.isoformat(timespec='seconds')}] "
                f"Outisde monitoring window ({START_TIME.strftime('%H:%M')} - {END_TIME.strftime('%H:%M')})"
            )
            time.sleep(60)


if __name__ == "__main__":
    init_db()
    poll_every_10_seconds()