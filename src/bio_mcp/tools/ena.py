"""EBI ENA 欧洲核苷酸档案核酸序列工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.ena import ENAClient


def register(server: Any) -> None:
    @server.tool(
        name="ena_sequence_search",
        description=(
            "Search EBI ENA nucleotide sequences (microbes/viruses/plasmids). "
            "检索 ENA 欧洲核苷酸档案核酸序列（微生物/病毒/质粒）："
            "输入物种或关键词（如 tax_tree(562) 大肠杆菌、tax_tree(2697049) 新冠），"
            "returns accession/description/organism/tax_id. "
            "返回序列登录号、描述、物种与分类号，用于微生物与核酸研究。"
        ),
    )
    def ena_sequence_search(
        query: str,
        max_results: int = 10,
    ) -> str:
        """检索 ENA 核酸序列。

        Args:
            query: ENA 查询语法（如 tax_tree(562)、tax_tree(2697049)、accession=AP023253）。
            max_results: 返回条数（1-20）。
        """
        max_results = max(1, min(int(max_results), 20))
        client = ENAClient()
        try:
            data = client.sequence_search(query, max_results)
        finally:
            client.close()
        if not data["records"]:
            return f"ENA 未找到「{query}」的核酸序列。"
        lines = [f"# ENA 核酸序列检索「{query}」（返回 {data['count']} 条）", ""]
        for r in data["records"]:
            head = f"**{r['accession']}**"
            if r.get("scientific_name"):
                head += f" · {r['scientific_name']}"
            lines.append(f"- {head}")
            if r.get("description"):
                lines.append(f"  {r['description'][:160]}")
            if r.get("tax_id"):
                lines.append(f"  taxid {r['tax_id']}")
        lines.append("")
        lines.append("来源：EBI ENA（European Nucleotide Archive）。")
        return "\n".join(lines)
