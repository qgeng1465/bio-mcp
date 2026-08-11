"""Europe PMC 全文文献检索客户端。

Europe PMC 聚合 PubMed 摘要 + 全文开放获取（OA）文章。
参考：https://europepmc.org/RestfulWebService
"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.http import BioHTTP

BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest"


class EuropePMCClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=30.0, rate_limit=0.5)

    def search(self, query: str, max_results: int = 10) -> dict[str, Any]:
        """全文检索，返回结果数 + 文章列表（含 OA 全文链接）。"""
        resp = self._http.get(
            "search",
            params={
                "query": query,
                "format": "json",
                "pageSize": max_results,
                "resultType": "core",
            },
        )
        data = resp.json()
        results = data.get("resultList", {}).get("result", [])
        articles = []
        for r in results:
            articles.append(
                {
                    "pmid": r.get("pmid"),
                    "pmcid": r.get("pmcid"),
                    "title": r.get("title", ""),
                    "authors": r.get("authorString", ""),
                    "journal": r.get("journalInfo", {}).get("journal", {}).get("title", ""),
                    "date": r.get("firstPublicationDate", ""),
                    "doi": r.get("doi", ""),
                    "has_fulltext": bool(r.get("fullTextUrlList", {}).get("fullTextUrl")),
                    "is_open_access": r.get("isOpenAccess", False) == "Y",
                    "abstract": (r.get("abstractText") or "")[:400],
                }
            )
        return {"count": data.get("hitCount", 0), "articles": articles}

    def close(self) -> None:
        self._http.close()
