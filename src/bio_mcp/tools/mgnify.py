"""EBI MGnify 微生物组研究工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.mgnify import MGnifyClient


def register(server: Any) -> None:
    @server.tool(
        name="microbiome_study_search",
        description=(
            "Search EBI MGnify microbiome metagenomics studies. "
            "检索 MGnify 微生物组研究（细菌/古菌/病毒宏基因组）："
            "输入宿主或栖息地（如 gut microbiome、human、soil），"
            "returns study accession/name/samples/bioproject. "
            "返回研究编号、名称、样本数与生物项目，用于微生物组学研究。"
        ),
    )
    def microbiome_study_search(
        query: str,
        max_results: int = 5,
    ) -> str:
        """检索微生物组研究。

        Args:
            query: 检索词（如 gut microbiome、human、soil、T2D）。
            max_results: 返回条数（1-10）。
        """
        max_results = max(1, min(int(max_results), 10))
        client = MGnifyClient()
        try:
            data = client.study_search(query, max_results)
        finally:
            client.close()
        if not data["studies"]:
            return f"MGnify 未找到「{query}」的微生物组研究。"
        lines = [f"# MGnify 微生物组研究「{query}」（共 {data['count']} 条）", ""]
        for s in data["studies"]:
            lines.append(f"- **{s['accession']}**: {s['name'] or '(未命名)'}")
            parts = []
            if s.get("samples") is not None:
                parts.append(f"{s['samples']} 样本")
            if s.get("bioproject"):
                parts.append(s["bioproject"])
            if s.get("centre"):
                parts.append(s["centre"])
            if parts:
                lines.append(f"  {' · '.join(parts)}")
            if s.get("abstract"):
                lines.append(f"  {s['abstract'][:200]}")
        lines.append("")
        lines.append("来源：EBI MGnify（微生物组宏基因组数据库）。")
        return "\n".join(lines)
