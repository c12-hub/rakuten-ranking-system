from __future__ import annotations

import time

import requests


TARGET_URL = "https://openapi.rakuten.co.jp"
TIMEOUT_SECONDS = 15

HTTP_PORTS = [7890, 7897, 10809, 8080, 7891]
SOCKS5_PORTS = [1080, 10808, 10809]


def classify_error(exc: requests.RequestException) -> str:
    if isinstance(exc, requests.exceptions.ProxyError):
        return "ProxyError"
    if isinstance(exc, (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout)):
        return "Timeout"
    if isinstance(exc, requests.exceptions.SSLError):
        return "SSLError"
    if isinstance(exc, requests.exceptions.ConnectionError):
        return "ConnectionError"
    return exc.__class__.__name__


def test_proxy(protocol: str, port: int) -> dict[str, str]:
    proxy_url = f"{protocol}://127.0.0.1:{port}"
    proxies = {
        "http": proxy_url,
        "https": proxy_url,
    }
    started_at = time.perf_counter()

    try:
        response = requests.get(TARGET_URL, proxies=proxies, timeout=TIMEOUT_SECONDS)
        elapsed = time.perf_counter() - started_at
        return {
            "protocol": protocol,
            "port": str(port),
            "success": "yes" if response.ok else "no",
            "status_code": str(response.status_code),
            "error": "" if response.ok else f"HTTP {response.status_code}",
            "elapsed": f"{elapsed:.2f}s",
        }
    except requests.RequestException as exc:
        elapsed = time.perf_counter() - started_at
        return {
            "protocol": protocol,
            "port": str(port),
            "success": "no",
            "status_code": "NONE",
            "error": classify_error(exc),
            "elapsed": f"{elapsed:.2f}s",
        }


def print_result(result: dict[str, str]) -> None:
    print(
        "protocol={protocol} port={port} success={success} "
        "status={status_code} error={error} elapsed={elapsed}".format(**result)
    )


def main() -> None:
    print(f"target={TARGET_URL}")
    print(f"timeout={TIMEOUT_SECONDS}s")
    print()

    for port in HTTP_PORTS:
        print_result(test_proxy("http", port))

    for port in SOCKS5_PORTS:
        print_result(test_proxy("socks5", port))


if __name__ == "__main__":
    main()
