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
