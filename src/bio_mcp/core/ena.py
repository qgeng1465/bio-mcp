"""EBI ENA 客户端：欧洲核苷酸档案序列检索。

ENA（European Nucleotide Archive，https://www.ebi.ac.uk/ena）收录核酸序列：
基因组 / 基因 / 转录本 / 质粒 / 微生物与病毒序列等。
API：ENA Portal API（/portal/api/search），免鉴权。
参考：https://www.ebi.ac.uk/ena/browser/api
"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.http import BioHTTP

BASE = "https://www.ebi.ac.uk/ena/portal/api"

# 请求中常用的返回字段
_FIELDS = "accession,description,tax_id,scientific_name"


class ENAClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=30.0)

    # ---- 序列检索（按物种 / 关键词 / 编号）----
    def sequence_search(
        self, query: str, max_results: int = 10
    ) -> dict[str, Any]:
        """按 ENA 查询语法检索核酸序列。

        query 示例：
          tax_tree(562)                    大肠杆菌（含全部株系）
          tax_tree(2697049)                SARS-CoV-2
          accession=AP023253               按登录号
          plasmid[description] AND tax_tree(562)
        """
        params: dict[str, Any] = {
            "result": "sequence",
            "query": query,
            "limit": max_results,
            "format": "json",
            "fields": _FIELDS,
        }
        resp = self._http.get("search", params=params)
        data = resp.json()  # ENA 返回 JSON 数组
        records: list[dict[str, Any]] = []
        for r in data or []:
            records.append(
                {
                    "accession": r.get("accession", ""),
                    "description": (r.get("description") or "").strip(),
                    "tax_id": r.get("tax_id"),
                    "scientific_name": r.get("scientific_name", ""),
                }
            )
        return {"count": len(records), "records": records}

    def close(self) -> None:
        self._http.close()
