"""BioMCP — 生物信息学 MCP 服务器入口。

运行方式：
    python -m bio_mcp.server
    # 或安装后直接
    bio-mcp

启动后作为 stdio MCP server 供任意 MCP 客户端调用。
"""
from __future__ import annotations

import asyncio
import logging
import sys

from mcp.server.mcpserver import MCPServer

from bio_mcp import __version__

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # 非终端环境
    pass

DESCRIPTION = (
    "BioMCP — Bioinformatics MCP Server / 生物信息学 MCP 服务器。"
    "Zero-config direct access to 19 open academic databases / "
    "零配置直连 19 个公开学术数据库：PubMed/EuropePMC literature、"
    "NCBI sequences/BLAST/Taxonomy/GEO/Assembly/dbSNP、PDB structures、"
    "AlphaFold predictions、UniProt annotations、GO/KEGG enrichment、"
    "Ensembl genome & homologs、STRING interactions、KEGG pathways、"
    "MyVariant/ClinVar variants、InterPro domains、PubChem/ChEMBL compounds、"
    "CELLxGENE single-cell、UCSC genomes、GlyGen glycobiology、"
    "UniParc archive、Metabolights metabolomics、Human Protein Atlas. "
    "Cross-database validation via gene_full_profile / "
    "支持跨库交叉验证 gene_full_profile。"
)

INSTRUCTIONS = (
    "BioMCP lets AI assistants query bioinformatics databases directly, "
    "all zero-config. 让 AI 助手直接访问生物数据库，全部零配置。\n"
    "Common usage / 常见用法：\n"
    "- Literature 文献：pubmed_search('BRCA1 breast cancer') / europepmc_search('BRCA1')\n"
    "- Sequences 序列：ncbi_fetch_sequence('NM_007294.4')\n"
    "- Homology 比对：blast_search(sequence)\n"
    "- Structure 结构：pdb_structure_summary('1crn') / alphafold_structure('P04637')\n"
    "- Enrichment 富集：gene_enrichment('BRCA1,TP53,EGFR')\n"
    "- Protein 蛋白：uniprot_annotate('P04637')\n"
    "- Genome 基因组：ensembl_gene_lookup('BRCA1') / genome_assembly_search('Escherichia coli[Organism]')\n"
    "- Interactions 互作：string_interactions('TP53')\n"
    "- Variants 变异：variant_annotate('chr13:g.32911145G>A') / dbsnp_search('BRCA1[Gene Name] AND Homo sapiens[Organism]')\n"
    "- Drugs 药物：chembl_drug_search('imatinib')\n"
    "- Glycomics 糖组学：glycan_lookup('G00051MO') / protein_glycosylation('P04637')\n"
    "- Metabolomics 代谢组学：metabolomics_study('MTBLS1')\n"
    "- Protein Atlas 蛋白图谱：protein_tissue_expression('ENSG00000141510')\n"
    "- Plasmids 质粒：plasmid_search('pET-28a[Title]')\n"
    "- Single-cell 单细胞：cellxgene_search('organoid')\n"
    "- Combined report 综合报告：gene_full_profile('BRCA1') — queries 4 DBs concurrently\n"
    "Note / 注意：NCBI has a rate limit — be patient with multi-query calls; "
    "always double-check results with specialized tools / NCBI 有限速，"
    "多查询请耐心等待；结果请结合专业工具复核。"
)


def create_server() -> MCPServer:
    """构建并注册全部工具的 MCP server。"""
    from bio_mcp.tools import (
        alphafold,
        blast,
        cellxgene,
        chembl,
        crosscheck,
        enrichment,
        ensembl,
        europepmc,
        glygen,
        interpro,
        kegg,
        metabolights,
        ncbi,
        ncbi_extra,
        pdb,
        proteinatlas,
        pubchem,
        pubmed,
        stringdb,
        ucsc,
        uniparc,
        uniprot,
        variant,
    )

    server = MCPServer(
        name="bio-mcp",
        title="BioMCP 生物信息学助手",
        description=DESCRIPTION,
        instructions=INSTRUCTIONS,
        version=__version__,
    )
    pubmed.register(server)
    ncbi.register(server)
    blast.register(server)
    pdb.register(server)
    enrichment.register(server)
    uniprot.register(server)
    ensembl.register(server)
    stringdb.register(server)
    kegg.register(server)
    variant.register(server)
    interpro.register(server)
    pubchem.register(server)
    europepmc.register(server)
    alphafold.register(server)
    chembl.register(server)
    cellxgene.register(server)
    ucsc.register(server)
    ncbi_extra.register(server)
    glygen.register(server)
    uniparc.register(server)
    metabolights.register(server)
    proteinatlas.register(server)
    crosscheck.register(server)
    return server


def main() -> None:
    logging.basicConfig(level=logging.WARNING)
    server = create_server()
    asyncio.run(server.run_stdio_async())


if __name__ == "__main__":
    main()
