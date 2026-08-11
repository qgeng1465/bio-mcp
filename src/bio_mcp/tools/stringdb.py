"""STRING-db 蛋白互作网络工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.stringdb import STRINGClient


def register(server: Any) -> None:
    @server.tool(
        name="string_interactions",
        description=(
            "Query protein interaction network from STRING-db. "
            "查询蛋白互作网络（STRING-db）：给定一个或多个蛋白，返回互作关系及分数"
            "（综合分数越高越可信），for protein functional network analysis. "
            "用于蛋白功能网络分析。"
        ),
    )
    def string_interactions(
        proteins: str,
        species: int = 9606,
    ) -> str:
        """查询蛋白互作网络。

        Args:
            proteins: 蛋白名或 UniProt accession，逗号分隔（如 P04637,P38398）。
            species: NCBI taxonomy ID（人=9606，小鼠=10090）。
        """
        plist = [p.strip() for p in proteins.replace("\n", ",").split(",") if p.strip()]
        if not plist:
            return "请提供至少一个蛋白名或 accession。"
        client = STRINGClient()
        try:
            edges = client.network(",".join(plist), species=species)
        finally:
            client.close()
        if not edges:
            return f"STRING 未找到这些蛋白的互作关系（species={species}）。请检查蛋白名或物种 ID。"
        lines = [f"# STRING 蛋白互作网络（species={species}，{len(edges)} 条边）", "", "| 蛋白 A | 蛋白 B | 综合分数 |", "|--------|--------|---------|"]
        for e in sorted(edges, key=lambda x: -(x.get("score") or 0)):
            lines.append(f"| {e['protein_a']} | {e['protein_b']} | {e['score']} |")
        lines.append("")
        lines.append("分数范围 0-1，>0.4 一般视为中高置信度。来源：STRING-db v12。")
        return "\n".join(lines)
