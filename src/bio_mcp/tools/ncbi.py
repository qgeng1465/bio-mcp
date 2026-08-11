"""NCBI 序列下载工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.ncbi import NCBIClient


def register(server: Any) -> None:
    @server.tool(
        name="ncbi_fetch_sequence",
        description=(
            "Download nucleotide/protein sequences (FASTA) from NCBI. "
            "从 NCBI 下载核酸/蛋白序列（FASTA），支持 accession、gene symbol、关键词。"
            "DB options: nucleotide/gene/protein. 数据库可选 nucleotide/gene/protein，"
            "for getting reference sequences for downstream analysis. "
            "用于获取参考序列做下游分析。"
        ),
    )
    def ncbi_fetch_sequence(
        query: str,
        db: str = "nucleotide",
        rettype: str = "fasta",
        max_ids: int = 3,
    ) -> str:
        """下载 NCBI 序列（FASTA 格式）。

        Args:
            query: accession（如 NM_007294.4）或 gene/关键词（如 CYP2D6[Gene Name]）。
            db: 数据库 nucleotide/gene/protein/assembly。
            rettype: 返回格式 fasta 或 gb（GenBank）。
            max_ids: 最多取前 N 条记录，1-5。
        """
        max_ids = max(1, min(int(max_ids), 5))
        client = NCBIClient()
        try:
            es = client.esearch(db, query, retmax=max_ids)
            ids = es["ids"]
            if not ids:
                return f"NCBI {db} 未检索到「{query}」。\n提示：查蛋白序列用 db=protein，查核酸用 db=nucleotide；基因名加 [Gene Name]。"
            if rettype == "gb":
                text = client.efetch(db, ids, rettype="gb", retmode="text")
                return f"```\n{text.strip()[:8000]}\n```"
            fasta = client.efetch(db, ids, rettype="fasta", retmode="text")
        finally:
            client.close()
        return f"命中 {es['count']} 条，取前 {len(ids)} 条（NCBI {db}）：\n```\n{fasta.strip()[:8000]}\n```"
