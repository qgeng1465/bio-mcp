"""EBI IntAct 客户端：实验分子互作检索。

IntAct（https://www.ebi.ac.uk/intact）收录经实验验证的分子互作
（蛋白-蛋白 / 蛋白-核酸等），带检测方法与文献支持（EBI 编号）。
API：/intact/ws/interaction/findInteractions/{query}，免鉴权。
参考：https://www.ebi.ac.uk/intact/ws
"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.http import BioHTTP

BASE = "https://www.ebi.ac.uk/intact/ws"


class IntActClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=30.0)

    # ---- 分子互作检索 ----
    def find_interactions(
        self, query: str, max_results: int = 10
    ) -> dict[str, Any]:
        """按基因 / 蛋白名或 UniProt 编号检索实验互作。

        query 示例：
          TP53         基因名
          P04637       UniProt 编号
        """
        resp = self._http.get(
            f"interaction/findInteractions/{query}",
            params={"page": 0, "pageSize": max_results},
        )
        data = resp.json()
        interactions: list[dict[str, Any]] = []
        for it in data.get("content", []):
            interactions.append(
                {
                    "binary_id": it.get("binaryInteractionId"),
                    "molecule_a": it.get("moleculeA", ""),
                    "molecule_b": it.get("moleculeB", ""),
                    "id_a": it.get("idA", ""),
                    "id_b": it.get("idB", ""),
                    "detection_method": it.get("detectionMethod", ""),
                    "miscore": it.get("intactMiscore"),
                    "count": it.get("count"),
                    "pubmed": it.get("publicationPubmedIdentifier"),
                    "first_author": it.get("firstAuthor", ""),
                }
            )
        return {
            "count": data.get("totalElements", len(interactions)),
            "interactions": interactions,
        }

    def close(self) -> None:
        self._http.close()
