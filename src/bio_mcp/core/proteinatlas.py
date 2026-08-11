"""Human Protein Atlas（HPA）客户端：蛋白组织/细胞表达图谱。

HPA（https://www.proteinatlas.org）基于抗体成像 + 转录组，提供
人体蛋白在组织、细胞、细胞系、脑区、血液中的表达谱与亚细胞定位。
API：/ENSG....json（按 Ensembl 基因号），免鉴权。
参考：https://www.proteinatlas.org/about/download
"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.http import BioHTTP

BASE = "https://www.proteinatlas.org"


class ProteinAtlasClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=30.0)

    # ---- 按 Ensembl 基因号查询表达图谱 ----
    def gene_summary(self, ensembl_id: str) -> dict[str, Any]:
        """按 Ensembl 基因号（如 ENSG00000141510）查询 HPA 表达摘要。"""
        eid = ensembl_id.strip()
        if not eid.startswith("ENSG"):
            raise ValueError(f"请输入 Ensembl 基因号（以 ENSG 开头），收到：{eid}")
        resp = self._http.get(f"{eid}.json")
        d = resp.json()
        return {
            "gene": d.get("Gene"),
            "synonym": d.get("Gene synonym", ""),
            "ensembl": d.get("Ensembl"),
            "uniprot": d.get("Uniprot"),
            "description": d.get("Gene description", ""),
            "protein_class": d.get("Protein class", ""),
            "biological_process": d.get("Biological process", ""),
            "molecular_function": d.get("Molecular function", ""),
            "disease_involvement": d.get("Disease involvement", ""),
            "subcellular": d.get("Subcellular main location", ""),
            "subcellular_additional": d.get("Subcellular additional location", ""),
            "rna_tissue_specificity": d.get("RNA tissue specificity", ""),
            "rna_tissue_distribution": d.get("RNA tissue distribution", ""),
            "rna_tissue_specific_tpm": self._normalize_map(d.get("RNA tissue specific nTPM")),
            "rna_blood_specificity": d.get("RNA blood cell specificity", ""),
            "rna_brain_specificity": d.get("RNA brain regional specificity", ""),
            "rna_single_cell_specificity": d.get("RNA single cell type specificity", ""),
            "protein_tissue_specificity": d.get("Protein tissue specificity", ""),
            "protein_tissue_distribution": d.get("Protein tissue distribution", ""),
            "tissue_expression_cluster": d.get("Tissue expression cluster", ""),
        }

    @staticmethod
    def _normalize_map(value: Any) -> dict[str, str]:
        """组织名 → 表达量 映射（保留前 15 个组织）。"""
        if not isinstance(value, dict):
            return {}
        out: dict[str, str] = {}
        for k, v in list(value.items())[:15]:
            if k not in out:
                out[str(k)] = str(v)
        return out

    def close(self) -> None:
        self._http.close()
