"""CELLxGENE Census（CZ）单细胞数据客户端。

CZ CELLxGENE 收录数百万单细胞转录组数据（含类器官/组织样本）。
参考：https://api.cellxgene.cziscience.com/curation/v1/
"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.http import BioHTTP

BASE = "https://api.cellxgene.cziscience.com"


class CellxGeneClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=30.0, rate_limit=0.5)

    def search_datasets(self, term: str, max_results: int = 5) -> list[dict[str, Any]]:
        """在已发布数据集中检索（按名称/疾病/组织/细胞类型匹配）。"""
        datasets: list[dict[str, Any]] = []
        try:
            resp = self._http.get("curation/v1/collections")
            collections = resp.json()
        except Exception:
            return datasets
        # 每个 collection 包含 datasets，过滤名称/描述/组织包含关键字
        term_l = term.lower()
        for c in collections:
            name = (c.get("name") or "").lower()
            desc = (c.get("description") or "").lower()
            if term_l in name or term_l in desc:
                datasets.append(
                    {
                        "collection_id": c.get("collection_id"),
                        "name": c.get("name"),
                        "description": (c.get("description") or "")[:200],
                        "dataset_count": len(c.get("datasets", [])),
                    }
                )
            if len(datasets) >= max_results:
                break
        return datasets

    def close(self) -> None:
        self._http.close()
