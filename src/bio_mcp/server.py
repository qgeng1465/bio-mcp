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
    "BioMCP — 生物信息学 MCP 服务器。"
    "提供 PubMed 文献检索、NCBI 序列下载、BLAST 同源比对、"
    "PDB 蛋白质结构查询、GO/KEGG 富集分析、UniProt 蛋白注释。"
    "所有数据来自公开学术数据库（NCBI / RCSB / UniProt / g:Profiler）。"
)

INSTRUCTIONS = (
    "BioMCP 让 AI 助手直接访问生物信息学数据库。常见用法：\n"
    "- 检索文献：pubmed_search('BRCA1 breast cancer')\n"
    "- 下载序列：ncbi_fetch_sequence('NM_007294.4')\n"
    "- 同源比对：blast_search(序列)\n"
    "- 结构查询：pdb_structure_summary('1crn')\n"
    "- 富集分析：gene_enrichment('BRCA1,TP53,EGFR')\n"
    "- 蛋白注释：uniprot_annotate('P04637')\n"
    "注意：NCBI 有速率限制，涉及多次查询时请耐心等待；结果请结合专业工具复核。"
)


def create_server() -> MCPServer:
    """构建并注册全部工具的 MCP server。"""
    from bio_mcp.tools import blast, enrichment, ncbi, pdb, pubmed, uniprot

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
    return server


def main() -> None:
    logging.basicConfig(level=logging.WARNING)
    server = create_server()
    asyncio.run(server.run_stdio_async())


if __name__ == "__main__":
    main()
