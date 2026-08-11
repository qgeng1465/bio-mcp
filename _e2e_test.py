"""端到端测试：真实调用 6 个 MCP 工具，验证与真实生物数据库的连通性。"""
import asyncio
import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def extract_text(result) -> str:
    if not result.content:
        return "<empty>"
    return result.content[0].text


async def main():
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client, StdioServerParameters

    params = StdioServerParameters(command=sys.executable, args=["-m", "bio_mcp.server"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = {t.name for t in (await session.list_tools()).tools}
            assert len(tools) == 6, f"期望 6 个工具，实际 {len(tools)}"

            results = {}

            # 1. UniProt（快）
            r = await session.call_tool("uniprot_annotate", {"query": "P04637"})
            results["uniprot_annotate"] = extract_text(r)
            print("[OK] uniprot_annotate:", results["uniprot_annotate"][:100].replace("\n", " | "))

            # 2. PDB（快）
            r = await session.call_tool("pdb_structure_summary", {"pdb_id": "1crn"})
            results["pdb_structure_summary"] = extract_text(r)
            print("[OK] pdb_structure_summary:", results["pdb_structure_summary"][:100].replace("\n", " | "))

            # 3. PubMed（中速，3 秒限速）
            r = await session.call_tool("pubmed_search", {"term": "BRCA1 breast cancer", "max_results": 3})
            results["pubmed_search"] = extract_text(r)
            print("[OK] pubmed_search:", results["pubmed_search"][:100].replace("\n", " | "))

            # 4. NCBI 序列下载（中速）
            r = await session.call_tool("ncbi_fetch_sequence", {"query": "NM_007294.4", "db": "nucleotide"})
            results["ncbi_fetch_sequence"] = extract_text(r)
            print("[OK] ncbi_fetch_sequence:", results["ncbi_fetch_sequence"][:100].replace("\n", " | "))

            # 5. 富集分析（中速）
            r = await session.call_tool("gene_enrichment", {"genes": "BRCA1,TP53,EGFR,ATM,RAD51"})
            results["gene_enrichment"] = extract_text(r)
            print("[OK] gene_enrichment:", results["gene_enrichment"][:100].replace("\n", " | "))

            # 6. BLAST（慢，提交+轮询）
            print("[..] blast_search 提交中（可能需 1-3 分钟）...")
            r = await session.call_tool("blast_search", {"sequence": "atgcatgcatgcatgcatgcatgcatgcatgca", "program": "blastn"})
            results["blast_search"] = extract_text(r)
            print("[OK] blast_search:", results["blast_search"][:120].replace("\n", " | "))

            print("\n=== 全部 6 个工具调用完成 ===")
            with open("_e2e_result.txt", "w", encoding="utf-8") as f:
                for name, text in results.items():
                    f.write(f"===== {name} =====\n{text}\n\n")


if __name__ == "__main__":
    asyncio.run(main())
