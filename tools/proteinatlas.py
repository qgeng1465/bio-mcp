"""Human Protein Atlas（HPA）蛋白组织表达工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.proteinatlas import ProteinAtlasClient


def register(server: Any) -> None:
    @server.tool(
        name="protein_tissue_expression",
        description=(
            "Get Human Protein Atlas tissue expression profile. "
            "查询蛋白组织表达图谱：按 Ensembl 基因号（如 ENSG00000141510），"
            "returns tissue-specific RNA/protein expression and localization. "
            "返回组织特异性表达、亚细胞定位、蛋白分类与疾病关联。"
        ),
    )
    def protein_tissue_expression(
        ensembl_id: str,
    ) -> str:
        """查询 HPA 蛋白组织表达。

        Args:
            ensembl_id: Ensembl 基因号（如 ENSG00000141510）。
        """
        client = ProteinAtlasClient()
        try:
            d = client.gene_summary(ensembl_id)
        finally:
            client.close()
        if not d.get("gene"):
            return f"Human Protein Atlas 未找到基因「{ensembl_id}」。"
        lines = [f"# 蛋白组织表达：{d['gene']}", ""]
        if d.get("description"):
            lines.append(f"- **描述 / Description**: {d['description'][:200]}")
        for label, key in (
            ("Ensembl", "ensembl"),
            ("UniProt", "uniprot"),
            ("蛋白分类 / Protein class", "protein_class"),
            ("亚细胞定位 / Subcellular", "subcellular"),
        ):
            if d.get(key):
                lines.append(f"- **{label}**: {d[key]}")
        # RNA 组织表达
        if d.get("rna_tissue_specificity") or d.get("rna_tissue_distribution"):
            lines.append("")
            lines.append("### RNA 组织表达")
            if d.get("rna_tissue_specificity"):
                lines.append(f"- 特异性 / Specificity: {d['rna_tissue_specificity']}")
            if d.get("rna_tissue_distribution"):
                lines.append(f"- 分布 / Distribution: {d['rna_tissue_distribution']}")
        tpm = d.get("rna_tissue_specific_tpm") or {}
        if tpm:
            lines.append(f"- 组织表达量 nTPM（{len(tpm)} 组织）:")
            for tissue, val in list(tpm.items())[:10]:
                lines.append(f"  - {tissue}: {val}")
        # 蛋白组织表达
        if d.get("protein_tissue_specificity") or d.get("protein_tissue_distribution"):
            lines.append("")
            lines.append("### 蛋白组织表达")
            if d.get("protein_tissue_specificity"):
                lines.append(f"- 特异性 / Specificity: {d['protein_tissue_specificity']}")
            if d.get("protein_tissue_distribution"):
                lines.append(f"- 分布 / Distribution: {d['protein_tissue_distribution']}")
        # 其他
        extra = []
        if d.get("rna_single_cell_specificity"):
            extra.append(f"单细胞特异性 / Single-cell: {d['rna_single_cell_specificity']}")
        if d.get("rna_brain_specificity"):
            extra.append(f"脑区特异性 / Brain: {d['rna_brain_specificity']}")
        if d.get("tissue_expression_cluster"):
            extra.append(f"组织表达簇 / Cluster: {d['tissue_expression_cluster']}")
        if d.get("disease_involvement"):
            extra.append(f"疾病关联 / Disease: {d['disease_involvement'][:120]}")
        if extra:
            lines.append("")
            for e in extra:
                lines.append(f"- **{e}**")
        lines.append("")
        lines.append("来源：Human Protein Atlas（https://www.proteinatlas.org）。")
        return "\n".join(lines)
