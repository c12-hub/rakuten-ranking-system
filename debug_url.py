from __future__ import annotations

import argparse
from urllib.parse import urlencode

from config import load_settings
from rakuten_client import APP_RANKING_API_URL


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print a browser-testable Rakuten API URL")
    parser.add_argument("--genre-id", default="100371", help="Rakuten genreId")
    parser.add_argument("--page", type=int, default=1, help="Ranking page")
    parser.add_argument(
        "--show-secret",
        action="store_true",
        help="Print the real URL with secrets for browser copy/paste.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = load_settings()

    params = {
        "applicationId": settings.application_id,
        "format": "json",
        "formatVersion": 2,
        "genreId": args.genre_id,
        "page": args.page,
    }
    if settings.affiliate_id:
        params["affiliateId"] = settings.affiliate_id

    real_url = f"{APP_RANKING_API_URL}?{urlencode(params)}"

    masked_params = params.copy()
    masked_params["applicationId"] = mask_value(masked_params["applicationId"])
    if "affiliateId" in masked_params:
        masked_params["affiliateId"] = mask_value(masked_params["affiliateId"])
    masked_url = f"{APP_RANKING_API_URL}?{urlencode(masked_params)}"

    print("Masked URL:")
    print(masked_url)
    print()

    if args.show_secret:
        print("Real browser URL:")
        print(real_url)
    else:
        print("Run with --show-secret to print the real URL for browser testing.")


def mask_value(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


if __name__ == "__main__":
    main()
