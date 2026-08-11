"""Europe PMC 全文文献检索工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.europepmc import EuropePMCClient


def register(server: Any) -> None:
    @server.tool(
        name="europepmc_search",
        description=(
            "Full-text literature search (Europe PMC, EBI). "
            "全文文献检索：比 PubMed 多了开放获取(OA)全文，"
            "returns title/journal/authors/DOI/open-access status. "
            "返回标题、期刊、作者、DOI、是否可获取全文，适合做文献综述。"
        ),
    )
    def europepmc_search(
        query: str,
        max_results: int = 5,
    ) -> str:
        """全文检索文献。

        Args:
            query: 检索式（如 BRCA1 AND breast cancer）。
            max_results: 返回条数（1-10）。
        """
        max_results = max(1, min(int(max_results), 10))
        client = EuropePMCClient()
        try:
            data = client.search(query, max_results)
        finally:
            client.close()
        if not data["articles"]:
            return f"Europe PMC 未找到「{query}」。"
        lines = [
            f"# Europe PMC 检索「{query}」（共 {data['count']} 条）",
            "",
        ]
        for a in data["articles"]:
            oa = "✅OA全文" if a["is_open_access"] else ""
            lines.append(f"- **{a['title']}**")
            lines.append(f"  {a['journal']} · {a['date']} · PMID {a['pmid']} {oa}")
            if a.get("doi"):
                lines.append(f"  DOI: {a['doi']}")
        lines.append("")
        lines.append("来源：Europe PMC (EBI)。OA 全文可通过 PMC 获取。")
        return "\n".join(lines)
