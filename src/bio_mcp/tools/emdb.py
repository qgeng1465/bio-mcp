"""EBI EMDB 冷冻电镜结构工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.emdb import EMDBClient


def register(server: Any) -> None:
    @server.tool(
        name="emdb_structure_lookup",
        description=(
            "Look up EBI EMDB cryo-EM structure entry. "
            "查询 EMDB 冷冻电镜结构：输入 EMD 编号（如 EMD-1234），"
            "returns title/authors/resolution/macromolecules/dates. "
            "返回标题、作者、分辨率、组分与发布信息，用于电镜结构研究。"
        ),
    )
    def emdb_structure_lookup(
        emdb_id: str,
    ) -> str:
        """查询冷冻电镜结构。

        Args:
            emdb_id: EMD 编号（如 EMD-1234 或 1234）。
        """
        client = EMDBClient()
        try:
            data = client.entry_lookup(emdb_id)
        finally:
            client.close()
        if not data["emdb_id"]:
            return f"EMDB 未找到结构「{emdb_id}」。"
        lines = [f"# EMDB 结构：{data['emdb_id']}", ""]
        if data["title"]:
            lines.append(f"- **标题 / Title**: {data['title']}")
        meta = []
        if data.get("resolution"):
            meta.append(f"分辨率 {data['resolution']}")
        if data.get("aggregation_state"):
            meta.append(data["aggregation_state"])
        if data.get("status"):
            meta.append(data["status"])
        if data.get("deposition"):
            meta.append(f"提交 {data['deposition']}")
        if data.get("release"):
            meta.append(f"发布 {data['release']}")
        if meta:
            lines.append(f"- **信息 / Info**: {' · '.join(meta)}")
        if data.get("authors"):
            lines.append(f"- **作者 / Authors**: {', '.join(data['authors'][:8])}")
        if data.get("samples"):
            lines.append(f"- **组分 / Macromolecules**（{len(data['samples'])}）")
            for s in data["samples"][:6]:
                nm = s.get("name") or "?"
                org = f"（{s['organism']}）" if s.get("organism") else ""
                state = s.get("oligomeric_state") or ""
                lines.append(f"  - {nm}{org}" + (f" · {state}" if state else ""))
        lines.append("")
        lines.append("来源：EBI EMDB（Electron Microscopy Data Bank）。")
        return "\n".join(lines)
