"""Ensembl 基因查询工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.ensembl import EnsemblClient


def register(server: Any) -> None:
    @server.tool(
        name="ensembl_gene_lookup",
        description=(
            "Look up gene by symbol in Ensembl. 按基因符号查询 Ensembl 基因信息："
            "Ensembl ID / chromosome location / biotype / description (GRCh38). "
            "Ensembl ID、染色体位置、生物型、描述，用于确认官方 ID 与坐标（GRCh38）。"
        ),
    )
    def ensembl_gene_lookup(
        symbol: str,
        species: str = "homo_sapiens",
    ) -> str:
        """查询 Ensembl 基因。

        Args:
            symbol: 基因符号（如 BRCA1、TP53、CYP2D6）。
            species: 物种（homo_sapiens / mus_musculus / danio_rerio...）。
        """
        client = EnsemblClient()
        try:
            g = client.gene_by_symbol(symbol, species)
        finally:
            client.close()
        if not g.get("gene_id"):
            return f"Ensembl 未找到基因「{symbol}」（{species}）。请检查符号拼写或物种代码。"
        return "\n".join([
            f"# {symbol} ({species})",
            "",
            f"- **Ensembl ID**: {g['gene_id']}",
            f"- **描述**: {g.get('description') or '-'}",
            f"- **生物型**: {g.get('biotype') or '-'}",
            f"- **位置**: chr{g['chr']}:{g['start']}-{g['end']} ({'+' if g['strand'] > 0 else '-'}链)",
            f"- **组装**: {g.get('assembly') or '-'}",
            "",
            "提示：可与 uniprot_annotate / string_interactions 联用做交叉验证。",
        ])

    @server.tool(
        name="ensembl_homologs",
        description=(
            "Query homologous genes (orthologs/paralogs) from Ensembl Compara. "
            "查询基因的同源基因（直系同源/旁系同源），返回物种、同源基因 ID、序列一致性，"
            "for evolutionary analysis and model organisms. 用于进化分析、模式生物研究。"
        ),
    )
    def ensembl_homologs(
        symbol: str,
        species: str = "homo_sapiens",
        target_species: str = "all",
    ) -> str:
        """查询同源基因。

        Args:
            symbol: 基因符号（如 BRCA1）。
            species: 查询物种（默认人类）。
            target_species: 目标物种（如 mus_musculus）。留空/all 返回全部同源（数据量大）。
        """
        client = EnsemblClient()
        try:
            try:
                hs = client.homologs(symbol, species, target=target_species)
            except Exception as e:
                return f"Ensembl 同源查询失败（网络可能超时）：{e}\n可指定 target_species（如 mus_musculus）缩小范围重试。"
        finally:
            client.close()
        if not hs:
            return f"未找到「{symbol}」的同源基因。请确认基因名。"
        lines = [f"# {symbol} 同源基因（{len(hs)} 个）", "", "| 类型 | 物种 | Ensembl ID | 一致性% |", "|------|------|-----------|---------|"]
        for h in hs[:30]:
            lines.append(f"| {h['type']} | {h['species']} | {h['gene_id']} | {h.get('identity') or '-'} |")
        lines.append("")
        lines.append("来源：Ensembl Compara。直系同源(ortholog)=不同物种同源；旁系同源(paralog)=同物种复制。")
        return "\n".join(lines)
