"""Ensembl REST API 客户端。

基因查询 / 转录本 / 同源映射 / 序列（GRCh38/hg38 默认）。
参考：https://rest.ensembl.org/documentation/info
"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.http import BioHTTP

BASE = "https://rest.ensembl.org"


class EnsemblClient:
    def __init__(self) -> None:
        self._http = BioHTTP(
            base_url=BASE,
            timeout=60.0,
            rate_limit=0.5,
            headers={"Content-Type": "application/json"},
        )

    def gene_by_symbol(self, symbol: str, species: str = "homo_sapiens") -> dict[str, Any]:
        """按基因符号查询基因（Ensembl gene ID、位置、生物型、描述）。"""
        resp = self._http.get(f"lookup/symbol/{species}/{symbol}")
        data = resp.json()
        return {
            "gene_id": data.get("id"),
            "symbol": data.get("display_name"),
            "description": data.get("description"),
            "biotype": data.get("biotype"),
            "chr": data.get("seq_region_name"),
            "start": data.get("start"),
            "end": data.get("end"),
            "strand": data.get("strand"),
            "assembly": data.get("assembly_name"),
            "biotype_description": None,
        }

    def transcript_sequences(self, symbol: str, species: str = "homo_sapiens") -> list[dict[str, Any]]:
        """查询基因的转录本序列（cDNA）。"""
        gene = self.gene_by_symbol(symbol, species)
        if not gene.get("gene_id"):
            return []
        resp = self._http.get(
            f"sequence/id/{gene['gene_id']}",
            params={"type": "cdna", "multiple_sequences": "1"},
        )
        data = resp.json()
        if isinstance(data, dict) and data.get("error"):
            return []
        if isinstance(data, list):
            return [
                {"id": x.get("id", "").split(".")[0], "seq": x.get("seq", "")}
                for x in data
            ]
        return []

    def homologs(self, symbol: str, species: str = "homo_sapiens", target: str = "all") -> list[dict[str, Any]]:
        """查询同源基因（orthologs/paralogs）。

        用 /homology/symbol/ 端点（/homology/id/ 在部分基因上返回 404）。
        target 为 "all" 时省略 target_species 参数（默认全部）；
        指定物种时传逗号分隔的物种列表。
        """
        params: dict[str, Any] = {"content-type": "application/json"}
        if target and target != "all":
            params["target_species"] = target
        resp = self._http.get(f"homology/symbol/{species}/{symbol}", params=params)
        data = resp.json()
        homologs: list[dict[str, Any]] = []
        for group in (data.get("data") or []):
            for h in (group.get("homologies") or []):
                target_obj = h.get("target", {})
                if not target_obj:
                    continue
                homologs.append(
                    {
                        "type": h.get("type"),
                        "species": target_obj.get("species", "").split("_")[-1],
                        "gene_id": target_obj.get("id", "").split(".")[0],
                        "protein_id": target_obj.get("protein_id", ""),
                        "percent_id": h.get("target", {}).get("perc_id"),
                        "positives": h.get("target", {}).get("perc_pos"),
                        "identity": h.get("target", {}).get("perc_id"),
                    }
                )
        return homologs

    def close(self) -> None:
        self._http.close()
