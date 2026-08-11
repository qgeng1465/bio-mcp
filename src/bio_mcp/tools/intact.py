"""EBI IntAct 实验分子互作工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.intact import IntActClient


def register(server: Any) -> None:
    @server.tool(
        name="intact_interactions",
        description=(
            "Search EBI IntAct experimentally-validated molecular interactions. "
            "检索 IntAct 实验分子互作：输入基因或蛋白（如 TP53、P04637），"
            "returns interacting partners/detection method/evidence. "
            "返回互作伙伴、检测方法与文献证据，用于验证蛋白互作网络。"
        ),
    )
    def intact_interactions(
        query: str,
        max_results: int = 10,
    ) -> str:
        """检索实验分子互作。

        Args:
            query: 基因或蛋白名 / UniProt 编号（如 TP53、P04637、Q9Y2B4）。
            max_results: 返回条数（1-20）。
        """
        max_results = max(1, min(int(max_results), 20))
        client = IntActClient()
        try:
            data = client.find_interactions(query, max_results)
        finally:
            client.close()
        if not data["interactions"]:
            return f"IntAct 未找到「{query}」的互作。"
        lines = [f"# IntAct 实验互作「{query}」（共 {data['count']} 条）", ""]
        shown = 0
        for it in data["interactions"]:
            a, b = it.get("molecule_a", "?"), it.get("molecule_b", "?")
            if a == b and a == "?":
                continue
            lines.append(f"- **{a}** ⇄ **{b}**")
            parts = []
            if it.get("detection_method"):
                parts.append(it["detection_method"])
            if it.get("miscore") is not None:
                parts.append(f"MI-score {it['miscore']}")
            if it.get("pubmed"):
                parts.append(f"PubMed {it['pubmed']}")
            if parts:
                lines.append(f"  {' · '.join(parts)}")
            shown += 1
            if shown >= 10:
                break
        lines.append("")
        lines.append("来源：EBI IntAct（实验分子互作数据库）。")
        return "\n".join(lines)
