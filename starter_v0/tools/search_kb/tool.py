from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tools._shared import ROOT, err, terms


KB_DIR = ROOT / "helpdesk_data" / "knowledge_base"


def _load_doc(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_text(encoding="utf-8")
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) == 3:
            return dict(yaml.safe_load(parts[1]) or {}), parts[2].strip()
    return {}, raw.strip()


def search_kb(query: str = "", category: str = "all", top_k: int = 3) -> dict[str, Any]:
    try:
        query_terms = terms(query)
        wanted_category = (category or "all").strip().lower()
        hits: list[dict[str, Any]] = []
        for path in sorted(KB_DIR.glob("*.md")):
            meta, body = _load_doc(path)
            doc_category = str(meta.get("category") or "general").lower()
            if wanted_category != "all" and wanted_category != doc_category:
                continue
            haystack = " ".join([
                str(meta.get("title") or path.stem),
                doc_category,
                " ".join(str(tag) for tag in meta.get("tags", [])),
                body,
            ])
            score = len(query_terms & terms(haystack))
            if score <= 0:
                continue
            hits.append({
                "article_id": meta.get("article_id") or path.stem,
                "title": meta.get("title") or path.stem,
                "category": doc_category,
                "content": body[:2400],
                "source": "Fictional IT Knowledge Base",
                "updated_at": str(meta.get("updated_at") or "unknown"),
                "score": score,
            })
        hits.sort(key=lambda item: (-item["score"], item["article_id"]))
        return {
            "tool": "search_kb",
            "query": query,
            "category": wanted_category,
            "results": hits[: max(1, int(top_k or 3))],
            "freshness": "static_lab_data",
        }
    except Exception as exc:
        return err("search_kb", exc)
