"""PubMed 文献检索工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.ncbi import NCBIClient


def register(server: Any) -> None:
    @server.tool(
        name="pubmed_search",
        description=(
            "检索 PubMed 生物医学文献，返回标题/作者/期刊/年份/PMID/DOI。"
            "用于文献综述、开题、课题调研、循证检索。"
            "参数 term 用 PubMed 查询语法（如 'BRCA1 AND breast cancer[Title]'）。"
        ),
    )
    def pubmed_search(
        term: str,
        max_results: int = 10,
        sort_by: str = "relevance",
    ) -> str:
        """检索 PubMed 文献。

        Args:
            term: PubMed 查询词，支持 field 限定与布尔逻辑（如 "PD-L1 immunotherapy"）。
            max_results: 返回条数，1-20。
            sort_by: 排序，relevance=相关度 / pub date=最新。
        """
        max_results = max(1, min(int(max_results), 20))
        sort = None if sort_by == "relevance" else sort_by
        client = NCBIClient()
        try:
            data = client.pubmed_search(term, retmax=max_results, sort=sort)
        finally:
            client.close()

        if not data["articles"]:
            return f"PubMed 未检索到符合「{term}」的文献（命中总数 {data['count']}）。\n可尝试：加引号、改 field 限定、或用更宽泛的关键词。"

        lines = [
            f"PubMed 检索：`{data['query']}`",
            f"命中 {data['count']} 篇，显示前 {len(data['articles'])} 篇：",
            "",
        ]
        for i, a in enumerate(data["articles"], 1):
            authors = ", ".join(
                f"{x.get('name','')}" for x in (a.get("authors") or [])[:3]
            )
            if len(a.get("authors") or []) > 3:
                authors += " et al."
            lines.append(f"### {i}. {a['title']}")
            lines.append(f"- 作者: {authors}")
            lines.append(f"- 期刊: {a['journal']} ({a['date']})")
            meta = [f"PMID: {a['pmid']}"]
            if a.get("doi"):
                meta.append(f"DOI: {a['doi']}")
            lines.append(f"- { ' | '.join(meta) }")
            lines.append("")
        return "\n".join(lines)
