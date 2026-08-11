"""NCBI Taxonomy 与 GEO 基因表达数据工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.ncbi import NCBIClient


def register(server: Any) -> None:
    @server.tool(
        name="taxonomy_lookup",
        description=(
            "Look up NCBI Taxonomy species classification. "
            "查询 NCBI Taxonomy 物种分类：输入物种名或 taxid（如 9606、human），"
            "returns scientific/common name, rank and lineage. "
            "返回学名、常用名、分类层级与谱系，用于确认物种的官方分类。"
        ),
    )
    def taxonomy_lookup(
        query: str,
    ) -> str:
        """查询物种分类。

        Args:
            query: 物种名或 taxid（如 9606、human、Homo sapiens）。
        """
        client = NCBIClient()
        try:
            data = client.taxonomy_lookup(query)
        finally:
            client.close()
        if not data["nodes"]:
            return f"NCBI Taxonomy 未找到「{query}」。"
        lines = [f"# 物种分类检索「{query}」（共 {data['count']} 条）", ""]
        for n in data["nodes"][:5]:
            rank = n.get("rank") or "no rank"
            common = f"（{n['common_name']}）" if n.get("common_name") else ""
            lines.append(f"- **{n['scientific_name']}{common}** — taxid {n['taxid']} · {rank}")
            if n.get("lineage"):
                lines.append(f"  谱系: {n['lineage'][:120]}")
        lines.append("")
        lines.append("来源：NCBI Taxonomy。")
        return "\n".join(lines)

    @server.tool(
        name="geo_dataset_search",
        description=(
            "Search NCBI GEO gene expression datasets. "
            "检索 NCBI GEO 基因表达数据集：按疾病/组织/实验类型（如 breast cancer、RNA-seq），"
            "returns GSE accession/title/platform/sample count/summary. "
            "返回 GSE 编号、标题、平台、样本数与摘要，用于表达谱研究找数据。"
        ),
    )
    def geo_dataset_search(
        query: str,
        max_results: int = 5,
    ) -> str:
        """检索 GEO 数据集。

        Args:
            query: 检索词（如 breast cancer expression、RNA-seq）。
            max_results: 返回条数（1-10）。
        """
        max_results = max(1, min(int(max_results), 10))
        client = NCBIClient()
        try:
            data = client.geo_search(query, max_results)
        finally:
            client.close()
        if not data["datasets"]:
            return f"GEO 未找到「{query}」的数据集。"
        lines = [f"# GEO 数据集检索「{query}」（共 {data['count']} 条）", "", ""]
        for d in data["datasets"]:
            lines.append(f"- **{d['accession']}**: {d['title']}")
            lines.append(f"  {d.get('gdstype') or '-'} · 平台 {d.get('gpl') or '-'} · {d.get('n_samples')} 样本 · {d.get('taxon') or '-'}")
            if d.get("summary"):
                lines.append(f"  {d['summary'][:150]}")
        lines.append("")
        lines.append("来源：NCBI GEO（GDS/GSE 系列）。")
        return "\n".join(lines)
