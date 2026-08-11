"""GO/KEGG 富集分析工具（Enrichr 引擎）。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.enrichr import DEFAULT_LIBS, EnrichrClient


def register(server: Any) -> None:
    @server.tool(
        name="gene_enrichment",
        description=(
            "对基因列表做 GO/KEGG/Reactome 通路富集分析（Enrichr 引擎），"
            "返回显著富集项（通路名/p值/校正p值/重叠基因）。"
            "用于转录组/蛋白组/单细胞的差异基因功能解读。"
        ),
    )
    def gene_enrichment(
        genes: str,
        library: str = "GO_Biological_Process_2021",
        max_terms: int = 15,
    ) -> str:
        """基因富集分析。

        Args:
            genes: 基因符号列表，逗号或换行分隔（如 "BRCA1,TP53,EGFR,ATM"）。
            library: 基因集库。GO_Biological_Process_2021 / GO_Molecular_Function_2021 / GO_Cellular_Component_2021 / KEGG_2021_Human / Reactome_2022 / WikiPathway_2021_Human。
            max_terms: 最多返回的显著项数量。
        """
        gene_list = [g.strip().upper() for g in genes.replace("\n", ",").split(",") if g.strip()]
        if len(gene_list) < 2:
            return "至少需要 2 个基因。用逗号或换行分隔，如：BRCA1,TP53,EGFR"
        if library not in DEFAULT_LIBS:
            return (
                f"未知基因集库：{library}。可选：\n"
                + "\n".join(f"- {k}（{v}）" for k, v in DEFAULT_LIBS.items())
            )
        max_terms = max(1, min(int(max_terms), 30))
        client = EnrichrClient()
        try:
            data = client.enrich(gene_list, background_type=library, max_terms=max_terms)
        finally:
            client.close()

        if not data["significant_terms"]:
            return (
                f"共测试 {data['total_tested']} 个通路，未发现显著富集项"
                f"（{len(gene_list)} 个基因, {data['library_name']}, p<0.05）。\n"
                "提示：检查基因符号是否正确（如人源基因需大写），或换用其他基因集库。"
            )

        lines = [
            f"# 基因富集分析（{data['library_name']}）",
            "",
            f"输入 {len(gene_list)} 个基因，在 {data['total_tested']} 个通路中"
            f"发现 {len(data['significant_terms'])} 个显著富集项（p<0.05）：",
            "",
            "| # | 通路/GO 项 | p 值 | 校正 p | 重叠基因 |",
            "|---|-----------|------|--------|----------|",
        ]
        for i, t in enumerate(data["significant_terms"], 1):
            genes_in = ", ".join(t["genes"][:5]) + ("…" if len(t["genes"]) > 5 else "")
            p = f"{t['p_value']:.2e}"
            adj = f"{t['adjusted_p_value']:.2e}" if t.get("adjusted_p_value") else "-"
            lines.append(f"| {i} | {t['term'][:40]} | {p} | {adj} | {genes_in} |")
        lines.append("")
        lines.append("来源：Enrichr (Ma'ayan Lab)。建议结合生物学背景解读，q 值同样需关注。")
        return "\n".join(lines)
