# Changelog

All notable changes to **BioMCP** are documented here. 记录 BioMCP 的版本变更。

## [0.2.0] - 2026-08-11

### Added 新增
- **8 个新数据库 / 8 new databases**（全部零配置直连 / all zero-config direct access）:
  - EuropePMC 全文文献检索 / full-text literature (`europepmc_search`)
  - AlphaFold DB AI 蛋白结构预测 / AI-predicted protein structures (`alphafold_structure`)
  - ChEMBL 药物活性 / drug bioactivity (`chembl_drug_search`)
  - CELLxGENE 单细胞数据 / single-cell datasets (`cellxgene_search`)
  - UCSC 基因组浏览器 / genome browser (`ucsc_genome_info`)
  - NCBI Taxonomy 物种分类 / species taxonomy (`taxonomy_lookup`)
  - NCBI GEO 基因表达数据集 / expression datasets (`geo_dataset_search`)
- **组合工具 / combined tool**: `gene_full_profile` 多库并发交叉验证 / concurrent multi-DB cross-validation (Ensembl + UniProt + STRING + PubMed)
- **架构 / architecture**: 线程安全 LRU 缓存层 / thread-safe LRU cache layer（`core/cache.py`）
- **项目成熟化 / project maturity**: 双语描述（中英）、`py.typed`、GitHub Actions CI、CHANGELOG

### Changed 变更
- 数据库数量 6 → 15，工具数量 6 → 23 / databases 6→15, tools 6→23
- Enrichr 替换 g:Profiler（大陆直连更稳）/ Enrichr engine (reliable from CN networks)
- KEGG 通路基因解析改用 `get` 端点（修复 400）/ KEGG parsing via `get` endpoint
- Ensembl 同源查询改用 `homology/symbol` 端点 / Ensembl homologs via symbol endpoint

### Removed 移除
- OpenGWAS（2024-05 起强制 API token，无法直连）/ requires token since 2024-05
- SGD（官网 API 已废弃返回 HTML）/ deprecated API

## [0.1.0] - 2026-08-10

### Added 新增
- 首个版本 / initial release：6 工具 / 6 tools
  - PubMed 文献 / `pubmed_search`
  - NCBI 序列 / `ncbi_fetch_sequence`
  - BLAST 同源比对 / `blast_search`
  - PDB 结构 / `pdb_structure_summary`
  - GO/KEGG 富集 / `gene_enrichment`
  - UniProt 注释 / `uniprot_annotate`
- MIT License、双语 README、捐赠二维码 / MIT license, bilingual README, donation QR
