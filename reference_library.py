# reference_library.py
"""PsychonautWiki 物质 × 主观效应参考集的只读加载层。

数据文件由 ``tools/build_effect_reference.py`` 生成：
    references/substance_effects.json
    references/effect_taxonomy.json

本模块不参与 PK-PD 数值计算；它只提供“物质 → 主观效应 → 现象学标签”
的检索层，供 API / UI 展示。缺少文件时不会让应用启动失败。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent
REFERENCE_DIR = BASE_DIR / "references"
SUBSTANCE_FILE = REFERENCE_DIR / "substance_effects.json"
TAXONOMY_FILE = REFERENCE_DIR / "effect_taxonomy.json"

ALLOWED_TAGS = (
    "pattern_formation",
    "spatial_warping",
    "chromatic_distortion",
    "temporal_persistence",
    "perceptual_reorganization",
)


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


_SUBSTANCE_DOC = _load_json(SUBSTANCE_FILE) or {"meta": {}, "substances": []}
_TAXONOMY_DOC = _load_json(TAXONOMY_FILE) or {"categories": [], "effect_count": 0}

REFERENCE_META: Dict[str, Any] = _SUBSTANCE_DOC.get("meta", {}) or {}
SUBSTANCE_REFERENCES: List[Dict[str, Any]] = _SUBSTANCE_DOC.get("substances", []) or []
EFFECT_TAXONOMY: Dict[str, Any] = _TAXONOMY_DOC
REFERENCE_BY_ID: Dict[str, Dict[str, Any]] = {
    item["id"]: item for item in SUBSTANCE_REFERENCES if isinstance(item, dict) and item.get("id")
}


def reference_available() -> bool:
    return bool(SUBSTANCE_REFERENCES)


def reference_count() -> int:
    return len(SUBSTANCE_REFERENCES)


def get_reference(substance_id: str) -> Optional[Dict[str, Any]]:
    return REFERENCE_BY_ID.get(substance_id)


def list_reference_summaries() -> List[Dict[str, Any]]:
    """返回适合列表展示的轻量摘要（不含全部效应文本）。"""
    summaries: List[Dict[str, Any]] = []
    for item in SUBSTANCE_REFERENCES:
        phenomenology = item.get("phenomenology") or {}
        counts = item.get("effect_counts") or {}
        summaries.append({
            "id": item.get("id"),
            "name": item.get("name"),
            "title": item.get("title"),
            "aliases": item.get("aliases", []),
            "group": item.get("group"),
            "family": item.get("family"),
            "effect_count": item.get("effect_count", counts.get("total", 0)),
            "effect_counts": {
                "visual": counts.get("visual", 0),
                "cognitive": counts.get("cognitive", 0),
                "physical": counts.get("physical", 0),
            },
            "primary_tags": phenomenology.get("primary_tags", []),
            "tags": phenomenology.get("tags", []),
            "strength": phenomenology.get("strength", {}),
            "source": {
                "url": (item.get("source") or {}).get("url"),
                "revid": (item.get("source") or {}).get("revid"),
                "timestamp": (item.get("source") or {}).get("timestamp"),
            },
        })
    return summaries


def get_taxonomy() -> Dict[str, Any]:
    """返回分类树（去掉仅供构建期使用的内部 index）。"""
    return {
        "source": EFFECT_TAXONOMY.get("source"),
        "list_source": EFFECT_TAXONOMY.get("list_source"),
        "effect_count": EFFECT_TAXONOMY.get("effect_count", 0),
        "categories": EFFECT_TAXONOMY.get("categories", []),
    }
