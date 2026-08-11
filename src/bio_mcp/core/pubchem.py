"""PubChem PUG REST API 客户端。

化合物查询：名称/标识符 → 分子式/分子量/规范 SMILES/性质。
参考：https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest
"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.http import BioHTTP

BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"


class PubChemClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=20.0, rate_limit=0.5)

    def compound_by_name(self, name: str) -> dict[str, Any]:
        """按化合物名称查询基本信息。"""
        import urllib.parse

        safe = urllib.parse.quote(name)
        try:
            resp = self._http.get(
                f"compound/name/{safe}/property/CanonicalSMILES,IsomericSMILES,MolecularFormula,MolecularWeight,IUPACName,InChIKey/JSON"
            )
        except Exception as e:
            return {"error": f"未找到化合物「{name}」: {e}", "name": name}
        props = (resp.json().get("PropertyTable", {}).get("Properties") or [{}])[0]
        return {
            "name": name,
            "cid": props.get("CID"),
            "canonical_smiles": props.get("CanonicalSMILES"),
            "isomeric_smiles": props.get("IsomericSMILES"),
            "molecular_formula": props.get("MolecularFormula"),
            "molecular_weight": props.get("MolecularWeight"),
            "iupac_name": props.get("IUPACName"),
            "inchikey": props.get("InChIKey"),
        }

    def synonyms(self, name: str) -> list[str]:
        """查询化合物的同义词/别名。"""
        import urllib.parse

        safe = urllib.parse.quote(name)
        try:
            resp = self._http.get(f"compound/name/{safe}/synonyms/JSON")
        except Exception:
            return []
        return resp.json().get("InformationList", {}).get("Information", [{}])[0].get("Synonym", [])

    def close(self) -> None:
        self._http.close()
