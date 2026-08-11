"""NCBI Taxonomy 与 GEO 基因表达数据工具。"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.ncbi import NCBIClient


def register(server: Any) -> None:
    @server.tool(
        name="taxonomy_lookup",
        description=(
            "Look up NCBI Taxonomy species classification. "
            "查询 NCBI Taxonomy 物种分类：输入物种名或 taxid（如 9606、human），"
            "returns scientific/common name, rank and lineage. "
            "返回学名、常用名、分类层级与谱系，用于确认物种的官方分类。"
        ),
    )
    def taxonomy_lookup(
        query: str,
    ) -> str:
        """查询物种分类。

        Args:
            query: 物种名或 taxid（如 9606、human、Homo sapiens）。
        """
        client = NCBIClient()
        try:
            data = client.taxonomy_lookup(query)
        finally:
            client.close()
        if not data["nodes"]:
            return f"NCBI Taxonomy 未找到「{query}」。"
        lines = [f"# 物种分类检索「{query}」（共 {data['count']} 条）", ""]
        for n in data["nodes"][:5]:
            rank = n.get("rank") or "no rank"
            common = f"（{n['common_name']}）" if n.get("common_name") else ""
            lines.append(f"- **{n['scientific_name']}{common}** — taxid {n['taxid']} · {rank}")
            if n.get("lineage"):
                lines.append(f"  谱系: {n['lineage'][:120]}")
        lines.append("")
        lines.append("来源：NCBI Taxonomy。")
        return "\n".join(lines)

    @server.tool(
        name="geo_dataset_search",
        description=(
            "Search NCBI GEO gene expression datasets. "
            "检索 NCBI GEO 基因表达数据集：按疾病/组织/实验类型（如 breast cancer、RNA-seq），"
            "returns GSE accession/title/platform/sample count/summary. "
            "返回 GSE 编号、标题、平台、样本数与摘要，用于表达谱研究找数据。"
        ),
    )
    def geo_dataset_search(
        query: str,
        max_results: int = 5,
    ) -> str:
        """检索 GEO 数据集。

        Args:
            query: 检索词（如 breast cancer expression、RNA-seq）。
            max_results: 返回条数（1-10）。
        """
        max_results = max(1, min(int(max_results), 10))
        client = NCBIClient()
        try:
            data = client.geo_search(query, max_results)
        finally:
            client.close()
        if not data["datasets"]:
            return f"GEO 未找到「{query}」的数据集。"
        lines = [f"# GEO 数据集检索「{query}」（共 {data['count']} 条）", "", ""]
        for d in data["datasets"]:
            lines.append(f"- **{d['accession']}**: {d['title']}")
            lines.append(f"  {d.get('gdstype') or '-'} · 平台 {d.get('gpl') or '-'} · {d.get('n_samples')} 样本 · {d.get('taxon') or '-'}")
            if d.get("summary"):
                lines.append(f"  {d['summary'][:150]}")
        lines.append("")
        lines.append("来源：NCBI GEO（GDS/GSE 系列）。")
        return "\n".join(lines)

    @server.tool(
        name="genome_assembly_search",
        description=(
            "Search NCBI Assembly genome assemblies (bacteria/virus/eukaryote). "
            "检索 NCBI Assembly 基因组组装（微生物/细菌/病毒/真核）："
            "输入物种或组装名（如 'Escherichia coli[Organism]'、'SARS-CoV-2[Organism]'），"
            "returns accession/name/organism/type/status. "
            "返回组装编号、名称、物种、组装类型与状态，用于基因组学研究。"
        ),
    )
    def genome_assembly_search(
        query: str,
        max_results: int = 5,
    ) -> str:
        """检索基因组组装。

        Args:
            query: 检索词（如 Escherichia coli[Organism]、SARS-CoV-2[Organism]）。
            max_results: 返回条数（1-10）。
        """
        max_results = max(1, min(int(max_results), 10))
        client = NCBIClient()
        try:
            data = client.assembly_search(query, max_results)
        finally:
            client.close()
        if not data["assemblies"]:
            return f"NCBI Assembly 未找到「{query}」。"
        lines = [f"# 基因组组装检索「{query}」（共 {data['count']} 条）", ""]
        for a in data["assemblies"]:
            lines.append(f"- **{a['accession']}** — {a['name']}")
            lines.append(
                f"  {a['organism']}（{a['species']}）· {a['type']} · {a['status']}"
            )
            if a.get("biosample"):
                lines.append(f"  BioSample: {a['biosample']}")
        lines.append("")
        lines.append("来源：NCBI Assembly（GenBank/RefSeq 基因组组装）。")
        return "\n".join(lines)

    @server.tool(
        name="dbsnp_search",
        description=(
            "Search NCBI dbSNP genetic variants. "
            "检索 NCBI dbSNP 遗传变异：按基因/位置/rs 编号"
            "（如 'BRCA1[Gene Name] AND Homo sapiens[Organism]'、'rs1800057[RS]'），"
            "returns rsID/chromosome/position/alleles/clinical significance. "
            "返回 rs 编号、染色体、位置、等位基因与临床意义。"
        ),
    )
    def dbsnp_search(
        query: str,
        max_results: int = 5,
    ) -> str:
        """检索 dbSNP 变异。

        Args:
            query: 检索词（如 BRCA1[Gene Name] AND Homo sapiens[Organism]）。
            max_results: 返回条数（1-10）。
        """
        max_results = max(1, min(int(max_results), 10))
        client = NCBIClient()
        try:
            data = client.dbsnp_search(query, max_results)
        finally:
            client.close()
        if not data["variants"]:
            return f"NCBI dbSNP 未找到「{query}」。"
        lines = [f"# dbSNP 变异检索「{query}」（共 {data['count']} 条）", ""]
        for v in data["variants"]:
            head = f"rs{v.get('rsid')}" if v.get("rsid") else "?"
            if v.get("gene"):
                head += f"（{v['gene']}）"
            lines.append(f"- **{head}**")
            pos = []
            if v.get("position"):
                # chrpos 已含染色体前缀（如 17:43127349）
                pos.append(f"chr{v['position']}")
            if v.get("alleles"):
                pos.append(v["alleles"])
            if pos:
                lines.append(f"  {' · '.join(pos)}")
            if v.get("function"):
                lines.append(f"  功能分类 / Function: {v['function']}")
            if v.get("clinical_significance"):
                lines.append(f"  临床意义 / Clinical: {v['clinical_significance']}")
        lines.append("")
        lines.append("来源：NCBI dbSNP。")
        return "\n".join(lines)

    @server.tool(
        name="plasmid_search",
        description=(
            "Search NCBI plasmid sequences. "
            "检索 NCBI 质粒序列：按质粒名称或宿主"
            "（如 'pET-28a[Title]'、'plasmid[Title] AND Escherichia coli[Organism]'），"
            "returns accession/title/organism/length. "
            "返回质粒编号、名称、宿主与长度，用于分子克隆与载体设计。"
        ),
    )
    def plasmid_search(
        query: str,
        max_results: int = 5,
    ) -> str:
        """检索质粒序列。

        Args:
            query: 检索词（如 pET-28a[Title]、plasmid[Title] AND Escherichia coli[Organism]）。
            max_results: 返回条数（1-10）。
        """
        max_results = max(1, min(int(max_results), 10))
        client = NCBIClient()
        try:
            data = client.plasmid_search(query, max_results)
        finally:
            client.close()
        if not data["plasmids"]:
            return f"NCBI 未找到质粒「{query}」。"
        lines = [f"# 质粒序列检索「{query}」（共 {data['count']} 条）", ""]
        for p in data["plasmids"]:
            lines.append(f"- **{p['accession']}**: {p['title']}")
            parts = []
            if p.get("length"):
                parts.append(f"{p['length']} bp")
            if p.get("organism"):
                parts.append(p["organism"])
            if parts:
                lines.append(f"  {' · '.join(parts)}")
        lines.append("")
        lines.append("来源：NCBI nuccore（质粒/载体序列）。")
        return "\n".join(lines)
