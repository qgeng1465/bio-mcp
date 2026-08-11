"""UniProt 蛋白注释工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.uniprot import UniProtClient


def register(server: Any) -> None:
    @server.tool(
        name="uniprot_annotate",
        description=(
            "Query UniProt protein annotations. 查询 UniProt 蛋白注释："
            "protein name/gene/organism/length/function/Gene Ontology. "
            "蛋白名/基因/物种/长度/功能/GO 项，支持 accession（如 P04637）或基因名检索，"
            "for protein function interpretation. 用于蛋白功能解读。"
        ),
    )
    def uniprot_annotate(
        query: str,
        max_results: int = 3,
    ) -> str:
        """查询 UniProt 注释。

        Args:
            query: UniProt accession（P04637）或检索词（如 "TP53 human"）。
            max_results: 检索模式下最多返回的条目数。
        """
        max_results = max(1, min(int(max_results), 5))
        client = UniProtClient()
        try:
            results = client.search(query, max_results=max_results)
        finally:
            client.close()

        if not results:
            return f"UniProt 未检索到「{query}」。\n提示：accession 如 P04637 / Q9Y261；也可用 基因名+物种 检索。"
        lines: list[str] = []
        for i, r in enumerate(results, 1):
            genes = ", ".join(g for g in (r.get("gene") or []) if g)
            go = ", ".join(str(g) for g in (r.get("go_terms") or [])[:5])
            lines.append(f"### {i}. {r['protein_name'] or '-'}")
            lines.append(f"- **Accession**: {r['accession']}")
            if genes:
                lines.append(f"- **基因**: {genes}")
            lines.append(f"- **物种**: {r['organism']} | **长度**: {r['length']} aa")
            if r.get("function"):
                lines.append(f"- **功能**: {r['function'][:200]}")
            if go:
                lines.append(f"- **GO**: {go}")
            lines.append("")
        return "\n".join(lines)
