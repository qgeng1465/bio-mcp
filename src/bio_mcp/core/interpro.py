"""InterPro 蛋白结构域客户端。

按 UniProt accession 查询蛋白的结构域/位点注释。
参考：https://www.ebi.ac.uk/interpro/api/
"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.http import BioHTTP

BASE = "https://www.ebi.ac.uk/interpro/api"


class InterProClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=30.0, rate_limit=1.0)

    def protein_entries(self, uniprot_acc: str) -> list[dict[str, Any]]:
        """查询蛋白的 InterPro 结构域/家族条目。

        /protein/uniprot/{acc}/entry/all/ 返回 entries_url，需再跟随该链接
        才能拿到分页的完整条目列表（metadata 含 accession/name/type）。
        """
        acc = uniprot_acc.strip().upper()
        resp = self._http.get(f"protein/uniprot/{acc}/entry/all/")
        data = resp.json()
        entries_url = data.get("entries_url")
        if not entries_url:
            return []
        resp2 = self._http.get(entries_url)
        data2 = resp2.json()
        out: list[dict[str, Any]] = []
        for r in data2.get("results") or []:
            meta = r.get("metadata") or {}
            out.append(
                {
                    "accession": meta.get("accession"),
                    "name": meta.get("name") or "",
                    "short_name": meta.get("short_name") or "",
                    "type": meta.get("type") or "",
                }
            )
        return out

    def close(self) -> None:
        self._http.close()
