"""UCSC 基因组浏览器工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.ucsc import UCSCClient


def register(server: Any) -> None:
    @server.tool(
        name="ucsc_genome_info",
        description=(
            "Query UCSC Genome Browser. 查询 UCSC 基因组浏览器信息："
            "list available genome assemblies or inspect one (e.g. hg38/GRCh38) "
            "and its gene annotation tracks. 列出可用组装，或查看某组装及其基因注释轨道，"
            "for genomics research. 用于基因组学研究。"
        ),
    )
    def ucsc_genome_info(
        assembly: str = "",
        list_tracks: bool = False,
    ) -> str:
        """查询 UCSC 基因组。

        Args:
            assembly: 组装名（如 hg38、mm39）。留空则列出全部可用组装。
            list_tracks: 是否同时返回该组装的基因注释轨道。
        """
        client = UCSCClient()
        try:
            if not assembly:
                genomes = client.list_genomes()
                lines = [f"# UCSC 可用基因组组装（{len(genomes)} 个）", ""]
                for g in genomes[:40]:
                    lines.append(f"- **{g['name']}** — {g['organism']}")
                lines.append("")
                lines.append("提示：用 ucsc_genome_info 传入组装名（如 hg38）查看详情。")
                return "\n".join(lines)
            info = client.genome_info(assembly)
            tracks = client.gene_tracks(assembly) if list_tracks else []
        finally:
            client.close()
        if not info:
            return f"UCSC 未找到组装「{assembly}」。可用 ucsc_genome_info 列出全部组装。"
        lines = [f"# UCSC 组装 {info['name']}", ""]
        lines.append(f"- **物种**: {info.get('organism') or '-'} ({info.get('scientificName') or '-'})")
        lines.append(f"- **描述**: {info.get('description') or '-'}")
        if tracks:
            lines.append("")
            lines.append("## 基因注释轨道")
            lines.append("\n".join(f"- {t}" for t in tracks))
        lines.append("")
        lines.append("来源：UCSC Genome Browser (University of California, Santa Cruz)。")
        return "\n".join(lines)
