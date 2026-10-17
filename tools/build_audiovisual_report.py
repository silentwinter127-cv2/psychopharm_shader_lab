#!/usr/bin/env python
"""Generate a human-readable audiovisual profile table from the PW reference set."""
from __future__ import annotations

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from audio_profiles import AUDIO_LABELS, AUDIO_PROFILES  # noqa: E402

OUT = PROJECT_DIR / "references" / "audiovisual_profiles.md"


def bar(value: float) -> str:
    filled = round(max(0.0, min(1.0, value)) * 10)
    return "█" * filled + "·" * (10 - filled)


def main() -> int:
    rows = sorted(AUDIO_PROFILES.values(), key=lambda p: (p.get("group") or "", p.get("name") or ""))
    lines = [
        "# 物质 × 视听效应画像",
        "",
        "本表把 PsychonautWiki 参考集中的**视觉 / 听觉 / 多感官效应**整理为可比较的画像。",
        "音频分数是效应名到 Web Audio 参数的**启发式映射**（0–1），不是心理声学测量，",
        "也不能预测个人实际听到什么。",
        "",
        "## 音效维度",
        "",
        "| 维度 | 含义 |",
        "| --- | --- |",
    ]
    for key, label in AUDIO_LABELS.items():
        lines.append(f"| `{key}` | {label} |")
    lines += [
        "",
        "## 总览",
        "",
        "| 物质 | 组别 | 视觉效应 | 听觉效应 | 联觉 | 主要听觉效应 | 音频画像 |",
        "| --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for profile in rows:
        scores = profile["scores"]
        top = sorted(
            ((key, scores[key]) for key in ("clarity", "suppression", "distortion", "hallucination",
                                            "tinnitus", "synaesthesia", "time_warp", "dissociation",
                                            "arousal", "sedation")),
            key=lambda item: item[1],
            reverse=True,
        )[:3]
        top_text = " / ".join(f"{AUDIO_LABELS[key]} {value:.2f}" for key, value in top if value > 0) or "—"
        auditory = ", ".join(profile.get("auditory_effects", [])[:4]) or "—"
        syn = "是" if profile.get("synaesthesia_effects") else "—"
        lines.append(
            f"| {profile.get('name')} (`{profile['id']}`) | {profile.get('group')} | "
            f"{profile.get('visual_effect_count', 0)} | {profile.get('auditory_effect_count', 0)} | "
            f"{syn} | {auditory} | {top_text} |"
        )

    lines += ["", "## 逐物质明细", ""]
    for profile in rows:
        lines += [
            f"### {profile.get('name')} (`{profile['id']}`)",
            "",
            f"- 组别：{profile.get('group')}　化学家族：{profile.get('family')}",
            f"- 听觉效应：{', '.join(profile.get('auditory_effects', [])) or '—'}",
            f"- 联觉 / 多感官：{', '.join(profile.get('synaesthesia_effects', [])) or '—'}",
        ]
        for key in ("clarity", "suppression", "distortion", "hallucination", "tinnitus",
                    "synaesthesia", "time_warp", "dissociation", "arousal", "sedation", "intensity"):
            value = profile["scores"].get(key, 0.0)
            lines.append(f"  - `{key}` {bar(value)} {value:.2f} — {AUDIO_LABELS[key]}")
        if profile.get("fallback"):
            lines.append("  - *参考集无 LSA 页面，使用 LSD 画像 ×0.8 作为回退。*")
        lines.append("")

    lines += [
        "---",
        "",
        "来源：PsychonautWiki（CC BY-SA 4.0），效应名为使用者主观报告与社区整理。",
        "本表仅用于艺术 / 研究模拟，不构成医疗或用药建议。",
        "",
    ]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT} ({len(rows)} profiles)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
