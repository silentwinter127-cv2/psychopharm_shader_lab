#!/usr/bin/env python
"""项目自检脚本（无需额外测试框架）。

用法：
    python selftest.py

覆盖内容：
* 单次给药包络的边界 / 连续性 / 衰减
* Hill 方程的数值稳定性
* 全部物质 × 全部给药途径 × 多个时间点的取值范围
* 补量叠加与跨机制协同
* 时间轴采样长度与数值有效性
* FastAPI 路由、静态资源、参数校验（422）与 JSON 序列化
* 从任意工作目录启动时静态目录仍然可用
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))

from fastapi.testclient import TestClient  # noqa: E402

from app import APP_VERSION, app  # noqa: E402
from archives import SUBSTANCE_DB  # noqa: E402
from audio_profiles import AUDIO_PROFILES, compute_audio_uniforms  # noqa: E402
from pk_pd_engine import IngestionEvent, PKPDEngine  # noqa: E402
from reference_library import (  # noqa: E402
    ALLOWED_TAGS,
    EFFECT_TAXONOMY,
    REFERENCE_META,
    SUBSTANCE_REFERENCES,
    get_reference,
    list_reference_summaries,
    reference_available,
)

PASSED: list[str] = []
FAILED: list[tuple[str, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSED.append(name)
        print(f"  [PASS] {name}")
    else:
        FAILED.append((name, detail))
        print(f"  [FAIL] {name}  {detail}")


def finite(value: float) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def state_issues(state: dict) -> list[str]:
    """返回状态对象中所有越界/缺失项；空列表表示完全合法。"""
    issues: list[str] = []
    effects = state.get("substance_effects")
    if not isinstance(effects, dict):
        issues.append("缺少 substance_effects")
        return issues
    for sub_id, effect in effects.items():
        if not (finite(effect) and 0.0 <= effect <= 1.0):
            issues.append(f"{sub_id} 效应={effect!r}")

    receptors = state.get("receptor_load")
    if not isinstance(receptors, dict) or not {"5HT2A", "NMDA_antag", "SERT", "D2"} <= set(receptors):
        issues.append("受体负载字段不完整")
    else:
        for key, value in receptors.items():
            if not (finite(value) and value >= 0.0):
                issues.append(f"受体 {key}={value!r}")

    synergy = state.get("synergy_index")
    if not (finite(synergy) and 0.0 <= synergy <= 1.0):
        issues.append(f"协同={synergy!r}")

    uniforms = state.get("shader_uniforms", {})
    expected = {
        "warp_amplitude", "warp_frequency", "symmetry_order", "pattern_density",
        "rgb_displacement", "hue_shift", "feedback_decay", "edge_reorg",
        "analog_glitch", "scenery_slice", "diplopia_offset",
        "cubism", "vortex", "shatter", "synergy_index",
    }
    if not expected <= set(uniforms):
        issues.append(f"uniform 缺失: {sorted(expected - set(uniforms))}")
        return issues
    for key in expected - {"symmetry_order"}:
        if not finite(uniforms[key]):
            issues.append(f"{key}={uniforms[key]!r}")
    for key in ("warp_amplitude", "pattern_density", "rgb_displacement", "hue_shift",
                "edge_reorg", "analog_glitch", "scenery_slice", "diplopia_offset",
                "cubism", "vortex", "shatter"):
        if not 0.0 <= uniforms[key] <= 1.0:
            issues.append(f"{key}={uniforms[key]!r} 越界")
    if not 0.0 <= uniforms["feedback_decay"] <= 0.95:
        issues.append(f"feedback_decay={uniforms['feedback_decay']!r}")
    if not 1.0 <= uniforms["warp_frequency"] <= 8.0:
        issues.append(f"warp_frequency={uniforms['warp_frequency']!r}")
    symmetry = uniforms["symmetry_order"]
    if not (isinstance(symmetry, int) and 1 <= symmetry <= 16 and (symmetry == 1 or symmetry % 2 == 0)):
        issues.append(f"symmetry_order={symmetry!r}")
    if state.get("time_minutes") is None:
        issues.append("缺少 time_minutes")
    return issues


def section(title: str) -> None:
    print(f"\n== {title} ==")


def main() -> int:
    print(f"Psychopharmacological Art Shader Lab · selftest (app version {APP_VERSION})")
    print(f"项目目录: {PROJECT_DIR}")

    # ------------------------------------------------------------------ #
    section("1. 单次给药包络")
    sample_times = (0.0, 0.5, 5.0, 30.0, 60.0, 120.0, 240.0, 480.0, 720.0, 1440.0)
    for sub_id, sub in SUBSTANCE_DB.items():
        for roa_key, roa in sub["roas"].items():
            label = f"{sub_id}/{roa_key}"
            values = [PKPDEngine.single_ingestion_envelope(dt, roa) for dt in sample_times]
            check(
                f"{label}: 包络在所有采样点有限且落在 [0,1]",
                all(finite(v) and 0.0 <= v <= 1.0 for v in values),
                str(values),
            )
            check(f"{label}: dt=0 时为 0", values[0] == 0.0, str(values[0]))

            t_comeup = roa["onset"] + roa["comeup"]
            t_peak_end = t_comeup + roa["peak"]
            continuity_failures = []
            for boundary in (roa["onset"], t_comeup, t_peak_end):
                if boundary <= 0.5:
                    continue
                before = PKPDEngine.single_ingestion_envelope(boundary - 1e-3, roa)
                after = PKPDEngine.single_ingestion_envelope(boundary + 1e-3, roa)
                if abs(before - after) >= 0.02:
                    continuity_failures.append(f"{boundary:g}m: {before:.4f}->{after:.4f}")
            check(f"{label}: 段边界连续", not continuity_failures, "; ".join(continuity_failures))

            peak_time = t_comeup + max(roa["peak"] * 0.2, 0.2)
            peak_value = PKPDEngine.single_ingestion_envelope(peak_time, roa)
            check(f"{label}: 峰值接近 1", peak_value > 0.85, f"{peak_value:.3f} @ {peak_time:.1f}m")
            tail_value = PKPDEngine.single_ingestion_envelope(t_peak_end + 20000.0, roa)
            check(f"{label}: 长尾趋近 0", tail_value < 0.01, str(tail_value))

    # ------------------------------------------------------------------ #
    section("2. Hill 方程数值稳定性")
    check("conc=0 -> effect=0", PKPDEngine._hill_effect(0.0, 100.0, 2.0) == 0.0)
    check("conc=EC50 -> effect=0.5", abs(PKPDEngine._hill_effect(100.0, 100.0, 2.0) - 0.5) < 1e-9)
    check("极小浓度 -> 接近 0", PKPDEngine._hill_effect(1e-12, 100.0, 2.0) < 1e-9)
    check("极大浓度 -> 接近 1", PKPDEngine._hill_effect(1e12, 100.0, 2.0) > 0.999)
    check("ec50=0 -> 1", PKPDEngine._hill_effect(1.0, 0.0, 2.0) == 1.0)
    check("NaN 输入安全", finite(PKPDEngine._hill_effect(float("nan"), 100.0, 2.0)))

    # ------------------------------------------------------------------ #
    section("3. 全物质 × 全 ROA × 时间点")
    for sub_id, sub in SUBSTANCE_DB.items():
        for roa_key in sub["roas"]:
            event = IngestionEvent(
                id="self_1",
                substance_id=sub_id,
                roa=roa_key,
                dose=sub["standard_dose"],
                time_minutes=0.0,
            )
            issues: list[str] = []
            for t in (0.0, 5.0, 30.0, 60.0, 120.0, 240.0, 480.0, 720.0, 1440.0):
                issues.extend(f"T{t:g}: {issue}" for issue in state_issues(PKPDEngine.evaluate_at_time([event], t)))
            check(f"{sub_id}/{roa_key}: 9 个时间点状态合法", not issues, "; ".join(issues[:4]))

    missing_new_weights = [
        sub_id for sub_id, sub in SUBSTANCE_DB.items()
        if not {"cubism", "vortex", "shatter"} <= set(sub.get("phenomenology_weights", {}))
    ]
    check("25 种物质均包含立体主义/漩涡/碎片化权重", not missing_new_weights, str(missing_new_weights[:5]))
    invalid_new_weights = [
        (sub_id, key, value)
        for sub_id, sub in SUBSTANCE_DB.items()
        for key, value in sub.get("phenomenology_weights", {}).items()
        if key in {"cubism", "vortex", "shatter"} and not (0.0 <= float(value) <= 1.0)
    ]
    check("新增算子权重均在 [0,1]", not invalid_new_weights, str(invalid_new_weights[:5]))

    # ------------------------------------------------------------------ #
    section("4. 补量叠加与协同")
    single = IngestionEvent(id="a", substance_id="lsd_25", roa="sublingual", dose=100.0, time_minutes=0.0)
    redose_late = IngestionEvent(id="b", substance_id="lsd_25", roa="sublingual", dose=50.0, time_minutes=60.0)
    redose_now = IngestionEvent(id="c", substance_id="lsd_25", roa="sublingual", dose=50.0, time_minutes=0.0)

    effect_single = PKPDEngine.evaluate_at_time([single], 120.0)["substance_effects"]["lsd_25"]
    effect_redose = PKPDEngine.evaluate_at_time([single, redose_late], 120.0)["substance_effects"]["lsd_25"]
    effect_split = PKPDEngine.evaluate_at_time([redose_now, redose_late], 120.0)["substance_effects"]["lsd_25"]
    check("补量后效应提高", effect_redose > effect_single, f"{effect_single} -> {effect_redose}")
    check("等效总剂量下 100@0 强于 50@0+50@60", effect_single > effect_split, f"{effect_single} vs {effect_split}")

    lsd_only = PKPDEngine.evaluate_at_time([single], 210.0)
    check("LSD 单药无协同", lsd_only["synergy_index"] == 0.0, str(lsd_only["synergy_index"]))

    lsd_k = [
        IngestionEvent(id="l", substance_id="lsd_25", roa="sublingual", dose=150.0, time_minutes=0.0),
        IngestionEvent(id="k", substance_id="ketamine", roa="insufflated", dose=50.0, time_minutes=150.0),
    ]
    state_lsd_k = PKPDEngine.evaluate_at_time(lsd_k, 210.0)
    check("LSD + Ketamine 产生 5HT2A/NMDA 协同", state_lsd_k["synergy_index"] > 0.2, str(state_lsd_k["synergy_index"]))
    check("协同提高 edge_reorg", state_lsd_k["shader_uniforms"]["edge_reorg"] > 0.4, str(state_lsd_k["shader_uniforms"]["edge_reorg"]))
    check("协同提高 analog_glitch", state_lsd_k["shader_uniforms"]["analog_glitch"] > 0.3, str(state_lsd_k["shader_uniforms"]["analog_glitch"]))

    candy = [
        IngestionEvent(id="l2", substance_id="lsd_25", roa="sublingual", dose=100.0, time_minutes=0.0),
        IngestionEvent(id="m", substance_id="mdma", roa="oral", dose=120.0, time_minutes=60.0),
    ]
    state_candy = PKPDEngine.evaluate_at_time(candy, 150.0)
    check("LSD + MDMA 产生 Candyflip 协同", state_candy["synergy_index"] > 0.05, str(state_candy["synergy_index"]))

    # ------------------------------------------------------------------ #
    section("5. 时间轴采样")
    timeline = PKPDEngine.simulate_timeline_series(lsd_k, duration_minutes=600.0, step_minutes=5.0)
    timestamps = timeline["timestamps"]
    check("时间轴为 121 个点", len(timestamps) == 121, str(len(timestamps)))
    check("时间轴从 0 开始", timestamps[0] == 0.0, str(timestamps[0]))
    check("时间轴在 600 结束", timestamps[-1] == 600.0, str(timestamps[-1]))
    check("时间轴单调递增", all(b > a for a, b in zip(timestamps, timestamps[1:])))
    check("曲线数量与物质数量一致", set(timeline["curves"]) == {"lsd_25", "ketamine"}, str(set(timeline["curves"])))
    for sub_id, curve in timeline["curves"].items():
        check(
            f"曲线 {sub_id} 长度一致且数值有效",
            len(curve) == len(timestamps) and all(finite(v) and 0.0 <= v <= 1.0 for v in curve),
            f"len={len(curve)}",
        )
    check(
        "协同曲线长度一致且数值有效",
        len(timeline["synergy_curve"]) == len(timestamps)
        and all(finite(v) and 0.0 <= v <= 1.0 for v in timeline["synergy_curve"]),
    )
    check("非整步长时间轴包含结束点", PKPDEngine.simulate_timeline_series(lsd_k, 610.0, 7.0)["timestamps"][-1] == 610.0)

    # ------------------------------------------------------------------ #
    section("6. FastAPI 路由与校验")
    client = TestClient(app)

    response = client.get("/api/health")
    check("GET /api/health 返回 200", response.status_code == 200, response.text[:200])
    health = response.json()
    check("health 状态为 ok", health.get("status") == "ok")
    check("health 中静态目录存在", Path(health.get("static_dir", "")).is_dir(), str(health.get("static_dir")))

    response = client.get("/api/metadata")
    check("GET /api/metadata 返回 200", response.status_code == 200, response.text[:200])
    metadata = response.json()
    check("物质数量为 25", len(metadata.get("substances", {})) == 25, str(len(metadata.get("substances", {}))))
    check("档案数量为 8", len(metadata.get("archives", [])) == 8, str(len(metadata.get("archives", []))))
    archive_ids = {item.get("id") for item in metadata.get("archives", [])}
    check(
        "包含立体主义 / 漩涡 / 碎片化档案",
        {"cubist_recomposition", "vortex_tunnel", "voronoi_shatter"} <= archive_ids,
        str(sorted(archive_ids)),
    )

    response = client.get("/")
    check("GET / 返回 200", response.status_code == 200)
    check("GET / 返回 HTML 页面", "Psychopharmacological Art Shader Lab" in response.text)
    check("首页禁止缓存", "no-store" in response.headers.get("cache-control", ""))

    response = client.get("/static/index.html")
    check("GET /static/index.html 返回 200", response.status_code == 200)
    response = client.get("/static/vendor/tailwindcss-3.4.17.js")
    check(
        "本地 Tailwind 资源可访问",
        response.status_code == 200 and len(response.content) > 100000,
        str(len(response.content)),
    )

    payload = {
        "ingestions": [
            {"id": "i1", "substance_id": "lsd_25", "roa": "sublingual", "dose": 120, "time_minutes": 0},
            {"id": "i2", "substance_id": "ketamine", "roa": "insufflated", "dose": 45, "time_minutes": 150},
        ],
        "current_time_minutes": 165,
        "timeline_duration_minutes": 600,
    }
    response = client.post("/api/simulate", json=payload)
    check("POST /api/simulate 返回 200", response.status_code == 200, response.text[:500])
    data = response.json()
    check("响应包含 current_state / timeline / version", {"current_state", "timeline", "version"} <= set(data))
    check("响应版本号正确", data.get("version") == APP_VERSION, str(data.get("version")))
    issues = state_issues(data["current_state"])
    check("API 状态合法", not issues, "; ".join(issues[:4]))
    check("API 时间轴为 121 点", len(data["timeline"]["timestamps"]) == 121)
    try:
        json.dumps(data)
        check("响应可 JSON 序列化", True)
    except (TypeError, ValueError) as error:
        check("响应可 JSON 序列化", False, str(error))

    empty = client.post("/api/simulate", json={"ingestions": [], "current_time_minutes": 0, "timeline_duration_minutes": 600})
    check("空摄入记录返回 200", empty.status_code == 200, empty.text[:200])
    empty_data = empty.json()
    check("空摄入记录无曲线", empty_data["timeline"]["curves"] == {})
    check("空摄入记录状态合法", not state_issues(empty_data["current_state"]), "; ".join(state_issues(empty_data["current_state"])))

    invalid_cases = [
        ("未知物质", {**payload, "ingestions": [{"id": "x", "substance_id": "heroin", "roa": "oral", "dose": 10, "time_minutes": 0}]}),
        ("未知 ROA", {**payload, "ingestions": [{"id": "x", "substance_id": "lsd_25", "roa": "vaporized", "dose": 10, "time_minutes": 0}]}),
        ("负剂量", {**payload, "ingestions": [{"id": "x", "substance_id": "lsd_25", "roa": "oral", "dose": -1, "time_minutes": 0}]}),
        ("负时间", {**payload, "ingestions": [{"id": "x", "substance_id": "lsd_25", "roa": "oral", "dose": 10, "time_minutes": -1}]}),
        ("时间轴过长", {**payload, "timeline_duration_minutes": 99999}),
        ("时间轴过短", {**payload, "timeline_duration_minutes": 10}),
        ("当前时间越界", {**payload, "current_time_minutes": 99999}),
        ("摄入事件过多", {**payload, "ingestions": [payload["ingestions"][0]] * 65}),
    ]
    for label, body in invalid_cases:
        response = client.post("/api/simulate", json=body)
        check(f"非法输入被拒绝：{label}", response.status_code == 422, f"{response.status_code} {response.text[:120]}")

    # ------------------------------------------------------------------ #
    section("7. 从任意工作目录导入/启动")
    with tempfile.TemporaryDirectory() as temp_dir:
        code = (
            "import sys; "
            f"sys.path.insert(0, {str(PROJECT_DIR)!r}); "
            "from app import app, STATIC_DIR; "
            "assert STATIC_DIR.is_dir(); "
            "print('cwd-independent-ok')"
        )
        completed = subprocess.run(
            [sys.executable, "-c", code],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        check(
            "从其他工作目录导入 app 成功",
            completed.returncode == 0 and "cwd-independent-ok" in completed.stdout,
            (completed.stdout + completed.stderr)[:300],
        )

    # ------------------------------------------------------------------ #
    section("8. PsychonautWiki 效应参考集")
    check("参考集已加载", reference_available())
    check("参考集物质数量为 25", len(SUBSTANCE_REFERENCES) == 25, str(len(SUBSTANCE_REFERENCES)))
    check("参考集许可证为 CC BY-SA 4.0", "CC BY-SA 4.0" in str(REFERENCE_META.get("license", "")), str(REFERENCE_META.get("license")))
    check("参考集来源为 PsychonautWiki", "psychonautwiki.org" in str(REFERENCE_META.get("source", "")))
    check("参考集生成时间存在", bool(REFERENCE_META.get("generated_at")), str(REFERENCE_META.get("generated_at")))

    reference_ids = [item.get("id") for item in SUBSTANCE_REFERENCES]
    check("参考集 id 唯一", len(reference_ids) == len(set(reference_ids)), str(len(reference_ids) - len(set(reference_ids))))
    check("参考集总效应数 >= 1500", int(REFERENCE_META.get("effect_count", 0)) >= 1500, str(REFERENCE_META.get("effect_count")))

    reference_issues: list[str] = []
    for item in SUBSTANCE_REFERENCES:
        label = item.get("id", "?")
        if not item.get("name") or not item.get("group") or not item.get("family"):
            reference_issues.append(f"{label}: 缺少 name/group/family")
        if not isinstance(item.get("effects"), list) or not item["effects"]:
            reference_issues.append(f"{label}: effects 为空")
            continue
        for effect in item["effects"]:
            if not effect.get("name"):
                reference_issues.append(f"{label}: 空效应名")
            if effect.get("category") not in {
                "visual", "cognitive", "physical", "auditory", "multisensory",
                "transpersonal", "disconnective", "tactile", "smell_taste", "aftereffects", "other",
            }:
                reference_issues.append(f"{label}: 未知分类 {effect.get('category')!r}")
        source = item.get("source") or {}
        if not source.get("url") or not source.get("revid"):
            reference_issues.append(f"{label}: 缺少来源/修订号")
        phenomenology = item.get("phenomenology") or {}
        if not set(phenomenology.get("tags", [])) <= set(ALLOWED_TAGS):
            reference_issues.append(f"{label}: 非法现象学标签")
        if not set(phenomenology.get("primary_tags", [])) <= set(phenomenology.get("tags", [])):
            reference_issues.append(f"{label}: primary_tags 不在 tags 中")
        for tag, value in (phenomenology.get("strength") or {}).items():
            if tag not in ALLOWED_TAGS or not (0.0 <= float(value) <= 1.0):
                reference_issues.append(f"{label}: 强度值非法 {tag}={value!r}")
    check("参考集所有条目结构合法", not reference_issues, "; ".join(reference_issues[:5]))

    check("效应分类树存在", bool(EFFECT_TAXONOMY.get("categories")))
    check("效应分类树包含 9 个类别", len(EFFECT_TAXONOMY.get("categories", [])) == 9, str(len(EFFECT_TAXONOMY.get("categories", []))))
    check("效应分类树条目数 >= 200", int(EFFECT_TAXONOMY.get("effect_count", 0)) >= 200, str(EFFECT_TAXONOMY.get("effect_count")))
    check("LSD 档案可检索", get_reference("lsd") is not None)
    check("参考集摘要数量一致", len(list_reference_summaries()) == len(SUBSTANCE_REFERENCES))

    response = client.get("/api/references")
    check("GET /api/references 返回 200", response.status_code == 200, response.text[:200])
    reference_payload = response.json()
    check("参考集 API 标记 available", reference_payload.get("available") is True)
    check("参考集 API 返回 25 个摘要", len(reference_payload.get("substances", [])) == 25, str(len(reference_payload.get("substances", []))))
    check("摘要不含完整 effects", "effects" not in (reference_payload.get("substances") or [{}])[0])

    response = client.get("/api/references/lsd")
    check("GET /api/references/lsd 返回 200", response.status_code == 200, response.text[:200])
    if response.status_code == 200:
        lsd_reference = response.json()
        check("LSD 档案包含效应列表", len(lsd_reference.get("effects", [])) > 20, str(len(lsd_reference.get("effects", []))))
        check("LSD 档案包含现象学标签", bool(lsd_reference.get("phenomenology", {}).get("primary_tags")))

    response = client.get("/api/references/not-a-substance")
    check("未知参考档案返回 404", response.status_code == 404, str(response.status_code))
    response = client.get("/api/reference-taxonomy")
    check("GET /api/reference-taxonomy 返回 200", response.status_code == 200)
    if response.status_code == 200:
        check("分类树 API 返回类别", len(response.json().get("categories", [])) == 9)

    # ------------------------------------------------------------------ #
    section("9. 视听画像与声音模拟")
    check("音频画像覆盖 25 种物质", len(AUDIO_PROFILES) == 25, str(len(AUDIO_PROFILES)))
    dxm_profile = AUDIO_PROFILES.get("dxm")
    check("DXM 音频画像存在", dxm_profile is not None)
    if dxm_profile:
        check("DXM 解离音效 >= 0.9", dxm_profile["scores"].get("dissociation", 0) >= 0.9, str(dxm_profile["scores"]))
        check("DXM 听觉效应为 4 条", dxm_profile.get("auditory_effect_count") == 4, str(dxm_profile.get("auditory_effect_count")))
        check("DXM 具备联觉耦合", dxm_profile["scores"].get("synaesthesia", 0) > 0, str(dxm_profile["scores"]))
    invalid_audio = [
        (sid, key, value)
        for sid, profile in AUDIO_PROFILES.items()
        for key, value in profile.get("scores", {}).items()
        if not (0.0 <= float(value) <= 1.0)
    ]
    check("音频画像分数均在 [0,1]", not invalid_audio, str(invalid_audio[:5]))

    mixed_audio = compute_audio_uniforms({"lsd_25": 0.5, "ketamine": 0.2})
    check("混合音频状态为 active", mixed_audio.get("active") is True)
    check("混合音频包含两个来源", len(mixed_audio.get("sources", [])) == 2, str(mixed_audio.get("sources")))
    check("混合音频具有清晰度", mixed_audio.get("clarity", 0) > 0)
    check("混合音频具有解离成分", mixed_audio.get("dissociation", 0) > 0.1, str(mixed_audio.get("dissociation")))
    check("混合音频具有联觉成分", mixed_audio.get("synaesthesia", 0) > 0.1, str(mixed_audio.get("synaesthesia")))

    response = client.get("/api/audio-profiles")
    check("GET /api/audio-profiles 返回 200", response.status_code == 200, response.text[:200])
    if response.status_code == 200:
        audio_payload = response.json()
        check("音频 API 返回 25 个画像", audio_payload.get("count") == 25, str(audio_payload.get("count")))

    response = client.get("/api/references/dxm")
    check("GET /api/references/dxm 返回 200", response.status_code == 200, response.text[:200])
    if response.status_code == 200:
        dxm_reference = response.json()
        check("DXM 参考档案包含听觉画像", bool(dxm_reference.get("audio_profile")))
        check("DXM 参考档案保留听觉效应", any(e.get("category") == "auditory" for e in dxm_reference.get("effects", [])))

    response = client.post("/api/simulate", json=payload)
    check("仿真响应包含 audio_uniforms", response.status_code == 200 and "audio_uniforms" in response.json().get("current_state", {}))
    if response.status_code == 200:
        audio_state = response.json()["current_state"]["audio_uniforms"]
        check("仿真音频状态为 active", audio_state.get("active") is True)
        check("仿真音频包含来源列表", len(audio_state.get("sources", [])) >= 1)

    # ------------------------------------------------------------------ #
    print("\n" + "=" * 62)
    print(f"通过 {len(PASSED)} 项，失败 {len(FAILED)} 项")
    if FAILED:
        print("\n失败明细：")
        for name, detail in FAILED:
            print(f"  - {name}  {detail}")
        return 1
    print("全部自检通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
