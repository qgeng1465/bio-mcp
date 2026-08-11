"""AlphaFold DB 蛋白结构预测工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.alphafold import AlphaFoldClient


def register(server: Any) -> None:
    @server.tool(
        name="alphafold_structure",
        description=(
            "Query AlphaFold DB AI-predicted protein structures. "
            "查询 AlphaFold DB 的 AI 蛋白结构预测：给定 UniProt accession，"
            "returns pLDDT confidence, sequence length, PDB download link. "
            "返回 pLDDT 置信度、序列长度、3D 模型（PDB）下载链接。"
            "AlphaFold covers 200M+ proteins. AlphaFold 覆盖 2 亿+ 蛋白。"
        ),
    )
    def alphafold_structure(
        uniprot_acc: str,
    ) -> str:
        """查询 AlphaFold 预测结构。

        Args:
            uniprot_acc: UniProt accession（如 P04637、Q9Y6K9）。
        """
        acc = uniprot_acc.strip().upper()
        client = AlphaFoldClient()
        try:
            entry = client.prediction(acc)
        finally:
            client.close()
        if not entry:
            return f"AlphaFold DB 未找到「{acc}」的预测结构。请确认是有效 UniProt accession。"
        plddt = entry.get("avg_plddt")
        plddt_note = ""
        if plddt is not None:
            if plddt >= 90:
                plddt_note = "（>90，高置信度，接近实验精度）"
            elif plddt >= 70:
                plddt_note = "（70-90，较高置信度）"
            elif plddt >= 50:
                plddt_note = "（50-70，中等置信度）"
            else:
                plddt_note = "（<50，低置信度区）"
        return "\n".join(
            [
                f"# AlphaFold 预测结构 {entry['entry_id']}",
                "",
                f"- **蛋白**: {entry.get('gene') or acc}（{entry.get('organism') or '-'}）",
                f"- **序列长度**: {entry.get('sequence_length')} aa",
                f"- **平均 pLDDT**: {plddt or '-'}{plddt_note}",
                f"- **模型下载**: {entry.get('model_db_url') or '-'}",
                "",
                "来源：AlphaFold DB (EMBL-EBI / DeepMind)。pLDDT 高代表模型可信。",
            ]
        )
