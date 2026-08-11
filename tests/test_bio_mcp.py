"""BioMCP 单元测试：注册完整性 + 参数校验逻辑（不依赖外部网络）。

真实数据库连通性已由 e2e 测试覆盖（_e2e_test.py）。
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest


def run(coro):
    """每个用例独立 event loop，避免重入问题。"""
    return asyncio.run(coro)


EXPECTED_TOOLS = {
    # 原有 6
    "pubmed_search",
    "ncbi_fetch_sequence",
    "blast_search",
    "pdb_structure_summary",
    "gene_enrichment",
    "uniprot_annotate",
    # v0.2 新增 10
    "ensembl_gene_lookup",
    "ensembl_homologs",
    "string_interactions",
    "kegg_pathway_search",
    "kegg_pathway_genes",
    "variant_annotate",
    "clinvar_query",
    "protein_domains",
    "compound_info",
    # v0.2 新增 7（开源直连，替换 OpenGWAS）
    "europepmc_search",
    "alphafold_structure",
    "chembl_drug_search",
    "cellxgene_search",
    "ucsc_genome_info",
    "taxonomy_lookup",
    "geo_dataset_search",
    # v0.2 组合工具
    "gene_full_profile",
    # v0.3 新增 10（糖/代谢/病毒/基因组/核酸/质粒/蛋白图谱）
    "glycan_lookup",
    "protein_glycosylation",
    "uniparc_search",
    "uniparc_by_id",
    "metabolomics_study",
    "metabolomics_latest",
    "protein_tissue_expression",
    "genome_assembly_search",
    "dbsnp_search",
    "plasmid_search",
    # v0.4 新增 7（核酸档案/微生物组/通路/文献/脂质/电镜结构/实验互作）
    "ena_sequence_search",
    "microbiome_study_search",
    "reactome_pathway_search",
    "openalex_work_search",
    "lipid_lookup",
    "emdb_structure_lookup",
    "intact_interactions",
}


def test_create_server_registers_all_forty():
    from bio_mcp.server import create_server

    server = create_server()

    async def _t():
        return {t.name for t in await server.list_tools()}

    tools = run(_t())
    assert tools == EXPECTED_TOOLS
    assert len(tools) == 40


def test_tool_descriptions_nonempty():
    from bio_mcp.server import create_server

    server = create_server()

    async def _t():
        return {t.name: t.description for t in await server.list_tools()}

    descs = run(_t())
    for name, desc in descs.items():
        assert desc and len(desc) > 10, f"{name} 缺描述"


def test_enrichment_requires_two_genes():
    """校验逻辑：少于 2 个基因直接拒绝。"""
    from bio_mcp.tools.enrichment import register
    from mcp.server.mcpserver import MCPServer

    server = MCPServer(name="t", version="1")
    register(server)

    async def _call():
        return await server.call_tool("gene_enrichment", {"genes": "ONLYONE"})

    res = run(_call())
    text = res.content[0].text if res.content else ""
    assert "至少需要 2 个基因" in text


def test_enrichment_rejects_unknown_library():
    from bio_mcp.tools.enrichment import register
    from mcp.server.mcpserver import MCPServer

    server = MCPServer(name="t", version="1")
    register(server)

    async def _call():
        return await server.call_tool(
            "gene_enrichment", {"genes": "BRCA1,TP53", "library": "NOT_A_LIB"}
        )

    res = run(_call())
    text = res.content[0].text if res.content else ""
    assert "未知基因集库" in text


def test_ncbi_limits_max_ids():
    """max_ids 参数被限制在 1-5。"""
    from bio_mcp.tools.ncbi import register
    from mcp.server.mcpserver import MCPServer

    server = MCPServer(name="t", version="1")
    register(server)

    async def _call():
        return await server.call_tool(
            "ncbi_fetch_sequence", {"query": "TP53", "db": "gene", "max_ids": 99}
        )

    # 不应因 max_ids=99 报错（会被 clamp），走真实网络前 mock 掉
    import bio_mcp.tools.ncbi as ncbi_tool

    orig = ncbi_tool.NCBIClient

    class Fake:
        def esearch(self, db, term, retmax=10, sort=None):
            return {"count": 0, "ids": [], "query": term}

        def close(self):
            pass

    ncbi_tool.NCBIClient = Fake
    try:
        res = run(_call())
    finally:
        ncbi_tool.NCBIClient = orig
    text = res.content[0].text if res.content else ""
    assert "未检索到" in text
