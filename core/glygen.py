"""GlyGen 糖组学客户端：糖苷结构、蛋白糖基化、糖蛋白互作。

GlyGen（https://www.glygen.org）整合糖生物学的权威数据：
糖苷结构（GlyTouCan）、糖蛋白、糖基转移酶、糖苷酶等，全库免鉴权。
API 使用 POST + JSON body；详情端点为路径参数 + 空 body。
参考：https://api.glygen.org/swagger.json
"""
from __future__ import annotations

from typing import Any, Optional

from bio_mcp.core.http import BioHTTP

BASE = "https://api.glygen.org"


class GlyGenClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=30.0)

    # ---- 糖苷结构详情 ----
    def glycan_detail(self, glytoucan_ac: str) -> dict[str, Any]:
        """按 GlyTouCan 编号（如 G00051MO）查询糖苷结构详情。

        返回组成单糖、质量、糖苷键序列、相关蛋白/酶等信息。
        """
        ac = glytoucan_ac.strip().upper()
        resp = self._http.post(f"glycan/detail/{ac}/", json={})
        return resp.json()

    # ---- 蛋白糖基化详情 ----
    def protein_detail(self, uniprot_acc: str) -> dict[str, Any]:
        """按 UniProt 编号（如 P04637）查询蛋白的糖基化信息。

        返回蛋白糖苷/糖基化位点、序列、名称、跨库编号等。
        """
        acc = uniprot_acc.strip().upper()
        resp = self._http.post(f"protein/detail/{acc}/", json={})
        return resp.json()

    # ---- 糖苷→糖蛋白（该糖修饰哪些蛋白）----
    def glycan_to_glycoproteins(
        self, tax_id: str, glytoucan_ac: str
    ) -> dict[str, Any]:
        """查询某个糖苷在某物种下修饰的糖蛋白列表。"""
        resp = self._http.get(
            f"usecases/glycan_to_glycoproteins/{tax_id}/{glytoucan_ac.strip().upper()}"
        )
        data = resp.json()
        return data

    # ---- 物种→糖基转移酶 ----
    def species_glycosyltransferases(self, tax_id: str) -> dict[str, Any]:
        """查询某物种的全部糖基转移酶（glycosyltransferases）。"""
        resp = self._http.get(f"usecases/species_to_glycosyltransferases/{tax_id}")
        return resp.json()

    def close(self) -> None:
        self._http.close()
