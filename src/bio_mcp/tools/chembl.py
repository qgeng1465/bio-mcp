"""ChEMBL 药物活性查询工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.chembl import ChEMBLClient


def register(server: Any) -> None:
    @server.tool(
        name="chembl_drug_search",
        description=(
            "Query drug/compound bioactivity (ChEMBL, EBI). "
            "查询药物/候选化合物：按名称返回 ChEMBL ID、SMILES、分子式、分子量、"
            "临床阶段与作用靶点及活性值（IC50/Ki），for medicinal chemistry & target research. "
            "用于药物化学与靶点调研。"
        ),
    )
    def chembl_drug_search(
        name: str,
        include_targets: bool = True,
    ) -> str:
        """查询药物信息。

        Args:
            name: 药物名（如 aspirin、imatinib、metformin）。
            include_targets: 是否同时查询作用靶点与活性。
        """
        client = ChEMBLClient()
        try:
            hits = client.search_compound(name, max_results=3)
            if not hits:
                return f"ChEMBL 未找到「{name}」。"
            hit = hits[0]
            targets = client.targets_for_compound(hit["chembl_id"]) if include_targets else []
        finally:
            client.close()

        m = hit
        lines = [
            f"# 药物：{m.get('pref_name') or name}（{m.get('chembl_id')}）",
            "",
            f"- **SMILES**: `{m.get('smiles') or '-'}`",
            f"- **分子式**: {m.get('molecular_formula') or '-'}",
            f"- **分子量**: {m.get('molecular_weight') or '-'}",
            f"- **最高临床阶段**: 临床 {m.get('max_phase') or '未进入'}" if m.get("max_phase") else f"- **临床阶段**: 未进入",
        ]
        if m.get("synonyms"):
            lines.append(f"- **别名**: {', '.join(m['synonyms'][:5])}")
        if targets:
            lines.append("")
            lines.append("## 作用靶点与活性")
            lines.append("| 靶点 | 类型 | 活性 | 值 | 单位 |")
            lines.append("|------|------|------|----|------|")
            for t in targets[:8]:
                lines.append(
                    f"| {t.get('target_pref_name') or t.get('target_chembl_id')} "
                    f"| {t.get('standard_type') or '-'} "
                    f"| {t.get('standard_relation') or '='} {t.get('standard_value') or '-'} "
                    f"| {t.get('pchembl_value') or '-'} | {t.get('standard_units') or '-'} |"
                )
        lines.append("")
        lines.append("来源：ChEMBL (EMBL-EBI)，240 万+ 化合物活性数据。")
        return "\n".join(lines)
