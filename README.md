# 🧬 BioMCP — 生物信息学 MCP 服务器

> **BioMCP** is an open-source **MCP server** that connects any AI assistant directly to public bioinformatics databases — PubMed, NCBI, BLAST, PDB, UniProt and Enrichr.
>
> BioMCP 是一个开源的 **MCP 服务器**，让任意 AI 助手直接查询公开生物数据库：PubMed 文献、NCBI 序列、BLAST 比对、PDB 蛋白质结构、UniProt 蛋白注释、GO/KEGG 富集分析。

![mcp](https://img.shields.io/badge/MCP-Server-7c5cff?style=flat-square)
![python](https://img.shields.io/badge/Python-3.10%2B-2ea44f?style=flat-square)
![license](https://img.shields.io/badge/License-MIT-blue?style=flat-square)
![platform](https://img.shields.io/badge/Platform-win%20%7C%20mac%20%7C%20linux-lightgrey?style=flat-square)

---

## ✨ 特性 / Features

- 🔌 **标准 MCP 协议** — 基于官方 MCP SDK，stdio 传输，兼容所有 MCP 客户端
- 🧬 **6 个生物信息学工具** — 文献 / 序列 / 比对 / 结构 / 注释 / 富集全流程
- ⚡ **零配置使用** — `pip install bio-mcp` 一条命令，无需数据库、无需密钥
- 🌐 **数据公开权威** — 全部来自 NCBI / RCSB PDB / UniProt / Enrichr 官方 API
- 🐌 **智能限速** — 内置 NCBI 3 秒/请求限速与重试退避，遵守学术 API 规范
- 🏷️ **中英双语** — 命令与输出双语，国内网络可达（已适配 Enrichr 替代 g:Profiler）

---

## 📦 安装 / Install

```bash
# 1. 安装（需要 Python 3.10+）
pip install bio-mcp

# 2. 启动（stdio 模式，供 MCP 客户端调用）
bio-mcp
```

### 手动安装（源码）

```bash
git clone https://github.com/qgeng1465/bio-mcp.git
cd bio-mcp
pip install .
# 或开发模式
pip install -e .[test]
```

---

## 🚀 快速开始 / Quick Start

在任何支持 MCP 的 AI 助手 / IDE 中注册 BioMCP：

```json
{
  "mcpServers": {
    "bio-mcp": {
      "command": "bio-mcp"
    }
  }
}
```

然后在对话中直接使用：

```
🧬 帮我查一下 BRCA1 相关的最新文献
🧬 下载 CYP2D6 的蛋白序列
🧬 对这段 DNA 做 BLAST 比对：ATGC...
🧬 查一下 PDB 1CRN 的结构
🧬 分析基因列表 BRCA1,TP53,EGFR,ATM,RAD51 的富集
🧬 查 UniProt P04637 的注释
```

---

## 🔧 工具 / Tools

| 工具 | 功能 | 数据源 |
|---|---|---|
| `pubmed_search` | 检索 PubMed 文献（标题/作者/期刊/PMID/DOI） | NCBI E-utilities |
| `ncbi_fetch_sequence` | 下载核酸/蛋白序列（FASTA/GenBank） | NCBI E-utilities |
| `blast_search` | DNA/蛋白同源 BLAST 比对，返回 top hits | NCBI BLAST |
| `pdb_structure_summary` | 蛋白质结构查询（分辨率/方法/链序列） | RCSB PDB |
| `uniprot_annotate` | 蛋白注释（名称/基因/功能/GO） | UniProt |
| `gene_enrichment` | GO/KEGG/Reactome 通路富集分析 | Enrichr |

---

## 💬 示例输出 / Example Output

**pubmed_search**

```
PubMed 检索：`BRCA1 breast cancer`
命中 1,248 篇，显示前 3 篇：

### 1. Germline BRCA1 and BRCA2 mutations in breast cancer
- 作者: Doe J, Smith A et al.
- 期刊: Nature Genetics (2024 Feb)
- PMID: 12345678 | DOI: 10.1038/s41588-024-xxxxx
```

**gene_enrichment**

```
# 基因富集分析（GO 生物过程）

输入 5 个基因，在 4,312 个通路中发现 12 个显著富集项（p<0.05）：

| # | 通路/GO 项 | p 值 | 校正 p | 重叠基因 |
|---|-----------|------|--------|----------|
| 1 | response to ionizing radiation (GO:0010212) | 7.70e-10 | 2.1e-06 | BRCA1, TP53, ATM |
| 2 | DNA damage response ... | 1.29e-07 | ... | BRCA1, TP53, ATM, RAD51 |
```

---

## 🏗️ 架构 / Architecture

```
┌─────────────────────────────────────────────────────┐
│                   MCP Client                        │
│        (任意支持 MCP 的 AI 助手 / IDE)              │
└───────────────────────┬─────────────────────────────┘
                        │  stdio (JSON-RPC 2.0)
┌───────────────────────▼─────────────────────────────┐
│                 bio-mcp server                       │
│  ┌───────────────────────────────────────────────┐  │
│  │  pubmed    ncbi    blast    pdb    uniprot    │  │
│  │  _search  _fetch   _search  _struct  _annotate│  │
│  │                  gene_enrichment              │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │  core:  BioHTTP（重试/退避/限速/超时）          │  │
│  └───────────────────────────────────────────────┘  │
└───────┬────────────┬───────────┬────────────┬───────┘
        │            │           │            │
   ┌────▼────┐  ┌────▼────┐ ┌────▼────┐ ┌─────▼─────┐
   │  NCBI   │  │  RCSB   │ │ UniProt │ │  Enrichr  │
   │ E-utils │  │   PDB   │ │  REST   │ │   API     │
   └─────────┘  └─────────┘ └─────────┘ └───────────┘
```

### 为什么用 Enrichr 而不是 g:Profiler？

g:Profiler（爱沙尼亚）在国内网络下常不可达，导致富集功能不可用；Enrichr（Ma'ayan Lab）国内可达且提供 GO/KEGG/Reactome/WikiPathways 等数百个基因集库。BioMCP 默认采用 Enrichr，保证开箱即用。

---

## 📁 目录结构 / Project Structure

```
bio-mcp/
├── src/bio_mcp/
│   ├── server.py            # MCP server 入口（装配所有工具）
│   ├── core/                # 数据源客户端（HTTP 封装）
│   │   ├── http.py          #   BioHTTP：重试/退避/限速
│   │   ├── ncbi.py          #   NCBI E-utilities + BLAST
│   │   ├── rcsb.py          #   RCSB PDB
│   │   ├── uniprot.py       #   UniProt REST
│   │   └── enrichr.py       #   Enrichr 富集
│   └── tools/               # MCP 工具定义
│       ├── pubmed.py
│       ├── ncbi.py
│       ├── blast.py
│       ├── pdb.py
│       ├── uniprot.py
│       └── enrichment.py
├── tests/                   # 单元测试（不依赖网络）
├── examples/                # 客户端配置示例
└── pyproject.toml
```

---

## 🧪 测试 / Testing

```bash
# 单元测试（离线，mock 外部 API）
python -m pytest tests/ -v

# 端到端测试（真实调用公开数据库）
python _e2e_test.py
```

---

## ⚠️ 免责声明 / Disclaimer

本工具**仅用于学习研究及个人合理使用**。
- 查询结果来自公开数据库原始数据，不保证完全准确，请结合专业工具与原始数据复核。
- 请遵守各数据库使用条款（NCBI 要求 ≥3 秒/请求并提供联系方式，本项目已内置）。
- 涉及临床/药物/医疗决策时，请咨询专业人士。使用本工具产生的任何风险与法律责任由使用者自行承担。

---

## ☕ 支持作者 / Support

如果 BioMCP 帮到了你，欢迎扫码赞赏支持，让我有动力持续更新～

<img src="assets/donate.png" alt="赞赏码" width="200">

---

## 📄 License

[MIT](./LICENSE) © 2026 qgeng1465
