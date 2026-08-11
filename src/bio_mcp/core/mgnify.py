"""EBI MGnify 客户端：微生物组宏基因组研究检索。

MGnify（https://www.ebi.ac.uk/metagenomics）是 EBI 的微生物组数据仓库：
收录来自细菌 / 古菌 / 病毒 / 真菌宏基因组学研究的样本与分析（MGYS 编号）。
API：/api/v1/studies（列表检索），免鉴权。
参考：https://www.ebi.ac.uk/metagenomics/api
"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.http import BioHTTP

BASE = "https://www.ebi.ac.uk/metagenomics/api/v1"


class MGnifyClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=30.0)

    # ---- 微生物组研究检索 ----
    def study_search(
        self, query: str, max_results: int = 5
    ) -> dict[str, Any]:
        """按关键词检索 MGnify 微生物组研究（宿主 / 栖息地 / 疾病等）。

        query 示例：
          gut microbiome      肠道微生物组
          human               人类宿主
          soil                土壤宏基因组
        """
        params: dict[str, Any] = {"search": query, "page_size": max_results}
        resp = self._http.get("studies", params=params)
        data = resp.json()
        studies: list[dict[str, Any]] = []
        for s in data.get("data", []):
            attrs = s.get("attributes", {}) or {}
            studies.append(
                {
                    "accession": attrs.get("accession") or s.get("id", ""),
                    "name": (attrs.get("study-name") or "").strip(),
                    "abstract": (attrs.get("study-abstract") or "").strip(),
                    "bioproject": attrs.get("bioproject", ""),
                    "samples": attrs.get("samples-count"),
                    "secondary_accession": attrs.get("secondary-accession", ""),
                    "centre": attrs.get("centre-name", ""),
                    "data_origination": attrs.get("data-origination", ""),
                    "updated": attrs.get("last-update", ""),
                }
            )
        meta = data.get("meta", {}) or {}
        pagination = meta.get("pagination", {}) or {}
        return {"count": pagination.get("count", 0), "studies": studies}

    def close(self) -> None:
        self._http.close()
