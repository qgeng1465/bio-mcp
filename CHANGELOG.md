# Changelog

All notable changes to **BioMCP** are documented here. 记录 BioMCP 的版本变更。

## [0.4.0] - 2026-08-11

### Added 新增
- **7 个新数据库 / 7 new databases**（全部零配置直连 / all zero-config direct access）:
  - **EBI ENA** 欧洲核苷酸档案 / nucleotide archive: `ena_sequence_search` 核酸序列（微生物/病毒/质粒，tax_tree 语法）
  - **EBI MGnify** 微生物组 / microbiome: `microbiome_study_search` 宏基因组研究（细菌/古菌/病毒）
  - **Reactome** 生物通路 / pathways: `reactome_pathway_search`（信号转导/代谢/DNA 修复）
  - **OpenAlex** 学术文献 / scholarly works: `openalex_work_search`（被引/作者/期刊）
  - **LIPID MAPS** 脂质组学 / lipidomics: `lipid_lookup`（名称/分子式/SMILES/DB 交叉引用）
  - **EBI EMDB** 冷冻电镜结构 / cryo-EM: `emdb_structure_lookup`（标题/作者/分辨率/组分）
  - **EBI IntAct** 实验分子互作 / experimental interactions: `intact_interactions`（检测方法/MI-score/文献）
- **数据库 19 → 26，工具 33 → 40** / databases 19→26, tools 33→40
- 全部 7 个新工具均以真实数据端到端验证（40/40 通过）/ all 7 new tools E2E validated with real data

### Changed 变更
- README 工具表新增 文献（OpenAlex）/ 核酸与质粒（ENA）/ 微生物组 / 脂质组学 分类，通路与互作分类补充 Reactome、IntAct
- 架构图与目录结构更新至 26 客户端 / 40 工具

### Note 说明
- 本轮所有新数据库均位于 EBI / Reactome / OpenAlex / LIPID MAPS 等免密钥服务；NCBI 在开发期网络不可达，其既有工具保持 v0.3 已验证状态，NCBI 新扩展（Gene/Protein/SRA）顺延至下一版本

## [0.3.0] - 2026-08-11

### Added 新增
- **4 个新数据库 / 4 new databases**（全部零配置直连 / all zero-config direct access）:
  - **GlyGen** 糖组学 / glycomics: `glycan_lookup` 糖苷结构（组成/质量/IUPAC）、`protein_glycosylation` 蛋白糖基化位点
  - **EBI UniParc** 蛋白序列归档 / protein archive: `uniparc_search`、`uniparc_by_id`（UPI/交叉引用/序列）
  - **EBI Metabolights** 代谢组学 / metabolomics: `metabolomics_study` 研究详情（技术/设计/因子）、`metabolomics_latest` 最新研究
  - **Human Protein Atlas** 蛋白组织图谱 / tissue atlas: `protein_tissue_expression`（组织表达/亚细胞定位）
- **NCBI 新检索能力 / new NCBI search capabilities**:
  - `genome_assembly_search` 基因组组装（微生物/细菌/病毒/真核）/ genome assemblies
  - `dbsnp_search` 遗传变异（rsID/等位基因/临床意义）/ dbSNP variants
  - `plasmid_search` 质粒/载体序列 / plasmid sequences
- **数据库 15 → 19，工具 23 → 33** / databases 15→19, tools 23→33

### Changed 变更
- README 工具表新增 糖组学 / 代谢组学 / 核酸与质粒 / 蛋白图谱 分类
- NCBI 客户端扩展 Assembly / dbSNP / nuccore 三个 esearch 系列方法

### Removed 移除
- DisGeNET（需要 API key，无法零配置直连）/ requires API key

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
