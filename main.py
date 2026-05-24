from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from config import load_settings
from exporter import save_rankings
from rakuten_client import RakutenApiError, RakutenRankingClient


LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
LOCAL_TZ = ZoneInfo("Asia/Shanghai")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rakuten Ichiba Ranking API Top100 crawler")
    parser.add_argument(
        "--genre-id",
        action="append",
        dest="genre_ids",
        help="Rakuten genreId. Can be supplied multiple times. Defaults to DEFAULT_GENRE_IDS in .env.",
    )
    parser.add_argument("--top", type=int, default=None, help="Number of ranking items to fetch.")
    parser.add_argument("--schedule", action="store_true", help="Run every day at DAILY_RUN_TIME.")
    return parser.parse_args()


def run_once(genre_ids: list[str], top_n: int) -> None:
    settings = load_settings()
    client = RakutenRankingClient(settings)

    for genre_id in genre_ids:
        logging.info("Fetching Rakuten ranking: genreId=%s top=%s", genre_id, top_n)
        items = client.fetch_top_items(genre_id=genre_id, top_n=top_n)
        csv_path, excel_path = save_rankings(items, settings.output_dir, genre_id)
        logging.info(
            "Saved %s deduplicated rows for genreId=%s: %s, %s",
            len(items),
            genre_id,
            csv_path,
            excel_path,
        )


def seconds_until_next_run(run_time: str) -> float:
    hour_text, minute_text = run_time.split(":", 1)
    now = datetime.now(LOCAL_TZ)
    next_run = now.replace(hour=int(hour_text), minute=int(minute_text), second=0, microsecond=0)
    if next_run <= now:
        next_run += timedelta(days=1)
    return (next_run - now).total_seconds()


def run_scheduler(genre_ids: list[str], top_n: int, run_time: str) -> None:
    logging.info("Scheduler started. Daily run time: %s Asia/Shanghai", run_time)
    while True:
        sleep_seconds = seconds_until_next_run(run_time)
        logging.info("Next run in %.0f seconds", sleep_seconds)
        time.sleep(sleep_seconds)
        try:
            run_once(genre_ids, top_n)
        except Exception:
            logging.exception("Scheduled run failed")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    args = parse_args()
    settings = load_settings()

    genre_ids = args.genre_ids or settings.default_genre_ids
    top_n = args.top or settings.top_n

    if args.schedule:
        run_scheduler(genre_ids, top_n, settings.daily_run_time)
    else:
        try:
            run_once(genre_ids, top_n)
        except RakutenApiError as exc:
            logging.error("%s", exc)
            sys.exit(1)


if __name__ == "__main__":
    main()
