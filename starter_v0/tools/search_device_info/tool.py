from __future__ import annotations

import os
import re
from typing import Any
from urllib.parse import urlparse

import requests

from tools._shared import TIMEOUT, err


VENDOR_DOMAINS = {
    "lenovo": ["support.lenovo.com", "psref.lenovo.com"],
    "dell": ["dell.com"],
    "hp": ["support.hp.com"],
    "hewlett-packard": ["support.hp.com"],
}
QUERY_LABELS = {
    "specs": "technical specifications",
    "drivers": "drivers and downloads",
    "support": "support documentation",
    "compatibility": "hardware and operating system compatibility",
}
INTERNAL_IDENTIFIER = re.compile(r"\b(?:LT|DT|EMP)-\d+\b", re.IGNORECASE)


def _domain(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


def search_device_info(
    manufacturer: str = "",
    model: str = "",
    query_type: str = "support",
    max_results: int = 3,
) -> dict[str, Any]:
    manufacturer_value = (manufacturer or "").strip()
    model_value = (model or "").strip()
    query_type_value = (query_type or "support").strip().lower()
    if not manufacturer_value or not model_value:
        return {"tool": "search_device_info", "error": "missing_public_product_identity"}
    if INTERNAL_IDENTIFIER.search(f"{manufacturer_value} {model_value}"):
        return {
            "tool": "search_device_info",
            "error": "restricted_internal_identifier",
            "message": "Remove asset and employee identifiers before external search.",
        }
    if query_type_value not in QUERY_LABELS:
        return {"tool": "search_device_info", "error": "invalid_query_type", "query_type": query_type_value}

    key = os.getenv("TAVILY_API_KEY")
    if not key:
        return {
            "tool": "search_device_info",
            "error": "missing_api_key",
            "message": "Set TAVILY_API_KEY in .env to use external device search.",
        }

    try:
        vendor_key = manufacturer_value.casefold().replace(" ", "-")
        official_domains = VENDOR_DOMAINS.get(vendor_key, [])
        query = f"{manufacturer_value} {model_value} {QUERY_LABELS[query_type_value]} official"
        limit = min(5, max(1, int(max_results or 3)))
        body: dict[str, Any] = {
            "query": query,
            "search_depth": "basic",
            "max_results": limit,
            "include_answer": False,
            "include_raw_content": False,
        }
        if official_domains:
            body["include_domains"] = official_domains
        response = requests.post(
            "https://api.tavily.com/search",
            json=body,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        items = [{
            "title": item.get("title"),
            "url": item.get("url"),
            "source": _domain(item.get("url") or ""),
            "summary": item.get("content"),
            "score": item.get("score"),
        } for item in data.get("results", [])]
        return {
            "tool": "search_device_info",
            "manufacturer": manufacturer_value,
            "model": model_value,
            "query_type": query_type_value,
            "query": query,
            "official_domains": official_domains,
            "items": items,
            "external_data_notice": "Public product identity was sent to Tavily. No internal identifier or diagnostic data was included.",
        }
    except Exception as exc:
        return err("search_device_info", exc)
