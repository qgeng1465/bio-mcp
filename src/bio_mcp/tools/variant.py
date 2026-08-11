"""变异注释工具（MyVariant.info + ClinVar via NCBI）。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.myvariant import MyVariantClient
from bio_mcp.core.ncbi import NCBIClient


def register(server: Any) -> None:
    @server.tool(
        name="variant_annotate",
        description=(
            "Annotate human genetic variants (MyVariant.info). "
            "注释人类基因变异：输入 HGVS（如 chr13:g.32911145G>A）或 rsID，"
            "returns allele frequency (GnomAD/1000G), functional predictions (SIFT/PolyPhen), "
            "gene and clinical significance. 返回人群频率、功能预测、基因与临床意义，"
            "for variant interpretation. 用于变异解读。"
        ),
    )
    def variant_annotate(
        variant: str,
    ) -> str:
        """注释基因变异。

        Args:
            variant: HGVS 格式（chr13:g.32911145G>A）或 rsID（如 rs180177832）。
        """
        v = variant.strip()
        client = MyVariantClient()
        try:
            d = client.annotate(v)
        finally:
            client.close()
        if not d.get("variant") and not d.get("rsid"):
            return f"MyVariant 未注释到「{v}」。\n格式示例：chr13:g.32911145G>A（chr+染色体:g.位置+ref>alt），或提供 rsID。"
        lines = [f"# 变异注释 {v}", ""]
        if d.get("rsid"):
            lines.append(f"- **rsID**: {d['rsid']}")
        if d.get("gene"):
            lines.append(f"- **基因**: {d['gene']}")
        if d.get("consequence"):
            lines.append(f"- **影响**: {d['consequence']}")
        if d.get("clinical_significance"):
            lines.append(f"- **临床意义**: {d['clinical_significance']}")
        lines.append("")
        lines.append("## 人群频率")
        lines.append(f"- GnomAD: {d.get('af_gnomad') or '-'}")
        lines.append(f"- 1000 Genomes: {d.get('af_1000g') or '-'}")
        if d.get("predictions"):
            lines.append("")
            lines.append("## 功能预测")
            for k, val in d["predictions"].items():
                lines.append(f"- {k}: {val}")
        lines.append("")
        lines.append("来源：MyVariant.info（整合 GnomAD/ClinVar/dbNSFP）。临床决策请咨询专业人士。")
        return "\n".join(lines)

    @server.tool(
        name="clinvar_query",
        description=(
            "Query ClinVar clinical variants (via NCBI E-utilities). "
            "查询 ClinVar 临床变异：输入基因名或变异，返回临床意义分类（致病/良性/意义不明），"
            "for clinical variant interpretation. 用于变异临床解读。"
        ),
    )
    def clinvar_query(
        query: str,
        max_results: int = 5,
    ) -> str:
        """查询 ClinVar 临床变异。

        Args:
            query: 基因名（如 BRCA1）或变异描述。
            max_results: 返回条数。
        """
        max_results = max(1, min(int(max_results), 10))
        client = NCBIClient()
        try:
            es = client.esearch("clinvar", query, retmax=max_results)
            ids = es["ids"]
            if not ids:
                return f"ClinVar 未找到「{query}」的变异。"
            articles = client.esummary("clinvar", ids)
        finally:
            client.close()
        lines = [f"# ClinVar 查询「{query}」（{es['count']} 条）", ""]
        for a in articles:
            title = a.get("title", "").strip()
            # ClinVar esummary 的 title 含基因与临床意义
            lines.append(f"- **{title}** (VariationID: {a.get('uid')})")
        lines.append("")
        lines.append("来源：NCBI ClinVar。完整意义分类请访问详情页。")
        return "\n".join(lines)
