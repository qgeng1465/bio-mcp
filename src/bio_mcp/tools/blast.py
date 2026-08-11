"""BLAST 同源比对工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.ncbi import NCBIClient


def register(server: Any) -> None:
    @server.tool(
        name="blast_search",
        description=(
            "对 DNA 或蛋白序列做 NCBI BLAST 同源搜索，返回 top hits（accession/物种/E值/一致性/描述）。"
            "用于鉴定未知序列、找同源基因、验证引物。"
        ),
    )
    def blast_search(
        sequence: str,
        program: str = "blastn",
        database: str = "nt",
        max_hits: int = 10,
    ) -> str:
        """执行 BLAST 比对。

        Args:
            sequence: 目标序列（DNA 或蛋白，FASTA 头可省略）。
            program: blastn(核酸-核酸)/blastp(蛋白-蛋白)/tblastn(蛋白-核酸)/blastx(核酸-蛋白)。
            database: 数据库 nt(核酸)/nr(蛋白)/refseq_rna 等。
            max_hits: 返回的 top hits 数量。
        """
        if program == "blastp" and database == "nt":
            database = "nr"
        max_hits = max(1, min(int(max_hits), 25))
        client = NCBIClient()
        try:
            rid = client.blast_submit(sequence, program=program, db=database)
            result = client.blast_poll(rid)
        finally:
            client.close()

        # 解析结果（识别 top hits 表格）
        lines = result.splitlines()
        parsed: list[str] = []
        start = None
        for idx, line in enumerate(lines):
            if line.startswith("Sequences producing significant alignments"):
                start = idx + 2
                break
        if start is not None:
            for line in lines[start:]:
                if not line.strip():
                    break
                if len(parsed) >= max_hits:
                    break
                parsed.append(line.strip())
        header = f"BLAST {program} / {database} 完成，RID={rid}，Top {len(parsed) or max_hits} hits：\n"
        if parsed:
            return header + "\n".join(f"{i+1}. {p}" for i, p in enumerate(parsed))
        # 无表格时返回原始输出摘要
        summary = "\n".join(l for l in lines if l.strip())[:3000]
        return header + "（未能解析表格，返回原始输出摘要）\n```\n" + summary + "\n```"
