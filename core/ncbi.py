"""NCBI E-utilities 客户端：esearch / efetch / esummary / blast。

遵循 NCBI 官方规范：限速 3 秒/请求，携带 email + tool。
参考：https://www.ncbi.nlm.nih.gov/books/NBK25501/
"""
from __future__ import annotations

from typing import Any, Optional

from bio_mcp.core.http import BioHTTP, NCBI_EMAIL, NCBI_RATE_LIMIT_SECONDS, NCBI_TOOL

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


class NCBIClient:
    def __init__(self) -> None:
        self._http = BioHTTP(
            base_url=BASE,
            timeout=60.0,
            rate_limit=NCBI_RATE_LIMIT_SECONDS,
        )

    # ---- esearch: 关键字检索，返回 ID 列表 ----
    def esearch(
        self,
        db: str,
        term: str,
        retmax: int = 10,
        sort: Optional[str] = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "db": db,
            "term": term,
            "retmax": retmax,
            "retmode": "json",
            "tool": NCBI_TOOL,
            "email": NCBI_EMAIL,
        }
        if sort:
            params["sort"] = sort
        resp = self._http.get("esearch.fcgi", params=params)
        data = resp.json().get("esearchresult", {})
        return {
            "count": int(data.get("count", 0)),
            "ids": data.get("idlist", []),
            "query": data.get("querytranslation", term),
        }

    # ---- esummary: 批量取摘要（期刊/年份/标题等）----
    def esummary(self, db: str, ids: list[str]) -> list[dict[str, Any]]:
        if not ids:
            return []
        resp = self._http.get(
            "esummary.fcgi",
            params={
                "db": db,
                "id": ",".join(ids),
                "retmode": "json",
                "tool": NCBI_TOOL,
                "email": NCBI_EMAIL,
            },
        )
        result = resp.json().get("result", {})
        out: list[dict[str, Any]] = []
        for uid in ids:
            if uid in result:
                out.append(result[uid])
        return out

    # ---- efetch: 拉取 FASTA / 序列记录 ----
    def efetch(
        self,
        db: str,
        ids: list[str],
        rettype: str = "fasta",
        retmode: str = "text",
    ) -> str:
        if not ids:
            return ""
        resp = self._http.get(
            "efetch.fcgi",
            params={
                "db": db,
                "id": ",".join(ids),
                "rettype": rettype,
                "retmode": retmode,
                "tool": NCBI_TOOL,
                "email": NCBI_EMAIL,
            },
        )
        return resp.text

    # ---- Taxonomy：物种分类检索 ----
    def taxonomy_lookup(self, query: str) -> dict[str, Any]:
        """按名称/ID 检索 NCBI Taxonomy，返回学名、常用名、层级。"""
        es = self.esearch("taxonomy", query, retmax=5)
        ids = es["ids"]
        if not ids:
            return {"count": 0, "nodes": []}
        nodes: list[dict[str, Any]] = []
        for rec in self.esummary("taxonomy", ids):
            nodes.append(
                {
                    "taxid": rec.get("uid"),
                    "scientific_name": rec.get("title", ""),
                    "common_name": rec.get("commonname", ""),
                    "rank": rec.get("rank", ""),
                    "lineage": rec.get("lineage", ""),
                }
            )
        return {"count": es["count"], "nodes": nodes}

    # ---- Assembly：基因组组装检索（细菌/病毒/真核）----
    def assembly_search(self, term: str, retmax: int = 5) -> dict[str, Any]:
        """检索 NCBI Assembly 基因组组装（细菌/病毒/真核）。

        term 示例：
          "Escherichia coli[Organism]"
          "SARS-CoV-2[Organism]"
          "GRCh38[Assembly Name]"
        """
        es = self.esearch("assembly", term, retmax=retmax)
        ids = es["ids"]
        if not ids:
            return {"count": 0, "assemblies": []}
        assemblies: list[dict[str, Any]] = []
        for rec in self.esummary("assembly", ids):
            assemblies.append(
                {
                    "accession": rec.get("assemblyaccession"),
                    "name": rec.get("assemblyname", ""),
                    "organism": rec.get("organism", ""),
                    "species": rec.get("speciesname", ""),
                    "taxid": rec.get("taxid"),
                    "type": rec.get("assemblytype", ""),
                    "status": rec.get("assemblystatus", ""),
                    "biosample": rec.get("biosampleaccn", ""),
                    "bioproject": next(
                        (p for p in (rec.get("gb_bioprojects") or []) if p), ""),
                }
            )
        return {"count": es["count"], "assemblies": assemblies}

    # ---- dbSNP：人类/模式生物变异检索 ----
    def dbsnp_search(self, term: str, retmax: int = 5) -> dict[str, Any]:
        """检索 NCBI dbSNP 变异。

        term 示例：
          "BRCA1[Gene Name] AND Homo sapiens[Organism]"
          "rs1800057[RS]"
        """
        es = self.esearch("snp", term, retmax=retmax)
        ids = es["ids"]
        if not ids:
            return {"count": 0, "variants": []}
        variants: list[dict[str, Any]] = []
        for rec in self.esummary("snp", ids):
            variants.append(
                {
                    "rsid": rec.get("snp_id"),
                    "chrom": rec.get("chr", ""),
                    "position": rec.get("chrpos", ""),
                    "alleles": rec.get("allele", ""),
                    "clinical_significance": (rec.get("clinical_significance") or "").strip()[:120],
                    "function": rec.get("fxn_class", ""),
                    "gene": ", ".join(
                        (g.get("name") or "") for g in (rec.get("genes") or []) if g.get("name")
                    ),
                    "summary": (rec.get("docsum") or "").strip()[:200],
                }
            )
        return {"count": es["count"], "variants": variants}

    # ---- nuccore：核酸/质粒序列检索 ----
    def plasmid_search(self, term: str, retmax: int = 5) -> dict[str, Any]:
        """检索 NCBI nuccore 中的质粒序列。

        term 示例：
          "pET-28a[Title]"
          "plasmid[Title] AND Escherichia coli[Organism]"
        """
        es = self.esearch("nuccore", term, retmax=retmax)
        ids = es["ids"]
        if not ids:
            return {"count": 0, "plasmids": []}
        plasmids: list[dict[str, Any]] = []
        for rec in self.esummary("nuccore", ids):
            plasmids.append(
                {
                    "accession": rec.get("caption"),
                    "title": (rec.get("title") or "").strip(),
                    "organism": rec.get("organism", ""),
                    "length": rec.get("slen"),
                    "genbank": rec.get("gi") or rec.get("uid"),
                }
            )
        return {"count": es["count"], "plasmids": plasmids}

    # ---- GEO：基因表达数据集检索 ----
    def geo_search(self, term: str, retmax: int = 10) -> dict[str, Any]:
        """检索 GEO 基因表达数据集（gds db），返回系列标题/类型/平台/样本数。"""
        es = self.esearch("gds", term, retmax=retmax)
        ids = es["ids"]
        if not ids:
            return {"count": 0, "datasets": []}
        datasets: list[dict[str, Any]] = []
        for rec in self.esummary("gds", ids):
            datasets.append(
                {
                    "accession": rec.get("accession"),
                    "title": rec.get("title", "").strip(),
                    "gdstype": rec.get("gdstype", ""),
                    "gpl": rec.get("gpl", ""),
                    "n_samples": rec.get("n_samples"),
                    "taxon": rec.get("taxon", ""),
                    "summary": rec.get("summary", "").strip()[:300],
                }
            )
        return {"count": es["count"], "datasets": datasets}

    # ---- PubMed 检索（esearch + esummary 两步）----
    def pubmed_search(
        self, term: str, retmax: int = 10, sort: Optional[str] = None
    ) -> dict[str, Any]:
        es = self.esearch("pubmed", term, retmax=retmax, sort=sort)
        ids = es["ids"]
        articles: list[dict[str, Any]] = []
        if ids:
            for rec in self.esummary("pubmed", ids):
                articles.append(
                    {
                        "pmid": rec.get("uid"),
                        "title": rec.get("title", "").strip(),
                        "authors": rec.get("authors", []),
                        "journal": rec.get("fulljournalname") or rec.get("source", ""),
                        "date": rec.get("pubdate", ""),
                        "doi": next(
                            (a["value"] for a in rec.get("articleids", []) if a.get("idtype") == "doi"),
                            "",
                        ),
                    }
                )
        return {"count": es["count"], "query": es["query"], "articles": articles}

    # ---- BLAST 提交与轮询 ----
    def blast_submit(self, sequence: str, program: str = "blastn", db: str = "nt") -> str:
        """提交 BLAST，返回 RID（Request ID）。program: blastn/tblastn/blastp。"""
        resp = self._http.post(
            "https://blast.ncbi.nlm.nih.gov/Blast.cgi",
            data={
                "CMD": "Put",
                "PROGRAM": program,
                "DATABASE": db,
                "QUERY": sequence,
                "FORMAT_TYPE": "Text",
                "TOOL": NCBI_TOOL,
                "EMAIL": NCBI_EMAIL,
            },
        )
        # RID 形如 "RID = XXXXX"
        text = resp.text
        rid = None
        for line in text.splitlines():
            if line.strip().startswith("RID"):
                rid = line.split("=")[1].strip()
                break
        if not rid:
            raise RuntimeError(f"BLAST 提交失败：{text[:200]}")
        return rid

    def blast_poll(self, rid: str, timeout: int = 180, interval: int = 8) -> str:
        """轮询 RID 直到 Ready 或超时，返回结果文本。"""
        import time

        waited = 0
        while waited < timeout:
            resp = self._http.get(
                "https://blast.ncbi.nlm.nih.gov/Blast.cgi",
                params={
                    "CMD": "Get",
                    "RID": rid,
                    "FORMAT_TYPE": "Text",
                },
            )
            text = resp.text
            if "Status=WAITING" in text or "Status=UNKNOWN" in text:
                time.sleep(interval)
                waited += interval
                continue
            if "Status=READY" in text or "No hits found" in text or "Query=" in text:
                return text
            # 结果或错误直接返回
            return text
        raise TimeoutError(f"BLAST 轮询超时（{timeout}s），RID={rid}")

    def close(self) -> None:
        self._http.close()
