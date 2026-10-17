#!/usr/bin/env python
"""Rebuild the PsychonautWiki substance × subjective-effect reference set.

The committed ``references/`` snapshot is a curated extraction. This script
refreshes it from the PsychonautWiki MediaWiki API:

    python tools/build_effect_reference.py
    python tools/build_effect_reference.py --titles LSD Ketamine
    python tools/build_effect_reference.py --output-dir references/_test

It parses the ``== Subjective effects ==`` section, keeps the primary effect
links of each bullet (not contextual mentions in the prose), links effect names
to the SEI taxonomy, and writes JSON + Markdown snapshots.

Content is adapted from PsychonautWiki contributors under CC BY-SA 4.0.
The effect lists are anecdotal, not clinical evidence, and no dosing data is
collected.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = PROJECT_DIR / "references"
API_URL = "https://psychonautwiki.org/w/api.php"
USER_AGENT = "PsychopharmShaderLab/1.3 (educational reference builder)"

DEFAULT_TITLES = [
    "LSD", "Psilocybin mushrooms", "Mescaline", "2C-B", "2C-E", "DMT",
    "4-AcO-DMT", "AL-LAD", "DOM", "Ketamine", "Methoxetamine", "PCP",
    "Dextromethorphan", "Nitrous", "MDMA", "MDA", "Amphetamine", "Cannabis",
    "Salvinorin A", "Ibogaine", "Ayahuasca", "GHB", "Alcohol", "Caffeine", "Nicotine",
]

CURATED: Dict[str, Dict[str, Any]] = {
    "LSD": {"id": "lsd", "name": "LSD", "group": "psychedelic", "family": "lysergamide",
            "aliases": ["Lysergide", "LSD-25", "L", "Lucy", "Acid"]},
    "Psilocybin mushrooms": {"id": "psilocybin", "name": "Psilocybin / 裸盖菇素", "group": "psychedelic", "family": "tryptamine",
                             "aliases": ["Psilocybin", "Psilocin", "Magic mushrooms", "Shrooms"]},
    "Mescaline": {"id": "mescaline", "name": "Mescaline / 麦司卡林", "group": "psychedelic", "family": "phenethylamine",
                  "aliases": ["3,4,5-Trimethoxyphenethylamine"]},
    "2C-B": {"id": "2c_b", "name": "2C-B", "group": "psychedelic", "family": "phenethylamine",
             "aliases": ["Nexus", "Bromo Mescaline", "BDMPEA", "Venus"]},
    "2C-E": {"id": "2c_e", "name": "2C-E", "group": "psychedelic", "family": "phenethylamine", "aliases": []},
    "DMT": {"id": "dmt", "name": "N,N-DMT", "group": "psychedelic", "family": "tryptamine",
            "aliases": ["N,N-DMT", "Dimethyltryptamine"]},
    "4-AcO-DMT": {"id": "4_aco_dmt", "name": "4-AcO-DMT", "group": "psychedelic", "family": "tryptamine",
                  "aliases": ["Psilacetin", "4-Acetoxy-DMT", "O-Acetylpsilocin"]},
    "AL-LAD": {"id": "al_lad", "name": "AL-LAD", "group": "psychedelic", "family": "lysergamide",
               "aliases": ["N-Allyl-nor-LSD"]},
    "DOM": {"id": "dom", "name": "DOM", "group": "psychedelic", "family": "phenethylamine",
            "aliases": ["STP"]},
    "Ketamine": {"id": "ketamine", "name": "Ketamine / 氯胺酮", "group": "dissociative", "family": "arylcyclohexylamine",
                 "aliases": ["K", "Special K"]},
    "Methoxetamine": {"id": "mxe", "name": "MXE / Methoxetamine", "group": "dissociative", "family": "arylcyclohexylamine",
                      "aliases": ["MXE"]},
    "PCP": {"id": "pcp", "name": "PCP / 苯环己哌啶", "group": "dissociative", "family": "arylcyclohexylamine",
            "aliases": ["Phencyclidine", "Angel Dust"]},
    "Dextromethorphan": {"id": "dxm", "name": "DXM / 右美沙芬", "group": "dissociative", "family": "morphinan",
                         "aliases": ["DXM"]},
    "Nitrous": {"id": "nitrous", "name": "Nitrous oxide / 一氧化二氮", "group": "dissociative", "family": "inhalant",
                "aliases": ["N2O", "Laughing gas"]},
    "MDMA": {"id": "mdma", "name": "MDMA", "group": "entactogen", "family": "substituted amphetamine",
             "aliases": ["Ecstasy", "Molly", "XTC"]},
    "MDA": {"id": "mda", "name": "MDA", "group": "entactogen", "family": "substituted amphetamine",
            "aliases": ["Tenamfetamine", "Sally", "Sass"]},
    "Amphetamine": {"id": "amphetamine", "name": "Amphetamine / 苯丙胺", "group": "stimulant", "family": "substituted amphetamine",
                    "aliases": ["Amfetamine"]},
    "Cannabis": {"id": "cannabis", "name": "Cannabis / 大麻", "group": "cannabinoid", "family": "phytocannabinoid",
                 "aliases": ["THC", "Marijuana", "Weed"]},
    "Salvinorin A": {"id": "salvinorin_a", "name": "Salvinorin A / 鼠尾草素 A", "group": "oneirogen", "family": "kappa-opioid agonist",
                     "aliases": ["Salvinorin A"]},
    "Ibogaine": {"id": "ibogaine", "name": "Ibogaine / 伊博格碱", "group": "psychedelic", "family": "iboga alkaloid",
                 "aliases": ["Ibogaine"]},
    "Ayahuasca": {"id": "ayahuasca", "name": "Ayahuasca / 死藤水", "group": "psychedelic", "family": "tryptamine + MAOI",
                  "aliases": ["Yagé", "Hoasca", "Daime"]},
    "GHB": {"id": "ghb", "name": "GHB", "group": "depressant", "family": "GABAergic",
            "aliases": ["Gamma-hydroxybutyrate"]},
    "Alcohol": {"id": "alcohol", "name": "Alcohol / 乙醇", "group": "depressant", "family": "GABAergic",
                "aliases": ["Ethanol"]},
    "Caffeine": {"id": "caffeine", "name": "Caffeine / 咖啡因", "group": "stimulant", "family": "xanthine",
                 "aliases": ["1,3,7-Trimethylxanthine"]},
    "Nicotine": {"id": "nicotine", "name": "Nicotine / 尼古丁", "group": "stimulant", "family": "nicotinic agonist",
                 "aliases": ["Nicotine"]},
}

BLOCK_CATEGORY = {
    "physical": "physical", "visual": "visual", "cognitive": "cognitive",
    "auditory": "auditory", "multisensory": "multisensory", "transpersonal": "transpersonal",
    "disconnective": "disconnective", "tactile": "tactile", "smell_taste": "smell_taste",
    "aftereffects": "aftereffects", "afterglow": "aftereffects",
}
CATEGORY_ORDER = ["visual", "cognitive", "physical", "auditory", "multisensory",
                  "transpersonal", "disconnective", "tactile", "smell_taste", "aftereffects", "other"]
CATEGORY_LABELS = {
    "visual": "视觉", "cognitive": "认知 / 心理", "physical": "身体", "auditory": "听觉",
    "multisensory": "多感官", "transpersonal": "超个人", "disconnective": "解离 / 连接中断",
    "tactile": "触觉", "smell_taste": "嗅觉与味觉", "aftereffects": "后效应", "other": "其他",
}

PHENOMENOLOGY_RULES: Dict[str, List[str]] = {
    "pattern_formation": ["geometry", "symmetrical texture repetition", "environmental patterning",
                          "pattern recognition enhancement", "recursion", "machinescapes",
                          "visual processing acceleration", "8a geometry", "8b geometry"],
    "spatial_warping": ["drifting", "perspective distortion", "visual stretching", "scenery slicing",
                        "visual haze", "environmental cubism", "environmental orbism", "object alteration",
                        "texture liquidation", "changes in felt gravity", "spatial disorientation",
                        "visual flipping"],
    "chromatic_distortion": ["color enhancement", "color shifting", "color replacement", "color tinting",
                             "brightness alteration", "diffraction", "visual acuity enhancement",
                             "visual acuity suppression", "photophobia", "vibrating vision"],
    "temporal_persistence": ["tracers", "after images", "double vision", "visual processing acceleration",
                             "visual processing deceleration", "time distortion", "temporal scaling",
                             "memory replays", "recursion", "spontaneous physical movements"],
    "perceptual_reorganization": ["visual disconnection", "holes, spaces and voids", "depth perception distortions",
                                  "transformations", "ego dissolution", "depersonalization", "derealization",
                                  "identity alteration", "environmental cubism", "environmental orbism",
                                  "object alteration", "machinescapes", "unspeakable horrors", "shadow people",
                                  "perspective hallucination", "autonomous entity", "cognitive disconnection",
                                  "physical disconnection"],
}
PHENOMENOLOGY_LABELS = {
    "pattern_formation": "几何化与图案生成", "spatial_warping": "空间扭曲与流动",
    "chromatic_distortion": "色彩分离与光谱异常", "temporal_persistence": "视觉残留与时间叠影",
    "perceptual_reorganization": "边界解构与空间重组",
}
HALLMARKS = {
    "pattern_formation": {"geometry", "symmetrical texture repetition", "environmental patterning"},
    "spatial_warping": {"drifting", "perspective distortion", "environmental cubism", "environmental orbism"},
    "chromatic_distortion": {"color enhancement", "color shifting", "color tinting", "brightness alteration"},
    "temporal_persistence": {"tracers", "after images", "double vision"},
    "perceptual_reorganization": {"visual disconnection", "depth perception distortions", "ego dissolution", "transformations"},
}
HALLMARK_BOOST = 0.75

MANUAL_ALIASES = {
    "color enhancement": "Color enhancement", "color shifting": "Color shifting",
    "color replacement": "Color replacement", "color tinting": "Color tinting",
    "auditory hallucinations": "Auditory hallucination", "auditory suppression": "Auditory acuity suppression",
    "auditory enhancement": "Auditory acuity enhancement", "tactile enhancement": "Tactile intensification",
    "tactile suppression": "Tactile suppression", "geometry": "Geometry",
    "8a geometry": "Geometry", "8b geometry": "Geometry", "ego death": "Memory suppression",
    "ego dissolution": "Memory suppression", "settings sceneries and landscapes": "Settings, sceneries, and landscapes",
    "machinescapes": "Machinescapes", "unspeakable horrors": "Unspeakable horrors", "shadow people": "Shadow people",
    "empathy affection and sociability enhancement": "Empathy, affection, and sociability enhancement",
    "trouble urinating": "Difficulty urinating", "memory formation enhancement": "Memory enhancement",
}

LINK_RE = re.compile(r"\[\[([^\[\]]+?)\]\]")
HEADING_RE = re.compile(r"^\s*={3,5}\s*(.+?)\s*={3,5}\s*$")
BULLET_RE = re.compile(r"^(\*+)\s*(.*)$")
GENERIC_LABELS = {"enhancements", "enhancement", "suppressions", "suppression", "distortions",
                  "distortion", "hallucinations", "hallucination", "amplifications", "amplification",
                  "depressions", "depression", "intensifications", "intensification", "alterations",
                  "alteration", "general", "effects"}


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
def api_get(params: Dict[str, Any], retries: int = 3) -> Dict[str, Any]:
    url = API_URL + "?" + urllib.parse.urlencode(params)
    last_error: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            with urllib.request.urlopen(request, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            last_error = error
            if attempt < retries:
                time.sleep(1.2 * attempt)
    raise RuntimeError(f"PsychonautWiki API failed: {url} ({last_error})")


def chunks(items: Sequence[str], size: int) -> Iterable[Sequence[str]]:
    for index in range(0, len(items), size):
        yield items[index:index + size]


def fetch_pages(titles: Sequence[str]) -> Dict[str, Dict[str, Any]]:
    pages: Dict[str, Dict[str, Any]] = {}
    for batch in chunks(list(titles), 5):
        data = api_get({
            "action": "query", "format": "json", "formatversion": "2",
            "prop": "revisions", "rvprop": "content|ids|timestamp", "rvslots": "main",
            "redirects": "1", "titles": "|".join(batch),
        })
        for page in data.get("query", {}).get("pages", []):
            if page.get("missing") or not page.get("revisions"):
                continue
            revision = page["revisions"][0]
            content = (revision.get("slots", {}).get("main", {}) or {}).get("content")
            if not content:
                continue
            pages[page["title"]] = {
                "title": page["title"], "pageid": page.get("pageid"),
                "revid": revision.get("revid"), "timestamp": revision.get("timestamp"),
                "url": "https://psychonautwiki.org/wiki/" + urllib.parse.quote(page["title"].replace(" ", "_")),
                "content": content,
            }
        time.sleep(0.35)
    return pages


# --------------------------------------------------------------------------- #
# Wikitext utilities
# --------------------------------------------------------------------------- #
def match_braces(text: str, start: int) -> Optional[int]:
    depth = 0
    index = start
    while index < len(text) - 1:
        pair = text[index:index + 2]
        if pair == "{{":
            depth += 1
            index += 2
        elif pair == "}}":
            depth -= 1
            index += 2
            if depth == 0:
                return index
        else:
            index += 1
    return None


def strip_templates(text: str) -> str:
    out: List[str] = []
    index = 0
    while index < len(text):
        if text.startswith("{{", index):
            end = match_braces(text, index)
            if end is not None:
                index = end
                continue
        out.append(text[index])
        index += 1
    return "".join(out)


def strip_wikitext(text: str) -> str:
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.S | re.I)
    text = re.sub(r"<ref[^>]*/\s*>", "", text, flags=re.I)
    text = strip_templates(text)
    text = re.sub(r"\[\[[A-Za-z][A-Za-z _-]*::([^\]\|]+)(?:\|([^\]]+))?\]\]",
                  lambda m: m.group(2) or m.group(1), text)
    text = re.sub(r"\[\[(?:[^\]\|]+)\|([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"'{2,}", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text).replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def shorten(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    sentence = re.match(r"(.+?[.!?。！？])(?:\s|$)", cut)
    if sentence and len(sentence.group(1)) > limit * 0.5:
        return sentence.group(1).strip()
    return cut.rstrip(" ,;:，；：") + "…"


def slugify(value: str) -> str:
    value = value.casefold().replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", "_", value).strip("_") or "general"


def norm_key(value: str) -> str:
    value = html.unescape(value).casefold().replace("colour", "color").replace("&", " and ")
    value = re.sub(r"[\u2018\u2019]", "'", value)
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def parse_link(raw: str) -> Optional[Dict[str, Any]]:
    target, _, label = raw.partition("|")
    target, label = target.strip(), label.strip()
    anchor = None
    if "#" in target:
        target, anchor = target.split("#", 1)
        target, anchor = target.strip(), anchor.strip() or None
    if not target or target.casefold().startswith(("file:", "image:", "category:")):
        return None
    return {"target": target, "anchor": anchor, "label": label or target}


def clean_note(text: str) -> str:
    text = strip_wikitext(text)
    text = re.sub(r"\(\s*(?:[,;，；、]+\s*)*(?:and\s*)?\)", " ", text, flags=re.I)
    text = re.sub(r"\(\s*[,;，；、\s]*\)", " ", text)
    text = re.sub(r"\(\s*(?:and|or)\s*\)", " ", text, flags=re.I)
    text = re.sub(r"\s*,\s*(?=[,;])", "", text)
    text = re.sub(r"(?:\s*,\s*){2,}", ", ", text)
    for _ in range(2):
        text = re.sub(r"^[\s'\"“”‘’`&|\-–—:：,，;；.。]+", "", text)
        text = re.sub(r"^and\s+", "", text, flags=re.I)
    text = re.sub(r"[\s'\"“”‘’`&|]+$", "", text).strip()
    if not re.search(r"[A-Za-z0-9\u4e00-\u9fff]", text) or norm_key(text) in {"and", "or", "with", "of"}:
        return ""
    return shorten(text, 280)


def note_source(body: str) -> str:
    parts = re.split(r"(\s[-–—]\s)", body, maxsplit=1)
    prefix = LINK_RE.sub("", parts[0])
    rest = "".join(parts[1:])
    rest = LINK_RE.sub(lambda m: (parse_link(m.group(1)) or {}).get("label") or "", rest)
    return prefix + rest


# --------------------------------------------------------------------------- #
# SEI taxonomy
# --------------------------------------------------------------------------- #
TAXONOMY_MAP = {
    "visual effects": "visual", "auditory effects": "auditory", "tactile effects": "tactile",
    "disconnective effects": "disconnective", "smell and taste effects": "smell_taste",
    "multisensory effects": "multisensory", "cognitive effects": "cognitive",
    "physical effects": "physical", "uncomfortable physical effects": "physical",
}


def label_from_html(fragment: str) -> str:
    link = LINK_RE.search(fragment)
    if link:
        parsed = parse_link(link.group(1))
        if parsed:
            return parsed["label"]
    return re.sub(r"<[^>]+>", "", fragment).strip()


def taxonomy_effect(line: str) -> Optional[Dict[str, Any]]:
    bullet = BULLET_RE.match(line.strip())
    if not bullet:
        return None
    link = LINK_RE.search(bullet.group(2))
    if not link:
        return None
    parsed = parse_link(link.group(1))
    if not parsed:
        return None
    name = re.sub(r"'{2,}", "", parsed["label"]).strip() or parsed["target"]
    return {"name": name, "target": parsed["target"], "anchor": parsed["anchor"], "label": name}


def dedupe(effects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen, out = set(), []
    for effect in effects:
        key = (effect.get("target", "").casefold(), effect.get("anchor") or "", effect.get("name", "").casefold())
        if key not in seen:
            seen.add(key)
            out.append(effect)
    return out


def parse_taxonomy(wikitext: str) -> Dict[str, Any]:
    categories: List[Dict[str, Any]] = []
    h3s = list(re.finditer(r"<h3[^>]*>(.*?)</h3>", wikitext, flags=re.S | re.I))
    for index, h3 in enumerate(h3s):
        label = label_from_html(h3.group(1))
        end = h3s[index + 1].start() if index + 1 < len(h3s) else len(wikitext)
        section = wikitext[h3.end():end]
        category = TAXONOMY_MAP.get(norm_key(label), "other")
        h4s = list(re.finditer(r"<h4[^>]*>(.*?)</h4>", section, flags=re.S | re.I))
        subs: List[Dict[str, Any]] = []
        if h4s:
            for h4_index, h4 in enumerate(h4s):
                sub_label = label_from_html(h4.group(1))
                h4_end = h4s[h4_index + 1].start() if h4_index + 1 < len(h4s) else len(section)
                effects = [e for e in (taxonomy_effect(line) for line in section[h4.end():h4_end].splitlines()) if e]
                if not effects:
                    continue
                if "transpersonal" in norm_key(sub_label):
                    categories.append({"slug": "transpersonal", "label": "Transpersonal effects",
                                       "subcategories": [{"slug": "general", "label": sub_label, "effects": dedupe(effects)}]})
                else:
                    subs.append({"slug": slugify(sub_label), "label": sub_label, "effects": dedupe(effects)})
        else:
            effects = [e for e in (taxonomy_effect(line) for line in section.splitlines()) if e]
            if effects:
                subs.append({"slug": "general", "label": "General", "effects": dedupe(effects)})
        if subs:
            categories.append({"slug": category, "label": label, "subcategories": subs})

    merged: Dict[str, Dict[str, Any]] = {}
    for category in categories:
        current = merged.setdefault(category["slug"], {"slug": category["slug"], "label": category["label"], "subcategories": []})
        for sub in category["subcategories"]:
            existing = next((s for s in current["subcategories"] if s["slug"] == sub["slug"]), None)
            if existing:
                existing["effects"] = dedupe(existing["effects"] + sub["effects"])
            else:
                current["subcategories"].append(sub)
    ordered = sorted(merged.values(), key=lambda c: (CATEGORY_ORDER.index(c["slug"]) if c["slug"] in CATEGORY_ORDER else 99, c["slug"]))
    for category in ordered:
        for sub in category["subcategories"]:
            if sub["slug"] == "geometry" and not any(e["target"].casefold() == "geometry" and not e["anchor"] for e in sub["effects"]):
                sub["effects"].insert(0, {"name": "Geometry", "target": "Geometry", "anchor": None, "label": "Geometry"})

    index: Dict[str, Dict[str, Any]] = {}
    for category in ordered:
        for sub in category["subcategories"]:
            for effect in sub["effects"]:
                entry = {"name": effect["name"], "category": category["slug"], "subcategory": sub["slug"],
                         "target": effect["target"], "anchor": effect["anchor"]}
                for key in {effect["target"], effect["name"], effect["label"]}:
                    index.setdefault(norm_key(key), entry)
    total = sum(len(sub["effects"]) for category in ordered for sub in category["subcategories"])
    return {"source": "https://psychonautwiki.org/wiki/Subjective_effect_index",
            "list_source": "https://psychonautwiki.org/wiki/List/effects",
            "effect_count": total, "categories": ordered, "index": index}


# --------------------------------------------------------------------------- #
# Substance pages
# --------------------------------------------------------------------------- #
def extract_section(text: str, title: str) -> Optional[str]:
    match = re.search(r"^==\s*" + re.escape(title) + r"\s*==\s*$(.*?)(?=^==[^=]|\Z)", text, re.M | re.S)
    return match.group(1) if match else None


def find_blocks(text: str) -> List[tuple]:
    pattern = re.compile(r"\{\{effects/([a-z_]+)\b", re.I)
    blocks, starts = [], set()
    for match in pattern.finditer(text):
        block_type = match.group(1).lower()
        if block_type == "base":
            continue
        start = match.start()
        if start in starts:
            continue
        end = match_braces(text, start)
        if end is None:
            continue
        starts.add(start)
        blocks.append((block_type, text[start:end]))
    return blocks


def strip_inner(block: str) -> str:
    pipe = block.find("|")
    inner = block[pipe + 1:-2] if pipe >= 0 and block.endswith("}}") else block
    return strip_templates(inner)


def effect_links(line: str, index: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for match in LINK_RE.finditer(line):
        parsed = parse_link(match.group(1))
        if not parsed:
            continue
        target = parsed["target"]
        explicit = target.casefold().startswith("effect::")
        if explicit:
            target = target.split("::", 1)[1].strip()
            parsed["target"] = target
        if not explicit and not (norm_key(target) in index or norm_key(parsed["label"]) in index):
            continue
        parsed["explicit"] = explicit
        out.append(parsed)
    return out


def primary_links(body: str, index: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    prefix = re.split(r"\s[-–—]\s", body, maxsplit=1)[0]
    links = effect_links(prefix, index)
    if links:
        return links
    first = LINK_RE.search(body.lstrip(" *'\""))
    return effect_links(first.group(0), index) if first else []


def parse_block(block_type: str, block: str, index: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    category = BLOCK_CATEGORY.get(block_type, "other")
    subcategory = "general"
    out = []
    for line in strip_inner(block).splitlines():
        line = line.strip()
        if not line:
            continue
        heading = HEADING_RE.match(line)
        if heading:
            subcategory = slugify(heading.group(1))
            continue
        bullet = BULLET_RE.match(line)
        if not bullet:
            continue
        links = primary_links(bullet.group(2), index)
        if not links:
            continue
        note = clean_note(note_source(bullet.group(2)))
        for link in links:
            name = link["label"] or link["target"]
            if not name or norm_key(name) in GENERIC_LABELS or name.casefold().startswith(("level ", "a ", "the ")):
                name = link["target"]
            out.append({
                "name": re.sub(r"'{2,}", "", name).strip(), "target": link["target"],
                "anchor": link["anchor"], "category": category, "subcategory": subcategory,
                "depth": len(bullet.group(1)), "note": note,
            })
    return out


def resolve_redirects(targets: Sequence[str]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for batch in chunks(sorted({t for t in targets if t}), 45):
        try:
            data = api_get({"action": "query", "format": "json", "formatversion": "2",
                            "redirects": "1", "titles": "|".join(batch)})
        except RuntimeError as error:
            print(f"  ! redirect lookup skipped: {error}", file=sys.stderr)
            continue
        for item in data.get("query", {}).get("normalized", []) or []:
            mapping[norm_key(item["from"])] = item["to"]
        for item in data.get("query", {}).get("redirects", []) or []:
            mapping[norm_key(item["from"])] = item["to"]
        time.sleep(0.2)
    return mapping


def canonicalize(substances: List[Dict[str, Any]], index: Dict[str, Dict[str, Any]]) -> None:
    redirects = resolve_redirects([e["target"] for s in substances for e in s["effects"]] +
                                 [e["name"] for s in substances for e in s["effects"]])
    for substance in substances:
        merged: Dict[str, Dict[str, Any]] = {}
        for effect in substance["effects"]:
            resolved = redirects.get(norm_key(effect["target"])) or effect["target"]
            manual = MANUAL_ALIASES.get(norm_key(effect["target"])) or MANUAL_ALIASES.get(norm_key(effect["name"]))
            if manual:
                resolved = manual
            elif re.match(r"^8[ab]\b", norm_key(effect["target"])) or re.match(r"^8[ab]\b", norm_key(effect["name"])):
                resolved = "Geometry"
            taxonomy = index.get(norm_key(resolved)) or index.get(norm_key(effect["name"])) or index.get(norm_key(effect["target"]))
            canonical = taxonomy["name"] if taxonomy else resolved
            category = effect["category"]
            key = f"{category}|{norm_key(canonical)}"
            existing = merged.get(key)
            if existing:
                if len(effect.get("note", "")) > len(existing.get("note", "")):
                    existing["note"] = effect["note"]
                continue
            merged[key] = {
                "name": canonical, "display_name": effect["name"], "target": effect["target"],
                "anchor": effect["anchor"], "category": category, "subcategory": effect["subcategory"],
                "depth": effect["depth"], "note": effect["note"], "in_sei": bool(taxonomy),
                "sei_category": taxonomy["category"] if taxonomy else None,
                "sei_subcategory": taxonomy["subcategory"] if taxonomy else None,
            }
        substance["effects"] = sorted(merged.values(), key=lambda e: (
            CATEGORY_ORDER.index(e["category"]) if e["category"] in CATEGORY_ORDER else 99,
            e["subcategory"], e["name"].casefold()))


def phenomenology(effects: List[Dict[str, Any]]) -> Dict[str, Any]:
    evidence: Dict[str, List[str]] = {}
    for tag, needles in PHENOMENOLOGY_RULES.items():
        matches = [e["name"] for e in effects if any(n == norm_key(e["name"]) or n in norm_key(e["name"]) for n in needles)]
        if matches:
            evidence[tag] = sorted(set(matches))
    if not evidence:
        return {"tags": [], "primary_tags": [], "strength": {}, "evidence": {},
                "method": "归一化效应名匹配；无视觉/知觉相关效应命中"}
    maximum = max(len(v) for v in evidence.values())
    strength = {tag: round(len(v) / maximum, 2) for tag, v in evidence.items()}
    for tag, hallmarks in HALLMARKS.items():
        if tag in evidence and any(any(h in norm_key(name) for h in hallmarks) for name in evidence[tag]):
            strength[tag] = max(strength[tag], HALLMARK_BOOST)
    primary = sorted(evidence, key=lambda t: (-strength[t], -len(evidence[t]), list(PHENOMENOLOGY_RULES).index(t)))[:3]
    return {"tags": [t for t in PHENOMENOLOGY_RULES if t in evidence], "primary_tags": primary,
            "strength": strength, "evidence": {t: v[:8] for t, v in evidence.items()},
            "method": "按效应名归一到 5 类现象学标签；strength 为相对命中数并对标志性效应加成（非临床强度）"}


def summary(text: str) -> str:
    intro = strip_wikitext(re.split(r"^==[^=]", text, maxsplit=1, flags=re.M)[0])
    paragraphs = [p.strip() for p in intro.split("\n\n") if p.strip()]
    return shorten(paragraphs[0], 760) if paragraphs else ""


def parse_substance(page: Dict[str, Any], index: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    title = page["title"]
    curated = CURATED.get(title, {"id": slugify(title), "name": title, "group": "other", "family": "unknown", "aliases": []})
    text = page["content"]
    section = extract_section(text, "Subjective effects")
    if not section:
        print(f"  ! {title}: no Subjective effects section", file=sys.stderr)
        return None
    effects = []
    for block_type, block in find_blocks(section):
        effects.extend(parse_block(block_type, block, index))
    if not effects:
        return None
    psycho = sorted(set(re.findall(r"\[\[psychoactive class::([^\]\|]+)\]\]", text, re.I)))
    chemical = sorted(set(re.findall(r"\[\[chemical class::([^\]\|]+)\]\]", text, re.I)))
    return {
        "id": curated["id"], "title": title, "name": curated["name"], "aliases": curated["aliases"],
        "group": curated["group"], "family": curated["family"],
        "psychoactive_class": psycho, "chemical_class": chemical,
        "summary": summary(text), "effects": effects,
        "source": {"url": page["url"], "pageid": page.get("pageid"), "revid": page.get("revid"),
                   "timestamp": page.get("timestamp"), "license": "CC BY-SA 4.0"},
    }


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #
def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def taxonomy_markdown(taxonomy: Dict[str, Any]) -> str:
    lines = ["# PsychonautWiki 主观效应分类树 (SEI)", "",
             "来源：[Subjective effect index](https://psychonautwiki.org/wiki/Subjective_effect_index) / "
             "[List/effects](https://psychonautwiki.org/wiki/List/effects)。", "",
             "> 效应名称为社区整理的主观报告术语，不是临床诊断标准。", ""]
    for category in taxonomy["categories"]:
        lines += [f"## {category['label']} (`{category['slug']}`)", ""]
        for sub in category["subcategories"]:
            lines += [f"### {sub['label']} (`{sub['slug']}`)", ""]
            lines += [f"- {e['name']}" for e in sub["effects"]]
            lines.append("")
    lines.append(f"共 {taxonomy['effect_count']} 个条目。")
    return "\n".join(lines) + "\n"


def substance_markdown(substances: List[Dict[str, Any]], meta: Dict[str, Any]) -> str:
    lines = ["# PsychonautWiki 物质 × 主观效应参考集", "",
             f"生成时间：{meta['generated_at']}　|　来源：{meta['source']}　|　许可：{meta['license']}", "",
             "> **说明**：以下为使用者主观报告与社区整理，属于轶事性资料，不是临床结论，不构成用药建议。",
             "", "## 总览", "",
             "| 物质 | 组别 | 化学家族 | 效应数 | 视觉效应 | 主现象学标签 |",
             "| --- | --- | --- | ---: | ---: | --- |"]
    for sub in substances:
        counts = sub["effect_counts"]
        tags = ", ".join(sub["phenomenology"]["primary_tags"]) or "—"
        lines.append(f"| [{sub['name']}](#{sub['id']}) | {sub['group']} | {sub['family']} | "
                     f"{counts.get('total', 0)} | {counts.get('visual', 0)} | {tags} |")
    lines.append("")
    for sub in substances:
        lines += [f'<a id="{sub["id"]}"></a>', "", f"## {sub['name']}", "",
                  f"`{sub['id']}`　·　组别：**{sub['group']}**　·　化学家族：**{sub['family']}**", ""]
        if sub["summary"]:
            lines += [sub["summary"], ""]
        if sub["aliases"]:
            lines += ["别名：" + "、".join(sub["aliases"]), ""]
        if sub["phenomenology"]["tags"]:
            lines += ["现象学标签：" + "、".join(f"`{t}`" for t in sub["phenomenology"]["tags"]), ""]
        for category in CATEGORY_ORDER:
            effects = [e for e in sub["effects"] if e["category"] == category]
            if not effects:
                continue
            lines += [f"### {CATEGORY_LABELS.get(category, category)} (`{category}`)", ""]
            for effect in effects:
                note = f" — {effect['note']}" if effect["note"] else ""
                sei = "" if effect["in_sei"] else " `未收录于 SEI`"
                lines.append(f"- **{effect['name']}**{sei}{note}")
            lines.append("")
        lines += [f"来源：[{sub['title']}]({sub['source']['url']})　修订：`{sub['source']['revid']}`　"
                  f"时间：{sub['source']['timestamp']}", "", "---", ""]
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build PsychonautWiki effect reference set")
    parser.add_argument("--titles", nargs="*", default=None)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--skip-taxonomy", action="store_true")
    args = parser.parse_args(argv)

    output = Path(args.output_dir).resolve()
    titles = args.titles or DEFAULT_TITLES
    print(f"Output: {output}\nSubstances: {len(titles)}")

    taxonomy_path = output / "effect_taxonomy.json"
    if args.skip_taxonomy and taxonomy_path.is_file():
        taxonomy = json.loads(taxonomy_path.read_text(encoding="utf-8"))
        print("Reused taxonomy")
    else:
        print("Fetching List/effects ...")
        parsed = api_get({"action": "parse", "format": "json", "formatversion": "2",
                          "page": "List/effects", "prop": "wikitext"})
        taxonomy = parse_taxonomy(parsed["parse"]["wikitext"])
        print(f"  {len(taxonomy['categories'])} categories / {taxonomy['effect_count']} effects")

    print("Fetching substance pages ...")
    pages = fetch_pages(titles)
    missing = [t for t in titles if t not in pages]
    substances = []
    for title in titles:
        if title not in pages:
            continue
        print(f"  - {title} (rev {pages[title]['revid']})")
        item = parse_substance(pages[title], taxonomy["index"])
        if item:
            substances.append(item)
    if not substances:
        print("Nothing parsed.", file=sys.stderr)
        return 1

    print("Canonicalizing ...")
    canonicalize(substances, taxonomy["index"])
    for sub in substances:
        counts: Dict[str, int] = {}
        for effect in sub["effects"]:
            counts[effect["category"]] = counts.get(effect["category"], 0) + 1
        counts["total"] = len(sub["effects"])
        sub["effect_counts"] = counts
        sub["effect_count"] = len(sub["effects"])
        sub["unique_effect_count"] = len({norm_key(e["name"]) for e in sub["effects"]})
        sub["phenomenology"] = phenomenology(sub["effects"])

    group_order = ["psychedelic", "dissociative", "entactogen", "stimulant", "cannabinoid", "oneirogen", "depressant", "other"]
    substances.sort(key=lambda s: (group_order.index(s["group"]) if s["group"] in group_order else 99, s["title"]))
    meta = {
        "title": "PsychonautWiki Substance × Subjective Effect Reference Set",
        "version": "1.1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": "https://psychonautwiki.org/wiki/Subjective_effect_index",
        "source_pages": "https://psychonautwiki.org/wiki/<Substance>",
        "license": "CC BY-SA 4.0",
        "attribution": "Effect names and summaries adapted from PsychonautWiki contributors, licensed CC BY-SA 4.0.",
        "method": "MediaWiki API + wikitext parsing of Subjective effects; SEI taxonomy linking; primary-effect extraction.",
        "disclaimer": "Anecdotal subjective-effect reports; not clinical evidence or medical advice.",
        "requested_titles": list(titles), "missing_titles": missing,
        "substance_count": len(substances), "effect_count": sum(len(s["effects"]) for s in substances),
        "phenomenology_tags": list(PHENOMENOLOGY_RULES.keys()),
    }
    write_json(output / "effect_taxonomy.json", taxonomy)
    write_json(output / "substance_effects.json", {
        "meta": meta,
        "phenomenology_rules": {k: {"needles": v, "label": PHENOMENOLOGY_LABELS[k]} for k, v in PHENOMENOLOGY_RULES.items()},
        "substances": substances,
    })
    (output / "effect_taxonomy.md").write_text(taxonomy_markdown(taxonomy), encoding="utf-8")
    (output / "substance_effects.md").write_text(substance_markdown(substances, meta), encoding="utf-8")
    print(f"\nDone: {len(substances)} substances / {meta['effect_count']} effect records")
    for sub in substances:
        print(f"  {sub['name']:28s} total={sub['effect_count']:3d} visual={sub['effect_counts'].get('visual', 0):3d} "
              f"tags={','.join(sub['phenomenology']['primary_tags'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
