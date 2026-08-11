"""EBI Metabolights 代谢组学工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.metabolights import MetabolightsClient


def register(server: Any) -> None:
    @server.tool(
        name="metabolomics_study",
        description=(
            "Get EBI Metabolights metabolomics study details. "
            "查询 Metabolights 代谢组学研究：按 MTBLS 编号（如 MTBLS1），"
            "returns title/description/technology/design/factors. "
            "返回研究标题、描述、检测技术（NMR/质谱）、实验设计与因子。"
        ),
    )
    def metabolomics_study(
        study_id: str,
    ) -> str:
        """查询代谢组学研究详情。

        Args:
            study_id: Metabolights 研究编号（如 MTBLS1）。
        """
        client = MetabolightsClient()
        try:
            d = client.study_detail(study_id)
        finally:
            client.close()
        if not d.get("title") and not d.get("accession"):
            return f"Metabolights 未找到研究「{study_id}」。"
        lines = [f"# 代谢组学研究：{d['accession']}", ""]
        lines.append(f"- **标题 / Title**: {d['title'] or '（无标题）'}")
        if d.get("description"):
            lines.append(f"- **描述 / Description**: {d['description'][:300]}")
        if d.get("status"):
            lines.append(f"- **状态 / Status**: {d['status']}")
        if d.get("technologies"):
            lines.append(f"- **检测技术 / Technology**: {', '.join(d['technologies'])}")
        if d.get("designs"):
            lines.append(f"- **设计 / Design**: {', '.join(d['designs'])}")
        if d.get("factors"):
            lines.append(f"- **实验因子 / Factors**: {', '.join(d['factors'])}")
        if d.get("assay_count"):
            lines.append(f"- **检测数 / Assays**: {d['assay_count']}")
        if d.get("submission_date") or d.get("publication_date"):
            dates = " / ".join(x for x in (d["submission_date"], d["publication_date"]) if x)
            lines.append(f"- **日期 / Dates**: {dates}")
        if d.get("study_url"):
            lines.append(f"- **链接**: {d['study_url']}")
        lines.append("")
        lines.append("来源：EBI Metabolights 代谢组学数据库。")
        return "\n".join(lines)

    @server.tool(
        name="metabolomics_latest",
        description=(
            "List latest EBI Metabolights metabolomics studies. "
            "列出 Metabolights 最新的代谢组学研究编号，"
            "returns MTBLS accession list for browsing. "
            "返回最新研究编号列表，便于浏览代谢组学数据。"
        ),
    )
    def metabolomics_latest(
        limit: int = 8,
    ) -> str:
        """列出最新代谢组学研究。

        Args:
            limit: 返回条数（1-15）。
        """
        limit = max(1, min(int(limit), 15))
        client = MetabolightsClient()
        try:
            studies = client.list_studies(limit)
        finally:
            client.close()
        if not studies:
            return "Metabolights 暂无研究列表。"
        lines = [f"# Metabolights 最新研究（{len(studies)} 条）", ""]
        for s in studies:
            lines.append(f"- **{s}**: https://www.ebi.ac.uk/metabolights/{s}")
        lines.append("")
        lines.append("来源：EBI Metabolights。")
        return "\n".join(lines)
