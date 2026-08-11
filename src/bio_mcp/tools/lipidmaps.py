"""LIPID MAPS 脂质结构工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.lipidmaps import LipidMapsClient


def register(server: Any) -> None:
    @server.tool(
        name="lipid_lookup",
        description=(
            "Look up LIPID MAPS lipid structure by LM ID. "
            "按 LIPID MAPS 编号查询脂质结构：输入 LM 编号"
            "（如 LMFA01030001 花生四烯酸、LMGP01010001 磷脂酰胆碱），"
            "returns name/formula/SMILES/InChIKey/DB cross-refs. "
            "返回名称、分子式、SMILES 与数据库交叉引用，用于脂质组学研究。"
        ),
    )
    def lipid_lookup(
        lm_id: str,
    ) -> str:
        """查询脂质结构。

        Args:
            lm_id: LIPID MAPS 编号（如 LMFA01030001）。
        """
        client = LipidMapsClient()
        try:
            data = client.lipid_lookup(lm_id)
        finally:
            client.close()
        if len(data) <= 1:
            return f"LIPID MAPS 未找到脂质「{lm_id}」。"
        lines = [f"# LIPID MAPS 脂质：{data['lm_id']}", ""]
        if data.get("name"):
            lines.append(f"- **名称 / Name**: {data['name']}")
        if data.get("formula"):
            lines.append(f"- **分子式 / Formula**: {data['formula']}")
        if data.get("smiles"):
            lines.append(f"- **SMILES**: `{data['smiles']}`")
        if data.get("inchi_key"):
            lines.append(f"- **InChIKey**: {data['inchi_key']}")
        refs = []
        for key, label in (
            ("pubchem_cid", "PubChem"),
            ("hmdb_id", "HMDB"),
            ("kegg_id", "KEGG"),
            ("chebi_id", "ChEBI"),
        ):
            if data.get(key):
                refs.append(f"{label}: {data[key]}")
        if refs:
            lines.append(f"- **交叉引用 / Cross-refs**: {' · '.join(refs)}")
        lines.append("")
        lines.append("来源：LIPID MAPS（脂质组学数据库）。")
        return "\n".join(lines)
