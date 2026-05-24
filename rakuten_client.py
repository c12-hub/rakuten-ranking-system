from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import socket
from typing import Any
from zoneinfo import ZoneInfo

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from config import Settings


PRIMARY_API_URL = "https://openapi.rakuten.co.jp/ichibaranking/api/IchibaItem/Ranking/20220601"
FALLBACK_API_URL = "https://app.rakuten.co.jp/services/api/IchibaItem/Ranking/20220601"
API_URLS = [PRIMARY_API_URL, FALLBACK_API_URL]
TOKYO_TZ = ZoneInfo("Asia/Tokyo")

ITEM_NAME = "\u5546\u54c1\u540d"
ITEM_PRICE = "\u5546\u54c1\u4ef7\u683c"
SHOP_NAME = "\u5e97\u94fa\u540d"
REVIEW_COUNT = "\u8bc4\u8bba\u6570"
REVIEW_AVERAGE = "\u8bc4\u5206"
ITEM_URL = "\u5546\u54c1URL"
IMAGE_URL = "\u4e3b\u56feURL"
RANK = "\u6392\u540d"
GENRE_ID = "\u7c7b\u76eeID"
FETCHED_AT = "\u6293\u53d6\u65f6\u95f4"


class RakutenApiError(RuntimeError):
    pass


@dataclass(frozen=True)
class ApiFailure:
    endpoint: str
    error_type: str
    detail: str
    status_code: int | None = None


class RakutenRankingClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.session = requests.Session()
        self.session.trust_env = settings.use_system_proxy

    @retry(
        retry=retry_if_exception_type(RakutenApiError),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def _request_page(self, genre_id: str, page: int) -> dict[str, Any]:
        failures: list[ApiFailure] = []

        for endpoint in API_URLS:
            try:
                return self._request_page_from_endpoint(endpoint, genre_id, page)
            except RakutenApiError as exc:
                failure = exc.args[0]
                if isinstance(failure, ApiFailure):
                    failures.append(failure)
                    if failure.error_type == "TIMEOUT" and endpoint == PRIMARY_API_URL:
                        continue
                    if failure.error_type in {"DNS", "PROXY", "TIMEOUT", "403", "429", "400"}:
                        continue
                raise

        raise RakutenApiError(self._format_failures(genre_id, page, failures))

    def _request_page_from_endpoint(
        self,
        endpoint: str,
        genre_id: str,
        page: int,
    ) -> dict[str, Any]:
        app_key_name = "accessKey" if endpoint == PRIMARY_API_URL else "applicationId"
        params: dict[str, Any] = {
            app_key_name: self.settings.application_id,
            "format": "json",
            "formatVersion": 2,
            "genreId": genre_id,
            "page": page,
        }
        if self.settings.affiliate_id:
            params["affiliateId"] = self.settings.affiliate_id

        try:
            response = self.session.get(
                endpoint,
                params=params,
                timeout=self.settings.request_timeout,
                proxies=self.settings.proxies,
            )
        except requests.exceptions.ProxyError:
            raise RakutenApiError(
                ApiFailure(endpoint=endpoint, error_type="PROXY", detail="Proxy connection failed")
            ) from None
        except requests.exceptions.ConnectTimeout:
            raise RakutenApiError(
                ApiFailure(endpoint=endpoint, error_type="TIMEOUT", detail="Connection timed out")
            ) from None
        except requests.exceptions.ReadTimeout:
            raise RakutenApiError(
                ApiFailure(endpoint=endpoint, error_type="TIMEOUT", detail="Read timed out")
            ) from None
        except requests.exceptions.ConnectionError as exc:
            error_type = "DNS" if _is_dns_error(exc) else "CONNECTION"
            raise RakutenApiError(
                ApiFailure(endpoint=endpoint, error_type=error_type, detail=exc.__class__.__name__)
            ) from None
        except requests.RequestException as exc:
            raise RakutenApiError(
                ApiFailure(endpoint=endpoint, error_type="REQUEST", detail=exc.__class__.__name__)
            ) from None

        if response.status_code >= 400:
            raise RakutenApiError(
                ApiFailure(
                    endpoint=endpoint,
                    error_type=str(response.status_code),
                    detail=response.text[:300],
                    status_code=response.status_code,
                )
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise RakutenApiError(
                ApiFailure(endpoint=endpoint, error_type="INVALID_JSON", detail=str(exc))
            ) from None

        if "Items" not in payload:
            error_text = payload.get("error_description") or payload.get("error") or str(payload)
            raise RakutenApiError(
                ApiFailure(endpoint=endpoint, error_type="API_RESPONSE", detail=error_text[:300])
            )

        return payload

    def fetch_top_items(self, genre_id: str, top_n: int = 100) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        seen_keys: set[str] = set()
        page = 1

        while len(items) < top_n and page <= 34:
            payload = self._request_page(genre_id=genre_id, page=page)
            page_items = payload.get("Items", [])
            if not page_items:
                break

            fetched_at = datetime.now(TOKYO_TZ).isoformat(timespec="seconds")

            for raw_item in page_items:
                normalized = self._normalize_item(raw_item, genre_id, fetched_at)
                dedupe_key = normalized[ITEM_URL] or normalized[ITEM_NAME]
                if dedupe_key in seen_keys:
                    continue
                seen_keys.add(dedupe_key)
                items.append(normalized)
                if len(items) >= top_n:
                    break

            page += 1

        return items

    def _format_failures(
        self,
        genre_id: str,
        page: int,
        failures: list[ApiFailure],
    ) -> str:
        proxy_text = self.settings.proxies or {}
        lines = [
            f"Rakuten API request failed for genreId={genre_id}, page={page}",
            f"applicationId loaded: {'yes' if bool(self.settings.application_id) else 'no'}",
            f"affiliateId loaded: {'yes' if bool(self.settings.affiliate_id) else 'no'}",
            f"use system proxy: {'yes' if self.settings.use_system_proxy else 'no'}",
            f"explicit proxies: {proxy_text}",
            f"timeout seconds: {self.settings.request_timeout}",
        ]

        for failure in failures:
            status = f", status={failure.status_code}" if failure.status_code else ""
            lines.append(
                f"endpoint={failure.endpoint}, error_type={failure.error_type}{status}, detail={failure.detail}"
            )

        return "\n".join(lines)

    @staticmethod
    def _normalize_item(item: dict[str, Any], genre_id: str, fetched_at: str) -> dict[str, Any]:
        image_urls = item.get("mediumImageUrls") or item.get("smallImageUrls") or []
        main_image_url = ""
        if image_urls:
            first_image = image_urls[0]
            if isinstance(first_image, dict):
                main_image_url = first_image.get("imageUrl", "")
            elif isinstance(first_image, str):
                main_image_url = first_image

        return {
            ITEM_NAME: item.get("itemName", ""),
            ITEM_PRICE: item.get("itemPrice", ""),
            SHOP_NAME: item.get("shopName", ""),
            REVIEW_COUNT: item.get("reviewCount", ""),
            REVIEW_AVERAGE: item.get("reviewAverage", ""),
            ITEM_URL: item.get("itemUrl", ""),
            IMAGE_URL: main_image_url,
            RANK: item.get("rank", ""),
            GENRE_ID: genre_id,
            FETCHED_AT: fetched_at,
        }


def _is_dns_error(exc: requests.exceptions.ConnectionError) -> bool:
    current: BaseException | None = exc
    while current:
        if isinstance(current, socket.gaierror):
            return True
        current = current.__cause__ or current.__context__
    return "NameResolutionError" in str(exc) or "getaddrinfo failed" in str(exc)
