"""GlyGen 糖组学工具：糖苷结构详情与蛋白糖基化。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.glygen import GlyGenClient


def _extract_name(value: Any) -> str:
    """从 GlyGen 名称字段（str / dict / dict 列表）提取可读名称。"""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return str(value.get("name") or value.get("value") or value)
    if isinstance(value, list):
        out = []
        for v in value:
            if isinstance(v, dict):
                nm = v.get("name") or v.get("value") or ""
                if nm:
                    out.append(str(nm))
            elif v:
                out.append(str(v))
        return ", ".join(out[:4])
    return str(value) if value else ""


def register(server: Any) -> None:
    @server.tool(
        name="glycan_lookup",
        description=(
            "Look up a glycan structure by GlyTouCan accession. "
            "按 GlyTouCan 编号查询糖苷结构：输入编号（如 G00051MO），"
            "returns composition/mass/monosaccharide count/sequence info. "
            "返回糖苷组成、质量、单糖数与结构信息，用于糖组学研究。"
        ),
    )
    def glycan_lookup(
        glytoucan_ac: str,
    ) -> str:
        """查询糖苷结构详情。

        Args:
            glytoucan_ac: GlyTouCan 糖苷编号（如 G00051MO）。
        """
        client = GlyGenClient()
        try:
            data = client.glycan_detail(glytoucan_ac)
        finally:
            client.close()
        g = data.get("glytoucan", {}) or {}
        if not g:
            return f"GlyGen 未找到糖苷「{glytoucan_ac}」。"
        lines = [f"# 糖苷结构：{g.get('glytoucan_ac')}", ""]
        lines.append(f"- **GlyTouCan**: [{g.get('glytoucan_ac')}]({g.get('glytoucan_url')})")
        if data.get("mass"):
            lines.append(f"- **质量 / Mass**: {data['mass']}")
        if data.get("number_monosaccharides"):
            lines.append(f"- **单糖数 / Monosaccharides**: {data['number_monosaccharides']}")
        if data.get("glycan_type"):
            lines.append(f"- **糖苷类型 / Type**: {data['glycan_type']}")
        # IUPAC 序列
        for k in ("iupac_condensed", "iupac_compact", "iupac"):
            v = data.get(k)
            if isinstance(v, str) and v:
                lines.append(f"- **IUPAC**: {v[:200]}")
                break
        # 单糖组成
        comp = data.get("composition")
        if isinstance(comp, list) and comp:
            parts = [f"{c.get('count')}×{c.get('name') or c.get('residue')}" for c in comp]
            lines.append(f"- **组成 / Composition**: {', '.join(parts)}")
        # 物种
        sp = data.get("species")
        if isinstance(sp, list) and sp:
            names = []
            for s in sp:
                if isinstance(s, dict):
                    nm = s.get("common_name") or s.get("name") or s.get("glygen_name") or ""
                    if nm:
                        names.append(str(nm))
                else:
                    names.append(str(s))
            if names:
                lines.append(f"- **物种 / Species**: {', '.join(names[:6])}")
        lines.append("")
        lines.append("来源：GlyGen（整合 GlyTouCan 糖苷结构数据）。")
        return "\n".join(lines)

    @server.tool(
        name="protein_glycosylation",
        description=(
            "Look up protein glycosylation and glycan sites. "
            "查询蛋白的糖基化信息：按 UniProt 编号（如 P04637），"
            "returns protein names/glycosites/glycan modifications. "
            "返回蛋白名称、糖基化位点与糖修饰信息，用于糖蛋白研究。"
        ),
    )
    def protein_glycosylation(
        uniprot_acc: str,
    ) -> str:
        """查询蛋白糖基化详情。

        Args:
            uniprot_acc: UniProt 蛋白编号（如 P04637）。
        """
        client = GlyGenClient()
        try:
            data = client.protein_detail(uniprot_acc)
        finally:
            client.close()
        if not data or "uniprot" not in data:
            return f"GlyGen 未找到蛋白「{uniprot_acc}」的糖基化信息。"
        lines = [f"# 蛋白糖基化：{uniprot_acc}", ""]
        unip = data.get("uniprot", {}) or {}
        acc = unip.get("uniprot_canonical_ac") or uniprot_acc
        uid = unip.get("uniprot_id") or ""
        if uid:
            lines.append(f"- **UniProt**: {acc}（{uid}）· {unip.get('length')} aa")
        # 蛋白名（dict 列表：{"name": ..., "type": ...}）
        pname = _extract_name(data.get("protein_names"))
        if pname:
            lines.append(f"- **蛋白 / Protein**: {pname}")
        gname = _extract_name(data.get("gene_names"))
        if gname:
            lines.append(f"- **基因 / Gene**: {gname}")
        # 糖基化位点（list of dicts）
        gl = data.get("glycosylation")
        if isinstance(gl, list) and gl:
            lines.append(f"- **糖基化位点 / Glycosylation sites** ({len(gl)}):")
            for s in gl[:10]:
                subtype = s.get("subtype") or s.get("type") or ""
                site = s.get("site_seq") or s.get("site") or ""
                siteinfo = f" @ {site}" if site else ""
                lines.append(f"  - {subtype}{siteinfo}（{s.get('glytoucan_ac', '')}）")
        elif gl:
            lines.append(f"- **糖基化 / Glycosylation**: {str(gl)[:200]}")
        # 磷酸化等其他 PTM
        for k, label in (("phosphorylation", "磷酸化 / Phosphorylation"), ("ptm_annotation", "PTM")):
            v = data.get(k)
            if isinstance(v, list) and v:
                lines.append(f"- **{label}** ({len(v)} 条)")
        lines.append("")
        lines.append("来源：GlyGen 糖蛋白数据库。")
        return "\n".join(lines)
