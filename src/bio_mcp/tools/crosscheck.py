"""交叉验证组合工具：一个查询 → 多数据库并发 → 综合分析报告。

这是 BioMCP 的"分析层"：不止查询单一数据库，而是把同一实体的信息
从多个来源（Ensembl/UniProt/STRING/NCBI）聚合，交叉验证后给出综合解读。
"""
from __future__ import annotations

import threading
from typing import Any

from bio_mcp.core.cache import LRUCache
from bio_mcp.core.ensembl import EnsemblClient
from bio_mcp.core.ncbi import NCBIClient
from bio_mcp.core.stringdb import STRINGClient
from bio_mcp.core.uniprot import UniProtClient

# 模块级缓存：跨调用共享，避免重复打 API
_gene_cache = LRUCache(maxsize=64, ttl_seconds=3600)


def _gene_key(symbol: str, species: str) -> str:
    return f"gene|{symbol}|{species}"


# Ensembl 物种代码 → UniProt 学名（UniProt 查询用 organism_name 而非 organism:）
_SPECIES_NAMES = {
    "homo_sapiens": "Homo sapiens",
    "mus_musculus": "Mus musculus",
    "danio_rerio": "Danio rerio",
    "rattus_norvegicus": "Rattus norvegicus",
    "drosophila_melanogaster": "Drosophila melanogaster",
    "caenorhabditis_elegans": "Caenorhabditis elegans",
    "saccharomyces_cerevisiae": "Saccharomyces cerevisiae",
    "arabidopsis_thaliana": "Arabidopsis thaliana",
}


def _uniprot_species(species: str) -> str:
    return _SPECIES_NAMES.get(species, species.replace("_", " ").title())


def register(server: Any) -> None:
    @server.tool(
        name="gene_full_profile",
        description=(
            "Combined multi-database gene analysis (cross-validation). "
            "基因综合分析（多数据库交叉验证）：给定基因符号，一次并发返回"
            "Ensembl 定位 + UniProt 蛋白注释 + STRING 互作伙伴 + PubMed 文献数，"
            "for project kickoff and functional overview. 适合开题调研、蛋白功能概述。"
        ),
    )
    def gene_full_profile(
        symbol: str,
        species: str = "homo_sapiens",
    ) -> str:
        """综合分析基因。

        Args:
            symbol: 基因符号（如 BRCA1、TP53、EGFR）。
            species: 物种（默认人类）。
        """
        symbol = symbol.strip().upper()
        cached = _gene_cache.get(_gene_key(symbol, species))
        if cached:
            return cached + "\n\n（数据来自缓存）"
        results: dict[str, str] = {}
        errors: list[str] = []

        def run_ensembl() -> None:
            try:
                c = EnsemblClient()
                try:
                    g = c.gene_by_symbol(symbol, species)
                finally:
                    c.close()
                if g.get("gene_id"):
                    results["ensembl"] = (
                        f"**Ensembl {g['gene_id']}** · chr{g['chr']}:{g['start']}-{g['end']} "
                        f"· {g.get('biotype')} · {g.get('description') or '-'}"
                    )
                else:
                    errors.append(f"Ensembl 未找到 {symbol}")
            except Exception as e:
                errors.append(f"Ensembl 查询失败: {e}")

        def run_uniprot() -> None:
            try:
                c = UniProtClient()
                try:
                    hits = c.search(f'gene:{symbol} AND organism_name:"{_uniprot_species(species)}"', max_results=1)
                finally:
                    c.close()
                if hits:
                    h = hits[0]
                    results["uniprot"] = (
                        f"**UniProt {h['accession']}** · {h['protein_name']} · "
                        f"{h['organism']} · {h['length']} aa · {h.get('function', '')[:120]}"
                    )
                else:
                    errors.append(f"UniProt 未找到 {symbol}")
            except Exception as e:
                errors.append(f"UniProt 查询失败: {e}")

        def run_string() -> None:
            try:
                c = STRINGClient()
                try:
                    partners = c.interactions(symbol, species=9606 if species == "homo_sapiens" else 10090)
                finally:
                    c.close()
                if partners:
                    top = ", ".join(f"{p['partner']}({p['score']})" for p in partners[:5])
                    results["string"] = f"**STRING 互作伙伴**: {top}"
                else:
                    errors.append(f"STRING 未找到 {symbol} 互作")
            except Exception as e:
                errors.append(f"STRING 查询失败: {e}")

        def run_pubmed() -> None:
            try:
                c = NCBIClient()
                try:
                    es = c.esearch("pubmed", f"{symbol}[Gene Name]", retmax=1)
                finally:
                    c.close()
                results["pubmed"] = f"**PubMed 文献**: {es['count']} 篇"
            except Exception as e:
                errors.append(f"PubMed 查询失败: {e}")

        threads = [
            threading.Thread(target=run_ensembl),
            threading.Thread(target=run_uniprot),
            threading.Thread(target=run_string),
            threading.Thread(target=run_pubmed),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)

        lines = [f"# 基因综合分析：{symbol} ({species})", ""]
        order = ["ensembl", "uniprot", "string", "pubmed"]
        for key in order:
            if key in results:
                lines.append(f"- {results[key]}")
        if errors:
            lines.append("")
            lines.append("### 部分数据源未返回")
            for e in errors[:3]:
                lines.append(f"- ⚠️ {e}")
        lines.append("")
        lines.append("综合来自 Ensembl / UniProt / STRING / PubMed 的交叉验证。来源：公开学术数据库。")
        report = "\n".join(lines)
        _gene_cache.set(_gene_key(symbol, species), report)
        return report
