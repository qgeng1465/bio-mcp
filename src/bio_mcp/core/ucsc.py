"""UCSC Genome Browser API 客户端。

UCSC 基因组浏览器（加州大学圣克鲁兹）覆盖 100+ 物种基因组。
参考：https://genome.ucsc.edu/goldenPath/help/api.html
"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.http import BioHTTP

BASE = "https://api.genome.ucsc.edu"


class UCSCClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=30.0, rate_limit=0.5)

    def list_genomes(self) -> list[dict[str, Any]]:
        """列出可用基因组组装（assembly）。"""
        resp = self._http.get("list/ucscGenomes")
        data = resp.json().get("ucscGenomes", {})
        out = []
        for key, info in data.items():
            out.append(
                {
                    "name": key,
                    "organism": info.get("organism", ""),
                    "description": info.get("description", ""),
                }
            )
        return out

    def genome_info(self, assembly: str) -> dict[str, Any]:
        """查询某个组装的信息。"""
        out: dict[str, Any] = {}
        try:
            resp = self._http.get("list/ucscGenomes")
            data = resp.json().get("ucscGenomes", {})
            if assembly in data:
                info = data[assembly]
                out = {
                    "name": assembly,
                    "organism": info.get("organism"),
                    "description": info.get("description"),
                    "scientificName": info.get("scientificName"),
                    "orderKey": info.get("orderKey"),
                }
        except Exception:
            pass
        return out

    def gene_tracks(self, assembly: str) -> list[str]:
        """查询某组装下可用的基因注释 track。"""
        out: list[str] = []
        try:
            resp = self._http.get(
                "list/tracks", params={"genome": assembly, "trackLeavesOnly": 1}
            )
            tracks = resp.json().get(assembly, {}).get("tracks", [])
            for t in tracks[:40]:
                if any(k in t.lower() for k in ("gene", "refseq", "ensembl", "ucsc", "mirna")):
                    out.append(t)
        except Exception:
            pass
        return out

    def close(self) -> None:
        self._http.close()
