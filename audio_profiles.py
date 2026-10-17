# audio_profiles.py
"""Derive an audio-effect profile for each substance from the PsychonautWiki reference set.

The profile is a heuristic mapping from reported auditory / multisensory effects
to Web Audio parameters. It is **not** a psychoacoustic measurement and does not
describe what a person will actually hear.

Dimensions (all normalized to 0..1):
    clarity        auditory enhancement / acuity / music appreciation
    suppression    auditory suppression / muffled hearing
    distortion     auditory distortion / misinterpretation
    hallucination  auditory hallucination / autonomous voice phenomena
    tinnitus       tinnitus
    synaesthesia   cross-modal audio→visual coupling
    time_warp      time distortion / temporal scaling / recursion
    dissociation   disconnective / depersonalization / derealization effects
    arousal        stimulation / wakefulness
    sedation       sedation / sleepiness / muscle relaxation
    intensity      maximum of the above (how strongly the auditory field is altered)
"""
from __future__ import annotations

import math
import re
from typing import Any, Dict, List

from reference_library import SUBSTANCE_REFERENCES

AUDIO_KEYS = (
    "clarity",
    "suppression",
    "distortion",
    "hallucination",
    "tinnitus",
    "synaesthesia",
    "time_warp",
    "dissociation",
    "arousal",
    "sedation",
    "intensity",
)

AUDIO_LABELS = {
    "clarity": "清晰度 / 听觉增强",
    "suppression": "听觉抑制 / 闷堵",
    "distortion": "听觉畸变",
    "hallucination": "幻听 / 语音",
    "tinnitus": "耳鸣",
    "synaesthesia": "联觉耦合",
    "time_warp": "时间拉伸 / 回声",
    "dissociation": "解离 / 空间剥离",
    "arousal": "唤醒 / 刺激",
    "sedation": "镇静 / 困倦",
    "intensity": "总体听觉扰动",
}

RULES: Dict[str, List[str]] = {
    "clarity": [
        "auditory acuity enhancement", "auditory enhancement", "increased music appreciation",
        "auditory processing acceleration",
    ],
    "suppression": [
        "auditory acuity suppression", "auditory suppression", "auditory processing deceleration",
    ],
    "distortion": [
        "auditory distortion", "auditory misinterpretation", "flanging", "reverb",
    ],
    "hallucination": [
        "auditory hallucination", "external auditory hallucination",
        "internal auditory hallucination", "autonomous voice communication",
    ],
    "tinnitus": ["tinnitus"],
    "synaesthesia": ["synaesthesia", "synesthesia"],
    "time_warp": ["time distortion", "temporal scaling", "recursion", "memory replays"],
    "dissociation": [
        "cognitive disconnection", "physical disconnection", "visual disconnection",
        "derealization", "depersonalization", "dissociation",
    ],
    "arousal": ["stimulation", "wakefulness", "increased music appreciation"],
    "sedation": ["sedation", "sleepiness", "physical fatigue", "muscle relaxation"],
}

# Reference IDs follow the PsychonautWiki titles; SUBSTANCE_DB uses shorter IDs.
REFERENCE_TO_DB: Dict[str, str] = {item["id"]: item["id"] for item in SUBSTANCE_REFERENCES}
REFERENCE_TO_DB.update({
    "lsd": "lsd_25",
    "psilocybin": "psilocybin_mushrooms",
    "nitrous": "nitrous_oxide",
})
REFERENCE_TO_DB.pop("4_aco_dmt", None)  # not present in the simulation DB

# LSA is in SUBSTANCE_DB but not in the current reference snapshot; borrow LSD
# at reduced intensity and flag the fallback explicitly.
DB_FALLBACK = {"lsa": "lsd_25"}


def _norm(value: str) -> str:
    value = value.casefold()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _score(matches: List[str]) -> float:
    if not matches:
        return 0.0
    return round(min(1.0, 0.35 + 0.20 * (len(matches) - 1)), 3)


