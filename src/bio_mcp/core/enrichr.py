"""Enrichr 富集分析客户端（Ma'ayan Lab）。

Enrichr 是国内可达的开源富集服务（g:Profiler 的爱沙尼亚服务器在部分地区不可达，
故默认采用 Enrichr）。支持 GO / KEGG / Reactome / WikiPathways 等数百个基因集库。
参考：https://maayanlab.cloud/Enrichr/（文档: https://maayanlab.cloud/Enrichr/#api）
"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.http import BioHTTP

BASE = "https://maayanlab.cloud/Enrichr"

# 常用基因集库（backgroundType）
DEFAULT_LIBS = {
    "GO_Biological_Process_2021": "GO 生物过程",
    "GO_Molecular_Function_2021": "GO 分子功能",
    "GO_Cellular_Component_2021": "GO 细胞组分",
    "KEGG_2021_Human": "KEGG 通路",
    "Reactome_2022": "Reactome 通路",
    "WikiPathway_2021_Human": "WikiPathways",
}


class EnrichrClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=30.0, rate_limit=0.3)

    def _add_list(self, genes: list[str]) -> int:
        """提交基因列表，返回 userListId。

        Enrichr 要求 multipart/form-data（不是 urlencoded）且基因按换行分隔。
        """
        import httpx

        resp = self._http.post(
            "addList",
            files={"list": ("list.txt", "\n".join(genes), "text/plain")},
        )
        return int(resp.json().get("userListId", 0))

    def enrich(
        self,
        genes: list[str],
        background_type: str = "GO_Biological_Process_2021",
        max_terms: int = 20,
        max_pvalue: float = 0.05,
    ) -> dict[str, Any]:
        """Enrichr 富集。返回显著项列表。"""
        user_list_id = self._add_list(genes)
        resp = self._http.get(
            "enrich",
            params={"userListId": user_list_id, "backgroundType": background_type},
        )
        data = resp.json()
        rows = data.get(background_type) or []
        significant: list[dict[str, Any]] = []
        for row in rows:
            # Enrichr 行结构:
            # [0] rank, [1] term, [2] pvalue, [3] zscore, [4] combined,
            # [5] overlapping_genes, [6] adjusted_pvalue, ...
            pvalue = float(row[2])
            if pvalue >= max_pvalue:
                continue
            significant.append(
                {
                    "term": row[1],
                    "p_value": pvalue,
                    "adjusted_p_value": float(row[6]) if len(row) > 6 and row[6] else None,
                    "z_score": float(row[3]) if row[3] else 0.0,
                    "combined_score": float(row[4]) if row[4] else 0.0,
                    "genes": row[5] if isinstance(row[5], list) else [],
                    "library": background_type,
                }
            )
        significant.sort(key=lambda t: t["p_value"])
        return {
            "library": background_type,
            "library_name": DEFAULT_LIBS.get(background_type, background_type),
            "input_genes": len(genes),
            "significant_terms": significant[:max_terms],
            "total_tested": len(rows),
        }

    def close(self) -> None:
        self._http.close()
