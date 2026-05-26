from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from exporter import save_rankings
from rakuten_client import RakutenRankingClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import downloaded Rakuten JSON into CSV and Excel")
    parser.add_argument("--input", default="downloaded_rakuten.json", help="Downloaded JSON path")
    parser.add_argument("--genre-id", default="100371", help="Rakuten genreId")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    with input_path.open("r", encoding="utf-8-sig") as file:
        payload = json.load(file)

    page_items = extract_items(payload)
    fetched_at = datetime.now(ZoneInfo("Asia/Tokyo")).isoformat(timespec="seconds")
    items = [
        RakutenRankingClient._normalize_item(raw_item, args.genre_id, fetched_at)
        for raw_item in page_items
    ]

    csv_path, excel_path = save_rankings(items, output_dir, args.genre_id)
    print(f"Imported {len(items)} rows")
    print(f"CSV: {csv_path}")
    print(f"Excel: {excel_path}")


def extract_items(payload: dict) -> list[dict]:
    if isinstance(payload.get("Items"), list):
        return payload["Items"]
    if isinstance(payload.get("items"), list):
        return payload["items"]
    if isinstance(payload.get("data"), dict) and isinstance(payload["data"].get("Items"), list):
        return payload["data"]["Items"]
    raise ValueError("Cannot find Items list in downloaded JSON")


if __name__ == "__main__":
    main()
