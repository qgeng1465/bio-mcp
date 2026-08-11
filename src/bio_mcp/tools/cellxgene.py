"""CELLxGENE 单细胞数据检索工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.cellxgene import CellxGeneClient


def register(server: Any) -> None:
    @server.tool(
        name="cellxgene_search",
        description=(
            "Search CELLxGENE (CZ) single-cell transcriptome datasets. "
            "检索 CELLxGENE 单细胞转录组数据：按疾病/组织/关键词匹配已发布数据集"
            "（含类器官、肿瘤、免疫等单细胞图谱），for finding single-cell data. "
            "用于单细胞研究找数据。"
        ),
    )
    def cellxgene_search(
        query: str,
        max_results: int = 5,
    ) -> str:
        """检索单细胞数据集。

        Args:
            query: 关键词（如 lung cancer、organoid、macrophage）。
            max_results: 返回条数（1-10）。
        """
        max_results = max(1, min(int(max_results), 10))
        client = CellxGeneClient()
        try:
            hits = client.search_datasets(query, max_results)
        finally:
            client.close()
        if not hits:
            return f"CELLxGENE 未找到匹配「{query}」的数据集。"
        lines = [f"# CELLxGENE 单细胞数据集（关键词：{query}）", "", ""]
        for d in hits:
            lines.append(f"- **{d['name']}**")
            if d.get("description"):
                lines.append(f"  {d['description']}")
            lines.append(f"  datasets: {d['dataset_count']} · 链接: https://cellxgene.cziscience.com/collections/{d['collection_id']}")
        lines.append("")
        lines.append("来源：CZ CELLxGENE Census（CZI）。单细胞/类器官研究数据搜索。")
        return "\n".join(lines)
