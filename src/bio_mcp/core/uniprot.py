"""UniProt REST API 客户端。

按 accession 或基因名查蛋白注释（名称、物种、功能、GO、结构域）。
参考：https://www.uniprot.org/help/api
"""
from __future__ import annotations

from typing import Any, Optional

from bio_mcp.core.http import BioHTTP

BASE = "https://rest.uniprot.org/uniprotkb"


class UniProtClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=30.0, rate_limit=0.5)

    def search(
        self,
        query: str,
        fields: Optional[list[str]] = None,
        max_results: int = 5,
    ) -> list[dict[str, Any]]:
        """按关键字检索 UniProt 条目。fields: accession,id,protein_name,gene_names,organism_name,length,go_id,cc_function"""
        default_fields = [
            "accession",
            "id",
            "protein_name",
            "gene_names",
            "organism_name",
            "length",
            "cc_function",
            "go_id",
            "cc_catalytic_activity",
        ]
        resp = self._http.get(
            "search",
            params={
                "query": query,
                "format": "json",
                "size": max_results,
                "fields": ",".join(fields or default_fields),
            },
        )
        results = resp.json().get("results", [])
        out: list[dict[str, Any]] = []
        for r in results:
            func = r.get("comments", [])
            function = next(
                (c["texts"][0]["value"] for c in func if c.get("commentType") == "FUNCTION" and c.get("texts")),
                "",
            )
            out.append(
                {
                    "accession": r.get("primaryAccession"),
                    "entry_name": r.get("secondaryAccessions") or [],
                    "protein_name": r.get("proteinDescription", {}).get("recommendedName", {}).get(
                        "fullName", {}
                    ).get("value", ""),
                    "gene": [g.get("geneName", {}).get("value") for g in r.get("genes", [])],
                    "organism": r.get("organism", {}).get("scientificName", ""),
                    "length": r.get("sequence", {}).get("length"),
                    "function": function,
                    "go_terms": r.get("go_terms", []) if r.get("go_terms") else [],
                    "sequence": r.get("sequence", {}).get("value", ""),
                }
            )
        return out

    def fetch(self, accession: str) -> Optional[dict[str, Any]]:
        """按 accession 拉取单个条目（精确匹配）。"""
        resp = self._http.get(accession.strip(), params={"format": "json"})
        r = resp.json()
        func = r.get("comments", [])
        function = next(
            (c["texts"][0]["value"] for c in func if c.get("commentType") == "FUNCTION" and c.get("texts")),
            "",
        )
        return {
            "accession": r.get("primaryAccession"),
            "protein_name": r.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get(
                "value", ""
            ),
            "gene": [g.get("geneName", {}).get("value") for g in r.get("genes", [])],
            "organism": r.get("organism", {}).get("scientificName", ""),
            "length": r.get("sequence", {}).get("length"),
            "function": function,
            "go_terms": [g.get("id") for g in (r.get("go_terms") or [])],
            "sequence": r.get("sequence", {}).get("value", ""),
        }

    def close(self) -> None:
        self._http.close()
