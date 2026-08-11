"""EBI UniParc 蛋白序列归档工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.uniparc import UniParcClient


def register(server: Any) -> None:
    @server.tool(
        name="uniparc_search",
        description=(
            "Search EBI UniParc protein sequence archive. "
            "检索 UniParc 蛋白序列归档：按物种/基因/蛋白编号，"
            "returns UPI IDs/cross-references/organism counts. "
            "返回 UPI 编号、交叉引用数据库与物种信息，覆盖所有公开蛋白序列。"
        ),
    )
    def uniparc_search(
        query: str,
        max_results: int = 5,
    ) -> str:
        """检索 UniParc 蛋白序列归档。

        Args:
            query: 查询（如 taxonomy_id:9606 AND gene:TP53、accession:P04637）。
            max_results: 返回条数（1-10）。
        """
        max_results = max(1, min(int(max_results), 10))
        client = UniParcClient()
        try:
            data = client.search(query, max_results)
        finally:
            client.close()
        if not data["results"]:
            return f"UniParc 未找到「{query}」。"
        lines = [f"# UniParc 蛋白序列归档检索「{query}」", ""]
        for r in data["results"]:
            upi = r.get("uniParcId", "")
            seq = (r.get("sequence") or {}).get("value", "")
            seq_len = len(seq) if seq else r.get("sequenceLength", "")
            lines.append(f"- **{upi}** · {seq_len} aa")
            # 交叉引用计数 + UniProtKB 编号
            cr_count = r.get("crossReferenceCount", 0)
            if cr_count:
                lines.append(f"  交叉引用 / Cross-refs: {cr_count} 个数据库")
            accs = r.get("uniProtKBAccessions") or []
            if accs:
                lines.append(f"  UniProtKB: {', '.join(accs[:6])}")
            # 常见物种
            taxons: list[str] = []
            for t in (r.get("commonTaxons") or []):
                nm = t.get("commonName") or t.get("scientificName") or ""
                if nm:
                    taxons.append(str(nm))
            if taxons:
                lines.append(f"  物种 / Taxa: {', '.join(sorted(set(taxons))[:6])}")
        lines.append("")
        lines.append("来源：EBI UniParc（Universal Protein Archive）。")
        return "\n".join(lines)

    @server.tool(
        name="uniparc_by_id",
        description=(
            "Get UniParc record details by UPI ID. "
            "按 UPI 编号查询 UniParc 记录详情：输入 UPI 编号（如 UPI0000123165），"
            "returns sequence length/sequence/cross-references. "
            "返回序列长度、序列本体与全部交叉引用数据库。"
        ),
    )
    def uniparc_by_id(
        upi: str,
    ) -> str:
        """查询 UniParc 记录详情。

        Args:
            upi: UniParc 编号（如 UPI0000123165）。
        """
        client = UniParcClient()
        try:
            data = client.by_accession(upi)
        finally:
            client.close()
        if not data or "uniParcId" not in data:
            return f"UniParc 未找到记录「{upi}」。"
        lines = [f"# UniParc 记录：{data['uniParcId']}", ""]
        seq = (data.get("sequence") or {}).get("value", "")
        lines.append(f"- **序列长度 / Length**: {len(seq) if seq else data.get('sequenceLength')} aa")
        crs = data.get("uniParcCrossReferences") or []
        lines.append(f"- **交叉引用 / Cross-references** ({len(crs)} 条)")
        # 按数据库分组统计
        counts: dict[str, int] = {}
        for cr in crs:
            counts[cr.get("database", "?")] = counts.get(cr.get("database", "?"), 0) + 1
        top = sorted(counts.items(), key=lambda x: -x[1])[:12]
        lines.append(f"  {', '.join(f'{k}:{v}' for k, v in top)}")
        if seq:
            lines.append("")
            lines.append(f"```\n{seq[:500]}{'…' if len(seq) > 500 else ''}\n```")
        lines.append("")
        lines.append("来源：EBI UniParc。")
        return "\n".join(lines)
