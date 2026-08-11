"""STRING-db 蛋白互作网络客户端。

查询蛋白的互作网络（STRING ID、名称、分数、物种）。
参考：https://string-db.org/help/api/
"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.http import BioHTTP

BASE = "https://string-db.org/api"


class STRINGClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=30.0, rate_limit=0.5)

    def network(self, proteins: str, species: int = 9606) -> list[dict[str, Any]]:
        """查询蛋白互作网络（默认人 9606）。

        Args:
            proteins: 蛋白名/UniProt accession，逗号分隔。
            species: NCBI taxonomy ID（人=9606）。
        """
        resp = self._http.get(
            "json/network",
            params={"identifiers": proteins, "species": species, "caller_identity": "BioMCP"},
        )
        data = resp.json()
        out: list[dict[str, Any]] = []
        for e in data:
            out.append(
                {
                    "protein_a": e.get("preferredName_A"),
                    "protein_b": e.get("preferredName_B"),
                    "string_id_a": e.get("stringId_A"),
                    "string_id_b": e.get("stringId_B"),
                    "score": e.get("score"),
                    "nscore": e.get("nscore"),
                    "tscore": e.get("tscore"),
                    "combined_score": e.get("score"),
                }
            )
        return out

    def interactions(self, proteins: str, species: int = 9606) -> list[dict[str, Any]]:
        """查询与给定蛋白相互作用的伙伴（扩展网络）。"""
        resp = self._http.get(
            "json/interaction_partners",
            params={"identifiers": proteins, "species": species, "caller_identity": "BioMCP"},
        )
        data = resp.json()
        out: list[dict[str, Any]] = []
        for e in data:
            out.append(
                {
                    "protein": e.get("preferredName_A"),
                    "partner": e.get("preferredName_B"),
                    "score": e.get("score"),
                }
            )
        return out

    def close(self) -> None:
        self._http.close()
