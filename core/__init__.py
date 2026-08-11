"""core —— 生物数据库 HTTP 客户端封装层。

直连数据库（全部零配置、免密钥）：
- NCBI E-utilities / BLAST / Taxonomy / GEO（ncbi）
- RCSB PDB（rcsb）
- UniProt REST（uniprot）
- Enrichr 富集（enrichr）
- Ensembl 基因组 / 同源（ensembl）
- STRING-db 蛋白互作（stringdb）
- KEGG REST（kegg）
- MyVariant.info 变异注释（myvariant）
- InterPro 蛋白结构域（interpro）
- PubChem 化合物（pubchem）
- EuropePMC 全文文献（europepmc）
- AlphaFold DB 蛋白结构预测（alphafold）
- ChEMBL 药物活性（chembl）
- CELLxGENE 单细胞（cellxgene）
- UCSC 基因组浏览器（ucsc）
- GlyGen 糖组学 / 糖苷与蛋白糖基化（glygen）
- EBI UniParc 蛋白序列归档（uniparc）
- EBI Metabolights 代谢组学（metabolights）
- Human Protein Atlas 蛋白组织表达（proteinatlas）
"""

from bio_mcp.core.http import BioHTTP
from bio_mcp.core.ncbi import NCBIClient
from bio_mcp.core.rcsb import RCSBClient
from bio_mcp.core.uniprot import UniProtClient
from bio_mcp.core.enrichr import EnrichrClient
from bio_mcp.core.ensembl import EnsemblClient
from bio_mcp.core.stringdb import STRINGClient
from bio_mcp.core.kegg import KEGGClient
from bio_mcp.core.myvariant import MyVariantClient
from bio_mcp.core.interpro import InterProClient
from bio_mcp.core.pubchem import PubChemClient
from bio_mcp.core.europepmc import EuropePMCClient
from bio_mcp.core.alphafold import AlphaFoldClient
from bio_mcp.core.chembl import ChEMBLClient
from bio_mcp.core.cellxgene import CellxGeneClient
from bio_mcp.core.ucsc import UCSCClient
from bio_mcp.core.glygen import GlyGenClient
from bio_mcp.core.uniparc import UniParcClient
from bio_mcp.core.metabolights import MetabolightsClient
from bio_mcp.core.proteinatlas import ProteinAtlasClient

__all__ = [
    "BioHTTP",
    "NCBIClient",
    "RCSBClient",
    "UniProtClient",
    "EnrichrClient",
    "EnsemblClient",
    "STRINGClient",
    "KEGGClient",
    "MyVariantClient",
    "InterProClient",
    "PubChemClient",
    "EuropePMCClient",
    "AlphaFoldClient",
    "ChEMBLClient",
    "CellxGeneClient",
    "UCSCClient",
    "GlyGenClient",
    "UniParcClient",
    "MetabolightsClient",
    "ProteinAtlasClient",
]
