"""MyVariant.info 变异注释客户端。

HGVS/chr:g.位置 → 人群频率(GnomAD/1000G)、功能预测(SIFT/PolyPhen/ClinVar)、dbSNP。
参考：https://docs.myvariant.info/
"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.http import BioHTTP

BASE = "https://myvariant.info/v1"


class MyVariantClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=20.0, rate_limit=0.3)

    def annotate(self, variant: str) -> dict[str, Any]:
        """注释单个变异。variant 格式：chr13:g.32911145G>A / chr7:g.117559590C>T 等。"""
        v = variant.strip().replace("g.", "g.")
        resp = self._http.get(f"variant/{v}")
        data = resp.json()
        # 提取关键字段
        gnomad = data.get("gnomad_exome") or {}
        clinvar = data.get("clinvar") or {}
        dbnsfp = data.get("dbnsfp") or {}
        rs = data.get("dbsnp", {}).get("rsid") or data.get("_id", "").split(":")[-1]
        # 提取功能预测
        predictions = {}
        sift = dbnsfp.get("sift", {}) or {}
        pp2 = dbnsfp.get("polyphen2", {}) or {}
        if sift.get("pred") or sift.get("hdiv_pred"):
            predictions["SIFT"] = sift.get("pred") or sift.get("hdiv_pred")
        if pp2.get("hdiv_pred"):
            predictions["PolyPhen"] = pp2["hdiv_pred"]
        return {
            "variant": v,
            "rsid": rs if str(rs) != "None" else None,
            "gene": (clinvar.get("gene", {}).get("symbol") if isinstance(clinvar, dict) else None)
                    or (data.get("cadd", {}).get("gene") if data.get("cadd") else None),
            "clinical_significance": clinvar.get("clinical_significance", {}).get("description") if isinstance(clinvar, dict) else None,
            "af_gnomad": gnomad.get("af"),
            "af_1000g": (data.get("1000g") or {}).get("af"),
            "consequence": dbnsfp.get("aapos"),
            "predictions": predictions,
            "hgvs": data.get("hgvs"),
        }

    def close(self) -> None:
        self._http.close()
