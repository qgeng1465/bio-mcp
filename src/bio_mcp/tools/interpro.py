"""InterPro 蛋白结构域工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.interpro import InterProClient


def register(server: Any) -> None:
    @server.tool(
        name="protein_domains",
        description=(
            "Query protein structural domains from InterPro. "
            "查询蛋白的 InterPro 结构域/家族/位点注释（输入 UniProt accession），"
            "returns domain name/type for functional region analysis. "
            "返回结构域名、类型与位置，用于蛋白功能区域分析。"
        ),
    )
    def protein_domains(
        uniprot_acc: str,
    ) -> str:
        """查询蛋白结构域。

        Args:
            uniprot_acc: UniProt accession（如 P04637）。
        """
        client = InterProClient()
        try:
            entries = client.protein_entries(uniprot_acc)
        finally:
            client.close()
        if not entries:
            return f"InterPro 未找到「{uniprot_acc}」的结构域注释。请确认是有效 UniProt accession。"
        lines = [f"# {uniprot_acc} 蛋白结构域（{len(entries)} 个）", "", "| 结构域 | 类型 | 名称 |", "|--------|------|------|"]
        for e in entries[:30]:
            lines.append(f"| {e['accession']} | {e.get('type') or '-'} | {e.get('name') or '-'} |")
        lines.append("")
        lines.append("来源：InterPro (EBI)。可与 uniprot_annotate 联用。")
        return "\n".join(lines)