def _build_profile(reference: Dict[str, Any], db_id: str) -> Dict[str, Any]:
    effects = reference.get("effects", []) or []
    scores: Dict[str, float] = {}
    evidence: Dict[str, List[str]] = {}
    for key, needles in RULES.items():
        matches = sorted({
            effect.get("name", "")
            for effect in effects
            if effect.get("name") and any(needle in _norm(effect["name"]) for needle in needles)
        })
        scores[key] = _score(matches)
        if matches:
            evidence[key] = matches[:8]

    auditory = [effect for effect in effects if effect.get("category") == "auditory"]
    multisensory = [effect for effect in effects if effect.get("category") == "multisensory"]
    scores["intensity"] = round(max(scores.values()), 3)

    return {
        "id": db_id,
        "reference_id": reference.get("id"),
        "name": reference.get("name"),
        "title": reference.get("title"),
        "group": reference.get("group"),
        "family": reference.get("family"),
        "scores": {key: round(float(scores.get(key, 0.0)), 3) for key in AUDIO_KEYS},
        "evidence": evidence,
        "auditory_effects": [effect.get("name") for effect in auditory],
        "synaesthesia_effects": [effect.get("name") for effect in multisensory],
        "auditory_effect_count": len(auditory),
        "visual_effect_count": (reference.get("effect_counts") or {}).get("visual", 0),
        "fallback": False,
    }


AUDIO_PROFILES: Dict[str, Dict[str, Any]] = {}
for _reference in SUBSTANCE_REFERENCES:
    _db_id = REFERENCE_TO_DB.get(_reference.get("id", ""))
    if _db_id:
        AUDIO_PROFILES[_db_id] = _build_profile(_reference, _db_id)

for _db_id, _source_id in DB_FALLBACK.items():
    if _source_id in AUDIO_PROFILES and _db_id not in AUDIO_PROFILES:
        _fallback = {
            key: (value if key not in {"id", "reference_id", "name", "title", "scores", "evidence",
                                       "auditory_effects", "synaesthesia_effects", "fallback"}
                  else value)
            for key, value in AUDIO_PROFILES[_source_id].items()
        }
        _fallback.update({
            "id": _db_id,
            "reference_id": AUDIO_PROFILES[_source_id].get("reference_id"),
            "name": "LSA / 麦角酸酰胺",
            "title": "LSA",
            "fallback": True,
        })
        _fallback["scores"] = {
            key: round(value * 0.8, 3)
            for key, value in AUDIO_PROFILES[_source_id]["scores"].items()
        }
        AUDIO_PROFILES[_db_id] = _fallback


def get_audio_profile(substance_id: str) -> Dict[str, Any] | None:
    return AUDIO_PROFILES.get(substance_id)


_REFERENCE_PROFILES = {
    profile["reference_id"]: profile
    for profile in AUDIO_PROFILES.values()
    if profile.get("reference_id") and not profile.get("fallback")
}


def get_audio_profile_for_reference(reference_id: str) -> Dict[str, Any] | None:
    return _REFERENCE_PROFILES.get(reference_id)


def list_audio_profiles() -> List[Dict[str, Any]]:
    return list(AUDIO_PROFILES.values())


def compute_audio_uniforms(substance_effects: Dict[str, float]) -> Dict[str, Any]:
    """Mix audio dimensions by current PK effect strength.

    Uses an energy-weighted RMS instead of a linear average. A strong effect from
    one substance is therefore not washed out by a weak co-active substance.
    """
    total = sum(max(0.0, float(value)) for value in (substance_effects or {}).values())
    if total <= 1e-9:
        return {
            **{key: 0.0 for key in AUDIO_KEYS},
            "active": False,
            "sources": [],
        }

    accumulator = {key: 0.0 for key in AUDIO_KEYS}
    sources = []
    for substance_id, strength in (substance_effects or {}).items():
        profile = AUDIO_PROFILES.get(substance_id)
        weight = max(0.0, float(strength))
        if not profile or weight <= 1e-9:
            continue
        for key in AUDIO_KEYS:
            value = profile["scores"].get(key, 0.0)
            # 能量加权 RMS：比线性平均更保留个别物质的强效应，避免被低剂量成分稀释。
            accumulator[key] += value * value * weight
        sources.append({
            "id": substance_id,
            "name": profile.get("name"),
            "effect": round(weight, 3),
            "auditory_effects": profile.get("auditory_effect_count", 0),
        })

    result = {key: round(math.sqrt(accumulator[key] / total), 3) for key in AUDIO_KEYS}
    result["intensity"] = round(max(result[key] for key in AUDIO_KEYS if key != "intensity"), 3)
    result["active"] = bool(sources)
    result["sources"] = sources
    return result
