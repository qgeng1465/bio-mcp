# 🧬 BioMCP — 生物信息学 MCP 服务器 / Bioinformatics MCP Server

> **BioMCP** is an open-source **MCP server** that connects any AI assistant directly to **19 open bioinformatics databases** — zero config, no API keys. Literature, sequences, BLAST, structures, enrichment, annotations, genomes, interactions, variants, domains, compounds, single-cell, glycomics, metabolomics and more.
>
> BioMCP 是一个开源的 **MCP 服务器**，让任意 AI 助手**零配置直连 19 个公开生物数据库**——文献、序列、比对、结构、富集、注释、基因组、互作、变异、结构域、化合物、单细胞、糖组学、代谢组学等全流程。

![MCP](https://img.shields.io/badge/MCP-Server-7c5cff?style=flat-square)
![Tools](https://img.shields.io/badge/Tools-33-0ea5e9?style=flat-square)
![Databases](https://img.shields.io/badge/Databases-19-22c55e?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10%2B-2ea44f?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-win%20%7C%20mac%20%7C%20linux-lightgrey?style=flat-square)

---

## ✨ 特性 / Features

- 🔌 **标准 MCP 协议** / Standard MCP protocol — 基于官方 MCP SDK，stdio 传输，兼容所有 MCP 客户端
- 🧬 **33 个工具 · 19 个数据库** / 33 tools · 19 databases — 覆盖文献→序列→结构→功能→互作→变异→药物→单细胞→糖组学→代谢组学全流程
- ⚡ **零配置使用** / Zero-config — `pip install bio-mcp` 一条命令，无需数据库、无需密钥
- 🌐 **数据公开权威** / Authoritative public data — 全部来自 NCBI / RCSB / UniProt / Ensembl / EBI / STRING / KEGG / GlyGen 等官方 API
- 🐌 **智能限速** / Smart rate-limiting — 内置 NCBI 3 秒/请求限速与重试退避，遵守学术 API 规范
- 🔄 **跨库交叉验证** / Cross-database validation — `gene_full_profile` 一次并发查询 4 个数据库
- 🏷️ **中英双语** / Bilingual — 命令描述与文档双语，国内网络可达（已适配 Enrichr 替代 g:Profiler）
- 🧪 **糖组学 & 代谢组学** / Glycomics & Metabolomics — 糖苷结构、蛋白糖基化、代谢组学研究全覆盖

---

## 📦 安装 / Install

```bash
# 1. 安装（需要 Python 3.10+）/ Install (Python 3.10+)
pip install bio-mcp

# 2. 启动（stdio 模式，供 MCP 客户端调用）/ Run in stdio mode
bio-mcp
```

### 手动安装（源码）/ Install from source

```bash
git clone https://github.com/qgeng1465/bio-mcp.git
cd bio-mcp
pip install .
# 或开发模式 / or dev mode
pip install -e ".[test]"
```

---

## 🚀 快速开始 / Quick Start

在任何支持 MCP 的 AI 助手 / IDE 中注册 BioMCP（Cursor / VS Code / 各类 MCP 客户端等）：

```json
{
  "mcpServers": {
    "bio-mcp": {
      "command": "bio-mcp"
    }
  }
}
```

然后在对话中直接使用 / Then just ask:

```
🧬 帮我查一下 BRCA1 相关的最新文献
🧬 下载 CYP2D6 的蛋白序列
🧬 对这段 DNA 做 BLAST：ATGC...
🧬 查 PDB 1CRN 的结构 / AlphaFold 预测 P04637
🧬 分析基因列表 BRCA1,TP53,EGFR,ATM,RAD51 的富集
🧬 查 imatinib 的靶点 / 查 aspilin 的分子式
🧬 查糖苷 G00051MO 的结构 / P04637 的糖基化
🧬 检索大肠杆菌的基因组组装 / 查 pET-28a 质粒
🧬 查 BRCA1 在人体组织中的表达
🧬 对 BRCA1 做一个多库综合分析报告
```

---

## 🔧 工具 / Tools（33）

### 📚 文献 / Literature
| 工具 | 功能 / Function | 数据源 / Source |
|---|---|---|
| `pubmed_search` | PubMed 文献检索（标题/作者/期刊/PMID/DOI）/ literature search | NCBI E-utilities |
| `europepmc_search` | 全文文献检索（含 OA 全文）/ full-text + open-access | Europe PMC (EBI) |

### 🧬 序列与比对 / Sequence & Alignment
| 工具 | 功能 / Function | 数据源 / Source |
|---|---|---|
| `ncbi_fetch_sequence` | 下载核酸/蛋白序列（FASTA/GenBank）/ fetch sequences | NCBI E-utilities |
| `blast_search` | DNA/蛋白同源 BLAST，返回 top hits / homology search | NCBI BLAST |
| `taxonomy_lookup` | 物种分类查询（学名/谱系）/ species taxonomy | NCBI Taxonomy |
| `geo_dataset_search` | 基因表达数据集检索 / expression dataset search | NCBI GEO |
| `uniparc_search` | 蛋白序列归档检索（UPI/交叉引用）/ protein archive search | EBI UniParc |
| `uniparc_by_id` | UniParc 记录详情（序列/全部交叉引用）/ record by UPI ID | EBI UniParc |

### 🏗️ 结构 / Structure
| 工具 | 功能 / Function | 数据源 / Source |
|---|---|---|
| `pdb_structure_summary` | 实验结构查询（分辨率/方法/链序列）/ experimental structures | RCSB PDB |
| `alphafold_structure` | AI 预测结构（pLDDT 置信度）/ AI-predicted structures | AlphaFold DB (EBI) |

### 🧫 蛋白功能 / Protein Function
| 工具 | 功能 / Function | 数据源 / Source |
|---|---|---|
| `uniprot_annotate` | 蛋白注释（名称/基因/功能/GO）/ protein annotations | UniProt |
| `protein_domains` | 蛋白结构域/家族/位点 / structural domains | InterPro (EBI) |

### 🕸️ 通路与互作 / Pathways & Interactions
| 工具 | 功能 / Function | 数据源 / Source |
|---|---|---|
| `gene_enrichment` | GO/KEGG/Reactome 富集分析 / enrichment analysis | Enrichr |
| `kegg_pathway_search` | KEGG 通路搜索 / pathway search | KEGG |
| `kegg_pathway_genes` | 通路包含的基因列表 / genes in a pathway | KEGG |
| `string_interactions` | 蛋白互作网络 / protein interaction network | STRING-db |
| `ensembl_gene_lookup` | 基因定位（GRCh38 坐标）/ gene lookup | Ensembl |
| `ensembl_homologs` | 同源基因（直系/旁系）/ homologous genes | Ensembl Compara |

### 🧬 基因组与组装 / Genome & Assembly
| 工具 | 功能 / Function | 数据源 / Source |
|---|---|---|
| `ucsc_genome_info` | 基因组组装与注释轨道 / genome assemblies | UCSC Genome Browser |
| `genome_assembly_search` | 基因组组装检索（细菌/病毒/真核）/ genome assemblies | NCBI Assembly |

### 🩺 变异与临床 / Variants & Clinical
| 工具 | 功能 / Function | 数据源 / Source |
|---|---|---|
| `variant_annotate` | 变异注释（频率/功能预测/临床意义）/ variant annotation | MyVariant.info |
| `clinvar_query` | ClinVar 临床变异分类 / clinical variant classification | NCBI ClinVar |
| `dbsnp_search` | dbSNP 遗传变异检索（rsID/等位基因/临床意义）/ variant search | NCBI dbSNP |

### 💊 化合物与药物 / Compounds & Drugs
| 工具 | 功能 / Function | 数据源 / Source |
|---|---|---|
| `compound_info` | 化合物信息（SMILES/分子式/InChIKey）/ compound info | PubChem |
| `chembl_drug_search` | 药物活性与靶点（IC50/Ki）/ drug bioactivity & targets | ChEMBL (EBI) |

### 🧬 核酸与质粒 / Nucleic Acid & Plasmids
| 工具 | 功能 / Function | 数据源 / Source |
|---|---|---|
| `plasmid_search` | 质粒/载体序列检索（名称/宿主/长度）/ plasmid search | NCBI nuccore |

### 🦠 单细胞 / Single-Cell
| 工具 | 功能 / Function | 数据源 / Source |
|---|---|---|
| `cellxgene_search` | 单细胞数据集检索（含类器官/肿瘤图谱）/ single-cell datasets | CELLxGENE (CZ) |

### 🍬 糖组学 / Glycomics
| 工具 | 功能 / Function | 数据源 / Source |
|---|---|---|
| `glycan_lookup` | 糖苷结构详情（组成/质量/IUPAC）/ glycan structure | GlyGen (GlyTouCan) |
| `protein_glycosylation` | 蛋白糖基化位点与糖修饰 / protein glycosylation | GlyGen |

### 🔬 代谢组学 / Metabolomics
| 工具 | 功能 / Function | 数据源 / Source |
|---|---|---|
| `metabolomics_study` | 代谢组学研究详情（技术/设计/因子）/ study details | EBI Metabolights |
| `metabolomics_latest` | 最新代谢组学研究列表 / latest studies | EBI Metabolights |

### 🧫 蛋白图谱 / Protein Atlas
| 工具 | 功能 / Function | 数据源 / Source |
|---|---|---|
| `protein_tissue_expression` | 蛋白组织表达与亚细胞定位 / tissue expression | Human Protein Atlas |

### 🧠 组合分析 / Combined
| 工具 | 功能 / Function | 数据源 / Source |
|---|---|---|
| `gene_full_profile` | **多库交叉验证**：一次并发查 Ensembl+UniProt+STRING+PubMed / combined report | 4 个数据库 |

---

## 💬 示例输出 / Example Output

**gene_full_profile**（组合工具 / combined tool）

```
# 基因综合分析：TP53 (homo_sapiens)

- **Ensembl ENSG00000141510** · chr17:7668402-7687550 · protein_coding · tumor protein p53
- **UniProt P04637** · Cellular tumor antigen p53 · Homo sapiens · 393 aa · Multifunctional transcription factor...
- **STRING 互作伙伴**: MDM2(0.999), TP53BP1(0.996), EP300(0.986), ...
- **PubMed 文献**: 74,021 篇

综合来自 Ensembl / UniProt / STRING / PubMed 的交叉验证。
```

---

## 🏗️ 架构 / Architecture

```
┌──────────────────────────────────────────────┐
│                 MCP Client                   │
│   (任意支持 MCP 的 AI 助手 / IDE)             │
└──────────────────────┬───────────────────────┘
                       │  stdio (JSON-RPC 2.0)
┌──────────────────────▼───────────────────────┐
│              bio-mcp server                   │
│  ┌────────────────────────────────────────┐  │
│  │  tools/  (33 个 MCP 工具 / 33 tools)     │  │
│  │  pubmed · ncbi · blast · pdb · uniprot  │  │
│  │  enrichment · ensembl · string · kegg   │  │
│  │  variant · interpro · pubchem · chembl  │  │
│  │  europepmc · alphafold · cellxgene ·    │  │
│  │  ucsc · taxonomy · geo · glygen ·       │  │
│  │  uniparc · metabolights · proteinatlas  │  │
│  │  assembly · dbsnp · plasmid · crosscheck│  │
│  └────────────────────┬───────────────────┘  │
│  ┌────────────────────▼───────────────────┐  │
│  │  core/  (19 个数据库客户端 / clients)    │  │
│  │  BioHTTP: 重试/退避/限速/超时/并发       │  │
│  │  LRUCache: 线程安全缓存层               │  │
│  └────────────────────┬───────────────────┘  │
└───────────────────────┼──────────────────────┘
        ┌───────┬───────┼───────┬───────┬────────────┐
     ┌──▼──┐ ┌──▼──┐ ┌──▼──┐ ┌──▼──┐ ┌──▼──┐ ┌─────▼─────┐
     │NCBI │ │RCSB │ │Uni  │ │Ens  │ │STRING│ │Enrichr   │
     │     │ │PDB  │ │Prot │ │embl │ │     │ │... 共19库 │
     └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └───────────┘
```

### 为什么用 Enrichr 而不是 g:Profiler？

g:Profiler（爱沙尼亚）在国内网络下常不可达；Enrichr（Ma'ayan Lab）国内可达且提供 GO/KEGG/Reactome/WikiPathways 等数百个基因集库。BioMCP 默认采用 Enrichr，保证开箱即用。

### 为什么 OpenGWAS / DisGeNET 被排除？

OpenGWAS 从 2024-05 起强制要求 API token；DisGeNET 也需 API key，均无法零配置直连，故不包含。所有收录的 19 个数据库均为开放免密钥 API。

---

## 📁 目录结构 / Project Structure

```
bio-mcp/
├── src/bio_mcp/
│   ├── server.py            # MCP server 入口（装配 33 个工具）
│   ├── core/                # 19 个数据源客户端
│   │   ├── http.py          #   BioHTTP：重试/退避/限速/超时
│   │   ├── cache.py         #   LRUCache：线程安全缓存层
│   │   ├── ncbi.py          #   NCBI E-utilities + BLAST + Assembly + dbSNP
│   │   ├── rcsb.py          #   RCSB PDB
│   │   ├── uniprot.py       #   UniProt REST
│   │   ├── enrichr.py       #   Enrichr 富集
│   │   ├── ensembl.py       #   Ensembl 基因/同源
│   │   ├── stringdb.py      #   STRING 互作
│   │   ├── kegg.py          #   KEGG 通路
│   │   ├── myvariant.py     #   MyVariant 变异
│   │   ├── interpro.py      #   InterPro 结构域
│   │   ├── pubchem.py       #   PubChem 化合物
│   │   ├── europepmc.py     #   Europe PMC 文献
│   │   ├── alphafold.py     #   AlphaFold 结构
│   │   ├── chembl.py        #   ChEMBL 药物
│   │   ├── cellxgene.py     #   CELLxGENE 单细胞
│   │   ├── ucsc.py          #   UCSC 基因组
│   │   ├── glygen.py        #   GlyGen 糖组学
│   │   ├── uniparc.py       #   UniParc 蛋白序列归档
│   │   ├── metabolights.py  #   Metabolights 代谢组学
│   │   └── proteinatlas.py  #   Human Protein Atlas
│   └── tools/               # 33 个 MCP 工具定义
│       ├── pubmed.py · ncbi.py · blast.py · pdb.py
│       ├── uniprot.py · enrichment.py · ensembl.py
│       ├── stringdb.py · kegg.py · variant.py
│       ├── interpro.py · pubchem.py · europepmc.py
│       ├── alphafold.py · chembl.py · cellxgene.py
│       ├── ucsc.py · ncbi_extra.py · glygen.py
│       ├── uniparc.py · metabolights.py · proteinatlas.py
│       └── crosscheck.py
├── tests/                   # 单元测试（不依赖网络）
├── examples/                # 客户端配置与快速开始
├── .github/workflows/       # CI（GitHub Actions）
└── pyproject.toml
```

---

## 🧪 测试 / Testing

```bash
# 单元测试（离线，不依赖网络）/ offline unit tests
python -m pytest tests/ -v
```

> 全部 33 个工具均已在开发期对真实公开数据库做端到端验证（33/33 通过）。
> All 33 tools were end-to-end validated against the real public databases (33/33 passed).

---

## 🗺️ Roadmap / 路线图

- ✅ 微生物 / 病毒 / 细菌基因组组装（NCBI Assembly）
- ✅ 核酸 / 质粒序列检索（NCBI nuccore、UniParc）
- ✅ 糖组学 / 代谢组学（GlyGen、Metabolights）
- ✅ 蛋白组织图谱（Human Protein Atlas）
- 脂质组学数据库（LIPID MAPS）
- 批量对比分析（多条序列/多基因批量富集）
- 虚拟细胞 / 类器官数据接口（多组学整合）

---

## ⚠️ 免责声明 / Disclaimer

本工具**仅用于学习研究及个人合理使用** / For educational research and personal reasonable use only.
- 查询结果来自公开数据库原始数据，不保证完全准确，请结合专业工具与原始数据复核。
- 请遵守各数据库使用条款（NCBI 要求 ≥3 秒/请求并提供联系方式，本项目已内置）。
- 涉及临床/药物/医疗决策时，请咨询专业人士。使用本工具产生的任何风险与法律责任由使用者自行承担。

---

## ☕ 支持作者 / Support

如果 BioMCP 帮到了你，欢迎扫码赞赏支持，让我有动力持续更新～

<img src="assets/donate.png" alt="赞赏码 / Donation QR" width="200">

---

## 📄 License

[MIT](./LICENSE) © 2026 qgeng1465
