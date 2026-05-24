from __future__ import annotations

import time

import requests

from config import load_settings


URLS = [
    "https://openapi.rakuten.co.jp",
    "https://app.rakuten.co.jp",
]


def classify_error(exc: requests.RequestException) -> str:
    if isinstance(exc, requests.exceptions.ProxyError):
        return "PROXY"
    if isinstance(exc, (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout)):
        return "TIMEOUT"
    if isinstance(exc, requests.exceptions.ConnectionError):
        text = str(exc)
        if "NameResolutionError" in text or "getaddrinfo failed" in text:
            return "DNS"
        return "CONNECTION"
    return "REQUEST"


def main() -> None:
    settings = load_settings()
    session = requests.Session()
    session.trust_env = settings.use_system_proxy

    print(f"applicationId loaded: {'yes' if bool(settings.application_id) else 'no'}")
    print(f"affiliateId loaded: {'yes' if bool(settings.affiliate_id) else 'no'}")
    print(f"use system proxy: {'yes' if settings.use_system_proxy else 'no'}")
    print(f"explicit proxies: {settings.proxies or {}}")
    print(f"timeout seconds: {settings.request_timeout}")
    print()

    for url in URLS:
        started_at = time.perf_counter()
        try:
            response = session.get(
                url,
                timeout=settings.request_timeout,
                proxies=settings.proxies,
            )
            elapsed = time.perf_counter() - started_at
            error_type = str(response.status_code) if response.status_code >= 400 else "OK"
            print(
                f"url={url} status={response.status_code} elapsed={elapsed:.2f}s error_type={error_type}"
            )
        except requests.RequestException as exc:
            elapsed = time.perf_counter() - started_at
            print(
                f"url={url} status=NONE elapsed={elapsed:.2f}s "
                f"error_type={classify_error(exc)} reason={exc.__class__.__name__}"
            )


if __name__ == "__main__":
    main()
