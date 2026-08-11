"""PDB 蛋白质结构工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.rcsb import RCSBClient


def register(server: Any) -> None:
    @server.tool(
        name="pdb_structure_summary",
        description=(
            "按 PDB ID 获取蛋白质结构摘要：标题/分辨率/实验方法/物种/沉积日期，"
            "以及指定链的序列。用于结构生物学、药物设计的结构查询。"
        ),
    )
    def pdb_structure_summary(
        pdb_id: str,
        chain_id: int = 1,
    ) -> str:
        """查询 PDB 结构。

        Args:
            pdb_id: PDB ID（如 1crn、4hhb、6m0j）。
            chain_id: 要显示序列的链序号（1 起）。
        """
        client = RCSBClient()
        try:
            entry = client.entry_summary(pdb_id)
            polymer = client.polymer_entity_info(pdb_id, chain_id)
        finally:
            client.close()

        res = entry.get("resolution") or ["-"]
        res_str = ", ".join(str(r) for r in res[:3])
        lines = [
            f"# PDB {entry['pdb_id']} — {entry['title'] or '无标题'}",
            "",
            f"- **分辨率**: {res_str} Å",
            f"- **方法**: {entry['methods'] or '-'}",
            f"- **物种**: {', '.join(entry['organism']) or '-'}",
            f"- **沉积日期**: {entry['deposited'] or '-'}",
            f"- **首次发布**: {entry['release_date'] or '-'}",
        ]
        if polymer and polymer.get("sequence"):
            lines.append("")
            lines.append(f"### 链 {chain_id}（{polymer.get('description') or '-'}）")
            lines.append(f"序列长度 {len(polymer['sequence'])} aa：")
            seq = polymer["sequence"]
            lines.append("```")
            for i in range(0, len(seq), 60):
                lines.append(seq[i : i + 60])
            lines.append("```")
        return "\n".join(lines)
