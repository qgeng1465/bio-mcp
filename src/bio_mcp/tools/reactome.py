"""Reactome 生物通路工具。"""
from __future__ import annotations

from typing import Any, Optional

from bio_mcp.core.reactome import ReactomeClient


def register(server: Any) -> None:
    @server.tool(
        name="reactome_pathway_search",
        description=(
            "Search Reactome biological pathways. "
            "检索 Reactome 生物通路：输入通路名或生物过程（如 apoptosis、glycolysis、DNA repair），"
            "returns stId/name/species/summation. "
            "返回通路编号、名称、物种与摘要，用于信号转导与代谢通路研究。"
        ),
    )
    def reactome_pathway_search(
        query: str,
        max_results: int = 5,
        species: Optional[str] = "9606",
    ) -> str:
        """检索生物通路。

        Args:
            query: 通路名或过程（如 apoptosis、glycolysis、DNA repair）。
            max_results: 返回条数（1-10）。
            species: NCBI Taxonomy id，默认 9606（人）；留空表示不限物种。
        """
        max_results = max(1, min(int(max_results), 10))
        client = ReactomeClient()
        try:
            data = client.pathway_search(query, max_results, species)
        finally:
            client.close()
        if not data["pathways"]:
            return f"Reactome 未找到通路「{query}」。"
        lines = [f"# Reactome 通路检索「{query}」（共 {data['count']} 条）", ""]
        for p in data["pathways"]:
            head = f"**{p['name']}** · {p['stId']}"
            if p.get("species"):
                head += f" · {p['species']}"
            lines.append(f"- {head}")
            if p.get("summation"):
                lines.append(f"  {p['summation'][:180]}")
        lines.append("")
        lines.append("来源：Reactome（人工策划的生物通路数据库）。")
        return "\n".join(lines)
