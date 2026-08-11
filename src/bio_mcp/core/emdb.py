"""EBI EMDB 客户端：冷冻电镜结构检索。

EMDB（Electron Microscopy Data Bank，https://www.ebi.ac.uk/emdb）
收录冷冻电镜 / 电子显微镜三维结构（EMD 编号）。
API：/emdb/api/entry/{id}，免鉴权。
参考：https://www.ebi.ac.uk/emdb/api
"""
from __future__ import annotations

from typing import Any

from bio_mcp.core.http import BioHTTP

BASE = "https://www.ebi.ac.uk/emdb/api/entry"


def _find_resolution(node: Any, depth: int = 0) -> str:
    """在嵌套结构里递归找第一个 resolution 数值（支持 dict/数值/字符串）。"""
    if depth > 8:
        return ""
    if isinstance(node, dict):
        for k, v in node.items():
            if "resolution" in str(k).lower():
                if isinstance(v, dict):  # {"valueOf_": "2.2", "units": "Å"}
                    val = v.get("valueOf_") or v.get("value")
                    if val is not None:
                        units = v.get("units") or "Å"
                        return f"{val} {units}".strip()
                elif isinstance(v, (int, float)):
                    return f"{v} Å"
                elif isinstance(v, str) and v.strip() and v.strip()[0].isdigit():
                    return f"{v.strip()} Å"
            found = _find_resolution(v, depth + 1)
            if found:
                return found
    elif isinstance(node, list):
        for item in node:
            found = _find_resolution(item, depth + 1)
            if found:
                return found
    return ""


class EMDBClient:
    def __init__(self) -> None:
        self._http = BioHTTP(base_url=BASE, timeout=30.0)

    # ---- 按 EMD 编号查询结构 ----
    def entry_lookup(self, emdb_id: str) -> dict[str, Any]:
        """按 EMD 编号查询冷冻电镜结构条目。

        emdb_id 示例：EMD-1234、1234。
        """
        emdb_id = emdb_id.strip().upper()
        if not emdb_id.startswith("EMD-"):
            emdb_id = "EMD-" + emdb_id
        resp = self._http.get(emdb_id)
        data = resp.json()
        admin = data.get("admin", {}) or {}
        authors = [
            a.get("valueOf_", "")
            for a in ((admin.get("authors_list") or {}).get("author") or [])
            if a.get("valueOf_")
        ]
        samples: list[dict[str, Any]] = []
        for m in (
            ((data.get("sample") or {}).get("macromolecule_list") or {})
            .get("macromolecule") or []
        ):
            nm = m.get("name") or {}
            org = ((m.get("natural_source") or {}).get("organism") or {})
            samples.append(
                {
                    "name": nm.get("valueOf_", "") or str(nm.get("name", "")),
                    "organism": org.get("valueOf_", ""),
                    "oligomeric_state": m.get("oligomeric_state", ""),
                    "copies": m.get("number_of_copies", ""),
                }
            )
        sdl = (
            ((data.get("structure_determination_list") or {})
             .get("structure_determination") or [{}])[0] or {}
        )
        kd = admin.get("key_dates") or {}
        # current_status 可能是字符串或 dict（如 {"status": "REL"}）
        cs = admin.get("current_status")
        status = ""
        if isinstance(cs, str):
            status = cs.strip()
        elif isinstance(cs, dict):
            status = str(cs.get("status", "")).strip()
        return {
            "emdb_id": data.get("emdb_id", emdb_id),
            "title": (admin.get("title") or "").strip(),
            "authors": authors[:20],
            "keywords": admin.get("keywords", []),
            "resolution": _find_resolution(sdl) or _find_resolution(data),
            "aggregation_state": sdl.get("aggregation_state", ""),
            "samples": samples,
            "deposition": (kd.get("deposition") or "")[:10],
            "release": (kd.get("map_release") or kd.get("header_release") or "")[:10],
            "status": status,
        }

    def close(self) -> None:
        self._http.close()
