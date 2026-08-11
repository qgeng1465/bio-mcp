"""OpenAlex 学术文献工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.openalex import OpenAlexClient


def register(server: Any) -> None:
    @server.tool(
        name="openalex_work_search",
        description=(
            "Search OpenAlex scholarly works. "
            "检索 OpenAlex 学术文献：输入主题或关键词（如 CRISPR gene editing、organ-on-chip），"
            "returns title/year/citations/authors/venue. "
            "返回标题、年份、被引、作者与期刊，用于文献调研与引用分析。"
        ),
    )
    def openalex_work_search(
        query: str,
        max_results: int = 5,
    ) -> str:
        """检索学术著作。

        Args:
            query: 检索词（如 CRISPR gene editing、single cell RNA-seq）。
            max_results: 返回条数（1-10）。
        """
        max_results = max(1, min(int(max_results), 10))
        client = OpenAlexClient()
        try:
            data = client.work_search(query, max_results)
        finally:
            client.close()
        if not data["works"]:
            return f"OpenAlex 未找到「{query}」。"
        lines = [f"# OpenAlex 文献检索「{query}」（共 {data['count']} 篇）", ""]
        for w in data["works"]:
            head = f"**{w['title']}**"
            if w.get("year"):
                head += f"（{w['year']}）"
            lines.append(f"- {head}")
            meta = []
            if w.get("authors"):
                meta.append(", ".join(w["authors"][:6]))
            if w.get("venue"):
                meta.append(w["venue"])
            if w.get("cited_by") is not None:
                meta.append(f"被引 {w['cited_by']} 次")
            if w.get("type"):
                meta.append(w["type"])
            if meta:
                lines.append(f"  {' · '.join(meta)}")
            if w.get("doi"):
                lines.append(f"  DOI: {w['doi']}")
        lines.append("")
        lines.append("来源：OpenAlex（全球学术著作索引）。")
        return "\n".join(lines)
