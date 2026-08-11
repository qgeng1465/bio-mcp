"""PubChem 化合物查询工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.pubchem import PubChemClient


def register(server: Any) -> None:
    @server.tool(
        name="compound_info",
        description=(
            "Query compound/drug basic info (PubChem). "
            "查询化合物/药物基本信息：分子式、分子量、规范 SMILES、IUPAC 名、InChIKey 与 CID，"
            "for medicinal chemistry and docking prep. 用于药物化学、分子对接前的化合物确认。"
        ),
    )
    def compound_info(
        name: str,
        include_synonyms: bool = False,
    ) -> str:
        """查询化合物信息。

        Args:
            name: 化合物名（如 aspirin、metformin、caffeine）。
            include_synonyms: 是否同时返回同义词/别名。
        """
        client = PubChemClient()
        try:
            c = client.compound_by_name(name)
            syn = client.synonyms(name) if include_synonyms else []
        finally:
            client.close()
        if c.get("error"):
            return c["error"]
        lines = [
            f"# 化合物：{name}（CID {c['cid']}）",
            "",
            f"- **分子式**: {c.get('molecular_formula') or '-'}",
            f"- **分子量**: {c.get('molecular_weight') or '-'}",
            f"- **IUPAC 名**: {c.get('iupac_name') or '-'}",
            f"- **InChIKey**: {c.get('inchikey') or '-'}",
            f"- **Canonical SMILES**: `{c.get('canonical_smiles') or '-'}`",
        ]
        if include_synonyms and syn:
            lines.append("")
            lines.append("## 别名（前 20 个）")
            lines.append("\n".join(f"- {s}" for s in syn[:20]))
        lines.append("")
        lines.append("来源：PubChem PUG REST (NCBI)。")
        return "\n".join(lines)
