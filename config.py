from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(encoding="utf-8-sig")


@dataclass(frozen=True)
class Settings:
    application_id: str
    affiliate_id: str | None
    output_dir: Path
    default_genre_ids: list[str]
    daily_run_time: str
    request_timeout: int
    use_system_proxy: bool
    proxies: dict[str, str] | None
    top_n: int = 100


def load_settings() -> Settings:
    application_id = os.getenv("RAKUTEN_APPLICATION_ID", "").strip()
    if not application_id:
        raise RuntimeError(
            "Missing RAKUTEN_APPLICATION_ID. Copy .env.example to .env and fill your API key."
        )

    default_genre_ids = [
        item.strip()
        for item in os.getenv("DEFAULT_GENRE_IDS", "0").split(",")
        if item.strip()
    ]

    http_proxy = os.getenv("HTTP_PROXY", "").strip()
    https_proxy = os.getenv("HTTPS_PROXY", "").strip()
    proxies = None
    if http_proxy or https_proxy:
        proxies = {
            "http": http_proxy,
            "https": https_proxy,
        }

    return Settings(
        application_id=application_id,
        affiliate_id=os.getenv("RAKUTEN_AFFILIATE_ID", "").strip() or None,
        output_dir=Path(os.getenv("OUTPUT_DIR", "output")).resolve(),
        default_genre_ids=default_genre_ids,
        daily_run_time=os.getenv("DAILY_RUN_TIME", "02:00").strip(),
        request_timeout=int(os.getenv("RAKUTEN_REQUEST_TIMEOUT", "60")),
        use_system_proxy=os.getenv("RAKUTEN_USE_SYSTEM_PROXY", "true").strip().lower()
        in {"1", "true", "yes", "on"},
        proxies=proxies,
    )
