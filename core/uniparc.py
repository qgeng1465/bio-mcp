"""EBI UniParc 客户端：蛋白序列归档与交叉引用检索。

UniParc（Universal Protein Archive，https://www.uniprot.org/uniparc）
收录所有公开蛋白序列，去冗余，记录每条序列在所有数据库中的
交叉引用（UniProtKB / RefSeq / Ensembl / EMBL / PDB 等）。
API：rest.uniprot.org/uniparc/search，免鉴权。
参考：https://www.uniprot.org/help/uniparc
"""
from __future__ import annotations

from typing import Any, Optional

from bio_mcp.core.http import BioHTTP

BASE = "https://rest.uniprot.org/uniparc"


class UniParcClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=30.0)

    # ---- 序列搜索（按物种/基因/蛋白名）----
    def search(
        self,
        query: str,
        max_results: int = 5,
        fields: Optional[str] = None,
    ) -> dict[str, Any]:
        """按 UniParc 查询语法检索序列归档。

        query 示例：
          taxonomy_id:9606 AND gene:TP53
          accession:P04637
          organism:"Homo sapiens"
        """
        params: dict[str, Any] = {"query": query, "format": "json", "size": max_results}
        if fields:
            params["fields"] = fields
        resp = self._http.get("search", params=params)
        data = resp.json()
        return {
            "count": len(data.get("results", [])),
            "results": data.get("results", []),
        }

    # ---- 按 UniParc ID 查询交叉引用 ----
    def by_accession(self, upi: str) -> dict[str, Any]:
        """按 UPI（如 UPI0000123165）查询序列及其全部交叉引用。"""
        resp = self._http.get(f"{upi.strip().upper()}.json")
        return resp.json()

    def close(self) -> None:
        self._http.close()
