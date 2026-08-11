"""KEGG REST API 客户端。

通路查询 / 通路与基因关联 / 通路图。
参考：https://www.kegg.jp/kegg/rest/keggapi.html
"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.http import BioHTTP

BASE = "https://rest.kegg.jp"


class KEGGClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=30.0, rate_limit=1.0)

    def find_pathways(self, keyword: str) -> list[dict[str, Any]]:
        """按关键字搜索通路（如 'breast cancer'）。"""
        resp = self._http.get(f"find/pathway/{keyword}")
        lines = [l for l in resp.text.strip().splitlines() if l.strip()]
        out: list[dict[str, Any]] = []
        for line in lines[:30]:
            parts = line.split("\t")
            if len(parts) == 2:
                out.append({"id": parts[0], "name": parts[1]})
        return out

    def pathway_genes(self, pathway_id: str) -> list[dict[str, Any]]:
        """查询通路包含的基因列表。pathway_id 如 hsa05224 / map05224。"""
        resp = self._http.get(f"link/pathway/{pathway_id}")
        lines = [l for l in resp.text.strip().splitlines() if l.strip()]
        genes: list[dict[str, Any]] = []
        for line in lines:
            parts = line.split("\t")
            if len(parts) == 2 and parts[0].startswith("hsa"):
                gene_id = parts[0].split(":")[-1]
                genes.append({"gene": gene_id, "pathway": parts[1]})
        return genes

    def pathway_genes_by_pathway(self, pathway_id: str) -> list[str]:
        """返回某通路下的基因列表。

        用 get 端点解析 GENE 区（比 link 端点稳定，避免 400）。
        """
        resp = self._http.get(f"get/{pathway_id}")
        genes: list[str] = []
        in_gene = False
        for line in resp.text.splitlines():
            if line.startswith("GENE") and not line.startswith("  "):
                in_gene = True
                continue
            if in_gene:
                if line.strip() and not line.startswith(" "):
                    break  # 下一个节标题
                toks = line.strip().split()
                if toks and toks[0].isdigit():
                    genes.append(toks[0])
        return sorted(set(genes))

    def close(self) -> None:
        self._http.close()
