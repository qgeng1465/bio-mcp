"""Reactome 客户端：生物通路检索。

Reactome（https://reactome.org）是开源人工策划的通路数据库：
信号转导、代谢、DNA 修复、免疫等生物过程（R-HSA 编号）。
API：ContentService（/ContentService/search/query），免鉴权。
参考：https://reactome.org/ContentService
"""
from __future__ import annotations

import re
from typing import Any, Optional

from bio_mcp.core.http import BioHTTP

BASE = "https://reactome.org/ContentService"


def _strip_tags(text: str) -> str:
    """去掉 Reactome 返回里的 <span class="highlighting"> 等 HTML 标签。"""
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", text).strip()


class ReactomeClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=30.0)

    # ---- 通路搜索 ----
    def pathway_search(
        self,
        query: str,
        max_results: int = 5,
        species: Optional[str] = "9606",
    ) -> dict[str, Any]:
        """搜索 Reactome 通路。

        query 示例：
          apoptosis              细胞凋亡
          glycolysis             糖酵解
          DNA repair             DNA 修复
        species：NCBI Taxonomy id，默认 9606（人）。
        """
        params: dict[str, Any] = {
            "types": "Pathway",
            "query": query,
            "pageSize": max_results,
        }
        if species:
            params["species"] = species
        resp = self._http.get("search/query", params=params)
        data = resp.json()
        pathways: list[dict[str, Any]] = []
        for grp in data.get("results", []):
            for e in grp.get("entries", []):
                if e.get("type") != "Pathway":
                    continue
                sp = e.get("species")
                species_txt = ", ".join(sp) if isinstance(sp, list) else (sp or "")
                pathways.append(
                    {
                        "stId": e.get("stId", ""),
                        "dbId": e.get("dbId"),
                        "name": _strip_tags(e.get("name", "")),
                        "species": species_txt,
                        "summation": _strip_tags(e.get("summation", ""))[:400],
                    }
                )
        return {"count": len(pathways), "pathways": pathways}

    def close(self) -> None:
        self._http.close()
