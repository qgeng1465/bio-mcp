"""EBI Metabolights 代谢组学客户端：研究检索与详情。

Metabolights（https://www.ebi.ac.uk/metabolights）是 EBI 的代谢组学
数据仓库：收录代谢物、代谢通路、临床/环境代谢组学研究（MTBLS 编号）。
API：/ws/studies（列表）与 /ws/studies/{id}（详情），免鉴权。
参考：https://www.ebi.ac.uk/metabolights/ws
"""
from __future__ import annotations

from typing import Any, Optional

from bio_mcp.core.http import BioHTTP

BASE = "https://www.ebi.ac.uk/metabolights/ws"


class MetabolightsClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=30.0)

    # ---- 研究列表（最新公开研究）----
    def list_studies(self, limit: int = 10) -> list[str]:
        """返回最新的公开研究编号列表（如 MTBLS1）。"""
        resp = self._http.get("studies")
        data = resp.json()
        return (data.get("content") or [])[:limit]

    # ---- 研究详情 ----
    def study_detail(self, study_id: str) -> dict[str, Any]:
        """按 MTBLS 编号查询研究详情（标题/描述/设计/技术类型/因子）。"""
        sid = study_id.strip().upper()
        resp = self._http.get(f"studies/{sid}")
        data = resp.json()
        inv = data.get("isaInvestigation", {}) or {}
        study = (inv.get("studies") or [{}])[0] or {}
        assays = study.get("assays") or []
        # 测量/技术类型（如 NMR、mass spectrometry）
        tech_types: list[str] = []
        for a in assays:
            mt = a.get("measurementType") or {}
            tt = a.get("technologyType") or {}
            tech_types.append(
                f"{mt.get('annotationValue') or mt.get('name') or ''} "
                f"({tt.get('annotationValue') or tt.get('name') or ''})"
            )
        # 设计描述符（如 diabetes mellitus）
        designs = [
            (dd.get("annotationValue") or "").strip()
            for dd in (study.get("studyDesignDescriptors") or [])
            if (dd.get("annotationValue") or "").strip()
        ]
        # 实验因子（如 Gender/Age）
        factors = [
            (f.get("factorName") or "").strip()
            for f in (study.get("factors") or [])
            if (f.get("factorName") or "").strip()
        ]
        return {
            "accession": inv.get("identifier") or sid,
            "title": (inv.get("title") or "").strip(),
            "description": (inv.get("description") or "").strip(),
            "submission_date": inv.get("submissionDate", ""),
            "publication_date": inv.get("publicReleaseDate", ""),
            "status": (data.get("mtblsStudy", {}) or {}).get("studyStatus", ""),
            "assay_count": len(assays),
            "technologies": [t for t in tech_types if t.strip() and t.strip() != " ()"],
            "designs": designs,
            "factors": factors,
            "study_url": (data.get("mtblsStudy", {}) or {}).get("studyHttpUrl", ""),
        }

    def close(self) -> None:
        self._http.close()
