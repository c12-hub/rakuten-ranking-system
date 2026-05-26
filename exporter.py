from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from openpyxl import Workbook


COLUMNS = [
    "\u5546\u54c1\u540d",
    "\u5546\u54c1\u4ef7\u683c",
    "\u5e97\u94fa\u540d",
    "\u8bc4\u8bba\u6570",
    "\u8bc4\u5206",
    "\u5546\u54c1URL",
    "\u4e3b\u56feURL",
    "\u6392\u540d",
    "\u7c7b\u76eeID",
    "\u6293\u53d6\u65f6\u95f4",
]


def save_rankings(items: list[dict], output_dir: Path, genre_id: str) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    date_text = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y%m%d")
    safe_genre_id = genre_id.replace("/", "_")

    rows = dedupe_items(items)
    csv_path = output_dir / f"ranking_{safe_genre_id}_{date_text}.csv"
    excel_path = output_dir / f"ranking_{safe_genre_id}_{date_text}.xlsx"

    write_csv(rows, csv_path)
    write_excel(rows, excel_path)

    return csv_path, excel_path


def dedupe_items(items: list[dict]) -> list[dict]:
    rows: list[dict] = []
    seen_urls: set[str] = set()

    for item in items:
        item_url = item.get("\u5546\u54c1URL", "")
        if item_url and item_url in seen_urls:
            continue
        if item_url:
            seen_urls.add(item_url)
        rows.append({column: item.get(column, "") for column in COLUMNS})

    return rows


def write_csv(rows: list[dict], csv_path: Path) -> None:
    with csv_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_excel(rows: list[dict], excel_path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Rakuten Ranking"
    sheet.append(COLUMNS)

    for row in rows:
        sheet.append([row.get(column, "") for column in COLUMNS])

    for column_cells in sheet.columns:
        max_length = max(len(str(cell.value or "")) for cell in column_cells)
        sheet.column_dimensions[column_cells[0].column_letter].width = min(max_length + 2, 60)

    workbook.save(excel_path)
