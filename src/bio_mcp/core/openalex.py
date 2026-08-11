"""OpenAlex 客户端：学术文献检索。

OpenAlex（https://openalex.org）收录全球 2.5 亿+ 学术著作，
覆盖期刊 / 会议 / 预印本，含引用计数、作者与机构信息。
API：api.openalex.org，免鉴权、免费。
参考：https://docs.openalex.org
"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.http import BioHTTP

BASE = "https://api.openalex.org"

# 只取需要的字段，减小响应体积
_SELECT = (
    "id,doi,display_name,publication_year,cited_by_count,"
    "type,authorships,primary_location,open_access"
)


class OpenAlexClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=30.0)

    # ---- 文献检索 ----
    def work_search(
        self, query: str, max_results: int = 5
    ) -> dict[str, Any]:
        """按关键词检索学术著作。

        query 示例：
          CRISPR gene editing
          single cell RNA-seq cancer
          "organ-on-chip"
        """
        params: dict[str, Any] = {
            "search": query,
            "per-page": max_results,
            "select": _SELECT,
        }
        resp = self._http.get("works", params=params)
        data = resp.json()
        works: list[dict[str, Any]] = []
        for w in data.get("results", []):
            authors = [
                (a.get("author") or {}).get("display_name", "")
                for a in (w.get("authorships") or [])
                if (a.get("author") or {}).get("display_name")
            ]
            src = (w.get("primary_location") or {}).get("source") or {}
            works.append(
                {
                    "title": (w.get("display_name") or "").strip(),
                    "year": w.get("publication_year"),
                    "cited_by": w.get("cited_by_count"),
                    "type": w.get("type", ""),
                    "doi": w.get("doi", ""),
                    "authors": authors[:15],
                    "venue": src.get("display_name", ""),
                    "oa_status": (w.get("open_access") or {}).get("oa_status", ""),
                }
            )
        meta = data.get("meta", {}) or {}
        return {"count": meta.get("count", 0), "works": works}

    def close(self) -> None:
        self._http.close()
