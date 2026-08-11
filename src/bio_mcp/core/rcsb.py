"""RCSB Protein Data Bank (PDB) 客户端。

支持按 PDB ID 拉取结构摘要（graphql 查询）与下载 mmCIF/PDB 文件。
参考：https://data.rcsb.org/
"""
from __future__ import annotations

from typing import Any, Optional

from bio_mcp.core.http import BioHTTP

BASE = "https://data.rcsb.org/rest/v1"


class RCSBClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=30.0, rate_limit=0.5)

    def entry_summary(self, pdb_id: str) -> dict[str, Any]:
        """按 PDB ID 获取结构条目摘要。"""
        pid = pdb_id.strip().lower()
        resp = self._http.get(f"core/entry/{pid}")
        data = resp.json()
        # 提取关键字段
        struct = data.get("struct", {})
        exptl = data.get("rcsb_entry_info", {})
        return {
            "pdb_id": pid.upper(),
            "title": data.get("struct", {}).get("title", ""),
            "resolution": exptl.get("resolution_combined", []),
            "methods": data.get("exptl", [{}])[0].get("method", "") if data.get("exptl") else "",
            "organism": [
                o.get("organism_scientific", "")
                for o in data.get("rcsb_entity_source_organism", [])
                if o.get("organism_scientific")
            ],
            "deposited": data.get("rcsb_accession_info", {}).get("deposit_date", ""),
            "release_date": data.get("rcsb_accession_info", {}).get("initial_release_date", ""),
            "polymer_entities": [
                e.get("rcsb_polymer_entity_container_identifiers", {}).get("auth_asym_id", "")
                for e in data.get("rcsb_entry_container_identifiers", {}).get("non_polymer_entity_ids", [])
            ],
        }

    def polymer_entity_info(self, pdb_id: str, entity_id: int = 1) -> Optional[dict[str, Any]]:
        """获取某链的序列/命名。"""
        pid = pdb_id.strip().lower()
        resp = self._http.get(f"core/polymer_entity/{pid}/{entity_id}")
        data = resp.json()
        comp_ids = data.get("rcsb_polymer_entity_sequence", {}).get("one_letter_codes", {}).get("monomers", [])
        return {
            "entity_id": entity_id,
            "description": data.get("rcsb_polymer_entity", {}).get("pdbx_description", ""),
            "sequence": "".join(comp_ids) if comp_ids else "",
            "source_organism": data.get("rcsb_polymer_entity_container_identifiers", {}).get(
                "pdbx_description", ""
            ),
        }

    def download_mmcif(self, pdb_id: str) -> str:
        """下载原始 mmCIF 文件文本。"""
        pid = pdb_id.strip().lower()
        resp = self._http.get(f"core/entry/{pid}.cif")
        return resp.text

    def close(self) -> None:
        self._http.close()
