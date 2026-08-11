"""AlphaFold DB（EBI）蛋白结构预测客户端。

AlphaFold 数据库提供 2 亿+ 蛋白的 AI 预测结构（pLDDT 置信度）。
参考：https://alphafold.ebi.ac.uk/api-docs
"""
from __future__ import annotations

from typing import Any, Optional

from bio_mcp.core.http import BioHTTP

BASE = "https://alphafold.ebi.ac.uk/api"


class AlphaFoldClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=30.0, rate_limit=0.5)

    def prediction(self, uniprot_acc: str) -> Optional[dict[str, Any]]:
        """按 UniProt accession 查询 AlphaFold 预测结构。

        返回 entry id、序列长度、pLDDT 置信度、3D 模型下载链接。
        """
        try:
            resp = self._http.get(f"prediction/{uniprot_acc}")
        except Exception:
            return None
        data = resp.json()
        if not isinstance(data, list) or not data:
            return None
        entry = data[0]
        model_urls = [
            u
            for u in entry.get("pdbUrl", "").split()
            if u
        ]
        return {
            "entry_id": entry.get("entryId"),
            "uniprot_acc": entry.get("uniprotAccession"),
            "gene": entry.get("gene"),
            "organism": entry.get("organismScientificName"),
            "sequence_length": entry.get("uniprotLength"),
            "avg_plddt": entry.get("uniprotScore"),
            "model_db_url": entry.get("pdbUrl"),
            "model_urls": model_urls,
        }

    def close(self) -> None:
        self._http.close()
