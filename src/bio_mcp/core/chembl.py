"""ChEMBL 药物活性数据库客户端。

ChEMBL（EBI）收录 240 万+ 化合物的生物活性数据（IC50/Ki 等）。
参考：https://www.ebi.ac.uk/chembl/api/data/docs
"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.http import BioHTTP

BASE = "https://www.ebi.ac.uk/chembl/api/data"


class ChEMBLClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=30.0, rate_limit=0.5)

    def search_compound(self, name: str, max_results: int = 5) -> list[dict[str, Any]]:
        """按名称搜索化合物（molecule/search 模糊匹配，返回 JSON）。"""
        out: list[dict[str, Any]] = []
        try:
            resp = self._http.get(
                "molecule/search",
                params={"q": name, "format": "json", "limit": max_results},
            )
            for m in resp.json().get("molecules", [])[:max_results]:
                out.append(self._parse_molecule(m))
        except Exception:
            pass
        return out

    def compound_by_id(self, chembl_id: str) -> dict[str, Any]:
        """按 ChEMBL ID（如 CHEMBL25）查询完整记录。"""
        resp = self._http.get(f"molecule/{chembl_id}.json")
        return self._parse_molecule(resp.json())

    def _parse_molecule(self, m: dict[str, Any]) -> dict[str, Any]:
        names = m.get("molecule_synonyms", [])
        synonyms = [n.get("synonyms", "") for n in names[:5] if n.get("synonyms")]
        return {
            "chembl_id": m.get("molecule_chembl_id"),
            "pref_name": m.get("pref_name"),
            "synonyms": synonyms,
            "smiles": (m.get("molecule_structures") or {}).get("canonical_smiles"),
            "molecular_formula": m.get("molecule_properties", {}).get("molecular_formula")
            if m.get("molecule_properties")
            else None,
            "molecular_weight": m.get("molecule_properties", {}).get("mw_freebase")
            if m.get("molecule_properties")
            else None,
            "target_count": m.get("target_count"),
            "max_phase": m.get("max_phase"),
        }

    def targets_for_compound(self, chembl_id: str, max_results: int = 5) -> list[dict[str, Any]]:
        """查询化合物的作用靶点（含 IC50/Ki 活性值）。"""
        out: list[dict[str, Any]] = []
        try:
            resp = self._http.get(
                "activity.json",
                params={"molecule_chembl_id": chembl_id, "limit": max_results},
            )
            for a in resp.json().get("activities", [])[:max_results]:
                tgt = a.get("target_chembl_id", "")
                out.append(
                    {
                        "target_chembl_id": tgt,
                        "target_pref_name": a.get("target_pref_name"),
                        "standard_type": a.get("standard_type"),
                        "standard_value": a.get("standard_value"),
                        "standard_units": a.get("standard_units"),
                        "standard_relation": a.get("standard_relation"),
                        "pchembl_value": a.get("pchembl_value"),
                    }
                )
        except Exception:
            pass
        return out

    def close(self) -> None:
        self._http.close()
