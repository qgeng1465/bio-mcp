"""BioMCP 快速上手示例：用 mcp 客户端直接调用各工具。

运行前：pip install -e .（安装本包）
运行：python examples/quickstart.py
"""
import asyncio
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TOOLCALLS = [
    ("uniprot_annotate", {"query": "P04637"}, "查询 p53 (P04637) 蛋白注释"),
    ("pdb_structure_summary", {"pdb_id": "1crn"}, "查询 PDB 1CRN 结构"),
    ("pubmed_search", {"term": "BRCA1 breast cancer", "max_results": 2}, "检索 BRCA1 文献"),
    ("gene_enrichment", {"genes": "BRCA1,TP53,EGFR,ATM,RAD51", "max_terms": 5}, "富集分析"),
]


async def main():
    from mcp import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client

    params = StdioServerParameters(command=sys.executable, args=["-m", "bio_mcp.server"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            for name, args, desc in TOOLCALLS:
                print(f"\n{'='*60}\n▶ {desc}\n{'='*60}")
                res = await session.call_tool(name, args)
                print(res.content[0].text if res.content else "<empty>")


if __name__ == "__main__":
    asyncio.run(main())
