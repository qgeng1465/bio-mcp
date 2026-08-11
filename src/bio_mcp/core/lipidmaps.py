"""LIPID MAPS 客户端：脂质结构与标识符检索。

LIPID MAPS（https://www.lipidmaps.org）是脂质组学权威数据库，
按 LIPID MAPS 分类（脂肪酸 / 甘油脂 / 鞘脂 / 甾醇等）编号 LM 前缀。
API：/rest/compound/lm_id/{id}/{resource}.json，免鉴权。
参考：https://www.lipidmaps.org/resources/rest
"""
from __future__ import annotations

from typing import Any, Optional

from bio_mcp.core.http import BioHTTP

BASE = "https://www.lipidmaps.org/rest"

# 按 LM ID 可获取的资源
_RESOURCES = (
    "name",
    "formula",
    "smiles",
    "inchi_key",
    "pubchem_cid",
    "hmdb_id",
    "kegg_id",
    "chebi_id",
)


class LipidMapsClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=20.0)

    # ---- 按 LM ID 查询脂质 ----
    def lipid_lookup(
        self,
        lm_id: str,
        resources: Optional[tuple[str, ...]] = _RESOURCES,
    ) -> dict[str, Any]:
        """按 LIPID MAPS 编号查询脂质结构信息。

        lm_id 示例：
          LMFA01030001    花生四烯酸（Arachidonic acid）
          LMGP01010001    磷脂酰胆碱（Phosphatidylcholine）
        """
        lm_id = lm_id.strip().upper()
        out: dict[str, Any] = {"lm_id": lm_id}
        for res in resources or ():
            try:
                resp = self._http.get(f"compound/lm_id/{lm_id}/{res}/json")
                data = resp.json()
            except Exception:  # 该资源对该脂质可能不存在
                continue
            if not isinstance(data, dict):
                continue
            val = data.get(res)
            if val in (None, "", {}):
                val = data.get("input")
            if val not in (None, "", {}):
                out[res] = val
        return out

    def close(self) -> None:
        self._http.close()
