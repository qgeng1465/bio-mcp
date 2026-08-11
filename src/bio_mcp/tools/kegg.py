"""KEGG 通路查询工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.kegg import KEGGClient


def register(server: Any) -> None:
    @server.tool(
        name="kegg_pathway_search",
        description=(
            "Search KEGG pathways by keyword. 按关键字搜索 KEGG 通路（如 'breast cancer'、'apoptosis'），"
            "returns pathway IDs and names. 返回通路 ID 与名称，用于找到目标通路编号。"
        ),
    )
    def kegg_pathway_search(
        keyword: str,
    ) -> str:
        """搜索 KEGG 通路。

        Args:
            keyword: 通路关键字（如 breast cancer、glycolysis、apoptosis）。
        """
        client = KEGGClient()
        try:
            paths = client.find_pathways(keyword)
        finally:
            client.close()
        if not paths:
            return f"KEGG 未找到含「{keyword}」的通路。"
        lines = [f"# KEGG 通路搜索结果（{len(paths)} 条）", "", "| ID | 通路名 |", "|----|--------|"]
        for p in paths:
            lines.append(f"| {p['id']} | {p['name'][:60]} |")
        lines.append("")
        lines.append("提示：用 kegg_pathway_genes 查询某通路下的基因。")
        return "\n".join(lines)

    @server.tool(
        name="kegg_pathway_genes",
        description=(
            "List genes in a KEGG pathway. 查询 KEGG 通路包含的基因列表（如 hsa05224=Breast cancer），"
            "returns the genes in the pathway. 返回该通路下的基因，用于了解通路的分子组成。"
        ),
    )
    def kegg_pathway_genes(
        pathway_id: str,
    ) -> str:
        """查询通路的基因组成。

        Args:
            pathway_id: KEGG 通路 ID（如 hsa05224、hsa04210）。
        """
        client = KEGGClient()
        try:
            genes = client.pathway_genes_by_pathway(pathway_id)
        finally:
            client.close()
        if not genes:
            return f"未找到通路「{pathway_id}」的基因。请用 hsa 前缀的 ID（如 hsa05224）。"
        return f"# KEGG {pathway_id} 基因列表（{len(genes)} 个）\n\n" + "、".join(genes) + \
               f"\n\n来源：KEGG REST API。可与 gene_enrichment 交叉验证。"
