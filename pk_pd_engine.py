# pk_pd_engine.py
"""精神药理学 PK-PD 计算引擎。

模型概要
--------
1. 每个摄入事件先按给药途径 / 剂量 / 时间差生成一条归一化效应包络；
2. 同一物质的所有摄入事件在“标准剂量当量”浓度空间叠加（支持补量 Redosing）；
3. 叠加后的浓度通过 Hill 方程转换为 [0, 1] 的药效强度；
4. 各物质按受体权重累加得到受体检出负载，并计算跨机制协同指数；
5. 药效强度 × 现象学权重（软饱和累加）映射为 GLSL 着色器 uniform 参数。

所有返回的数值都是原生 Python float / int，保证可以直接被 JSON 序列化。
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Sequence

from pydantic import BaseModel, Field, field_validator, model_validator

from archives import SUBSTANCE_DB

# 参与负载统计的受体。未知受体（未来扩展）也会被动态累加。
RECEPTOR_KEYS = ("5HT2A", "NMDA_antag", "SERT", "D2", "DA_NE", "CB1", "KOR", "GABA")

# 现象学算子参数（0 ~ 1 归一化空间），含新增的立体主义 / 漩涡 / 碎片化。
PHENOMENOLOGY_KEYS = (
    "warp_amplitude",
    "warp_frequency",
    "symmetry_order",
    "pattern_density",
    "rgb_displacement",
    "hue_shift",
    "feedback_decay",
    "edge_reorg",
    "analog_glitch",
    "cubism",
    "vortex",
    "shatter",
)

# 摄入时间最多允许到 24 小时，与前端时间轴 / 模拟请求上限保持一致。
MAX_EVENT_TIME_MINUTES = 24 * 60.0


class IngestionEvent(BaseModel):
    """单次摄入事件。输入非法时由 FastAPI 返回 422，而不是静默忽略。"""

    id: str = Field(default="ing", min_length=1, max_length=64)
    substance_id: str
    roa: str
    dose: float = Field(gt=0.0, le=10000.0, description="剂量，单位见物质档案")
    time_minutes: float = Field(ge=0.0, le=MAX_EVENT_TIME_MINUTES, description="相对于时间轴 0 点的摄入时刻")

    @field_validator("substance_id")
    @classmethod
    def _validate_substance(cls, value: str) -> str:
        if value not in SUBSTANCE_DB:
            known = ", ".join(sorted(SUBSTANCE_DB))
            raise ValueError(f"未知物质 {value!r}，可选: {known}")
        return value

    @model_validator(mode="after")
    def _validate_roa(self) -> "IngestionEvent":
        sub = SUBSTANCE_DB[self.substance_id]
        if self.roa not in sub["roas"]:
            known = ", ".join(sub["roas"])
            raise ValueError(f"物质 {self.substance_id!r} 不支持给药途径 {self.roa!r}，可选: {known}")
        return self


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


class PKPDEngine:
    """确定性、无状态的 PK-PD 计算引擎（可被并发请求安全调用）。"""

    # ------------------------------------------------------------------ #
    # 1. 单次给药包络
    # ------------------------------------------------------------------ #
    @staticmethod
    def single_ingestion_envelope(dt: float, roa_params: Dict[str, float]) -> float:
        """计算给药后 ``dt`` 分钟的归一化效应包络，范围 [0, 1]。

        四段式：Onset 潜伏 → Comeup 平滑爬升 → Peak 平台 → Offset 指数消除。
        段与段之间在数值上连续，避免曲线出现台阶。
        """
        dt = _safe_float(dt)
        if dt <= 0.0:
            return 0.0

        onset = max(_safe_float(roa_params.get("onset")), 0.0)
        comeup = max(_safe_float(roa_params.get("comeup")), 0.1)
        peak = max(_safe_float(roa_params.get("peak")), 0.1)
        half_life = max(_safe_float(roa_params.get("half_life")), 1.0)

        t_comeup = onset + comeup
        t_peak_end = t_comeup + peak

        # 1) Onset：微弱指数萌芽 0 -> 0.08
        if dt < onset:
            ratio = dt / max(onset, 0.1)
            return _clamp(0.08 * (ratio ** 2.5), 0.0, 1.0)

        # 2) Comeup：余弦 S 型爬升 0.08 -> 1.0
        if dt < t_comeup:
            ratio = (dt - onset) / comeup
            smooth = 0.5 * (1.0 - math.cos(math.pi * _clamp(ratio, 0.0, 1.0)))
            return _clamp(0.08 + 0.92 * smooth, 0.0, 1.0)

        # 3) Peak：带轻微代谢衰减的平台 1.0 -> 0.88
        if dt < t_peak_end:
            ratio = (dt - t_comeup) / peak
            return _clamp(1.0 - 0.12 * (ratio ** 1.5), 0.0, 1.0)

        # 4) Offset：一室指数消除 + 长尾
        dt_after_peak = dt - t_peak_end
        k_elim = math.log(2.0) / max(half_life * 0.65, 1.0)
        value = 0.88 * math.exp(-k_elim * dt_after_peak)
        return value if value > 0.005 else 0.0

    # ------------------------------------------------------------------ #
    # 2. Hill 方程
    # ------------------------------------------------------------------ #
    @staticmethod
    def _hill_effect(conc: float, ec50: float, hill_n: float) -> float:
        """E = C^n / (EC50^n + C^n)，用 EC50/C 的形式避免大数溢出。"""
        conc = _safe_float(conc)
        ec50 = _safe_float(ec50)
        hill_n = max(_safe_float(hill_n, 1.0), 0.01)
        if conc <= 0.0:
            return 0.0
        if ec50 <= 0.0:
            return 1.0
        try:
            ratio = math.pow(ec50 / conc, hill_n)
        except (OverflowError, ValueError):
            return 0.0
        if not math.isfinite(ratio):
            return 0.0
        return _clamp(1.0 / (1.0 + ratio), 0.0, 1.0)

    # ------------------------------------------------------------------ #
    # 3. 当前时刻求值
    # ------------------------------------------------------------------ #
    @classmethod
    def evaluate_at_time(cls, ingestions: Sequence[IngestionEvent], t_minutes: float) -> Dict[str, Any]:
        """计算 ``t_minutes`` 时刻的浓度、药效、受体负载与着色器参数。"""
        t = _safe_float(t_minutes)
        substance_conc: Dict[str, float] = {}
        present_substances = sorted({ing.substance_id for ing in ingestions})

        for ing in ingestions:
            sub = SUBSTANCE_DB.get(ing.substance_id)
            if sub is None:  # 已由 pydantic 校验，这里仅作防御
                continue
            roa_info = sub["roas"].get(ing.roa)
            if roa_info is None:
                continue

            dt = t - _safe_float(ing.time_minutes)
            if dt <= 0.0:
                continue

            envelope = cls.single_ingestion_envelope(dt, roa_info)
            if envelope <= 0.0:
                continue

            reference_bio = _safe_float(next(iter(sub["roas"].values())).get("bioavailability"), 1.0)
            relative_bio = _safe_float(roa_info.get("bioavailability"), 1.0) / max(reference_bio, 0.05)
            effective = _safe_float(ing.dose) * relative_bio * envelope
            if effective > 0.0:
                substance_conc[ing.substance_id] = substance_conc.get(ing.substance_id, 0.0) + effective

        # ---- Hill 方程：浓度 -> 药效强度 ----
        substance_effects: Dict[str, float] = {sub_id: 0.0 for sub_id in present_substances}
        receptor_load: Dict[str, float] = {key: 0.0 for key in RECEPTOR_KEYS}

        for sub_id in sorted(substance_conc):
            sub = SUBSTANCE_DB[sub_id]
            effect = cls._hill_effect(
                substance_conc[sub_id],
                _safe_float(sub.get("ec50_dose"), 1.0),
                _safe_float(sub.get("hill_n"), 1.0),
            )
            substance_effects[sub_id] = round(effect, 4)
            if effect <= 1e-6:
                continue
            for receptor, weight in sub.get("receptors", {}).items():
                receptor_load[receptor] = receptor_load.get(receptor, 0.0) + effect * _safe_float(weight)

        # ---- 跨机制协同 ----
        load_5ht2a = receptor_load.get("5HT2A", 0.0)
        load_nmda = receptor_load.get("NMDA_antag", 0.0)
        load_sert = receptor_load.get("SERT", 0.0)
        load_cb1 = receptor_load.get("CB1", 0.0)
        load_kor = receptor_load.get("KOR", 0.0)
        load_gaba = receptor_load.get("GABA", 0.0)

        # 5-HT2A + NMDA 拮抗：空间几何解构 + 时间反馈倍增
        synergy_psy_diss = _clamp(load_5ht2a * load_nmda * 2.2, 0.0, 1.0)
        # 5-HT2A + SERT：Candyflip 式色彩 / 流体协同
        synergy_candy = _clamp(load_5ht2a * load_sert * 1.8, 0.0, 1.0)
        # 5-HT2A + CB1：几何密度与拖尾增强
        synergy_cannabis = _clamp(load_5ht2a * load_cb1 * 2.0, 0.0, 1.0)
        # KOR + (5-HT2A / NMDA)：场景切片与维度折叠
        synergy_kor = _clamp(load_kor * (load_5ht2a + load_nmda) * 2.1, 0.0, 1.0)
        total_synergy_score = round(
            max(synergy_psy_diss, synergy_candy, synergy_cannabis, synergy_kor), 3
        )

        # ---- 现象学算子：软饱和累加 1-(1-a)(1-b)，天然有界 ----
        raw_params: Dict[str, float] = {key: 0.0 for key in PHENOMENOLOGY_KEYS}
        for sub_id, effect in substance_effects.items():
            if effect <= 1e-6:
                continue
            weights = SUBSTANCE_DB[sub_id].get("phenomenology_weights", {})
            for key in raw_params:
                contribution = _clamp(effect * _safe_float(weights.get(key)), 0.0, 1.0)
                raw_params[key] = 1.0 - (1.0 - raw_params[key]) * (1.0 - contribution)

        # 协同项只增益、不削减
        if synergy_psy_diss > 0.05:
            raw_params["edge_reorg"] = min(1.0, raw_params["edge_reorg"] + synergy_psy_diss * 0.35)
            raw_params["feedback_decay"] = min(1.0, raw_params["feedback_decay"] + synergy_psy_diss * 0.25)
            raw_params["pattern_density"] = min(1.0, raw_params["pattern_density"] + synergy_psy_diss * 0.25)
            raw_params["analog_glitch"] = min(1.0, raw_params["analog_glitch"] + synergy_psy_diss * 0.30)
            # 经典致幻 + 解离：多视点空间碎裂
            raw_params["cubism"] = min(1.0, raw_params["cubism"] + synergy_psy_diss * 0.30)
            raw_params["shatter"] = min(1.0, raw_params["shatter"] + synergy_psy_diss * 0.28)
            raw_params["vortex"] = min(1.0, raw_params["vortex"] + synergy_psy_diss * 0.15)

        if synergy_candy > 0.05:
            raw_params["hue_shift"] = min(1.0, raw_params["hue_shift"] + synergy_candy * 0.30)
            raw_params["warp_amplitude"] = min(1.0, raw_params["warp_amplitude"] + synergy_candy * 0.20)
            raw_params["rgb_displacement"] = min(1.0, raw_params["rgb_displacement"] + synergy_candy * 0.25)
            raw_params["vortex"] = min(1.0, raw_params["vortex"] + synergy_candy * 0.18)

        if synergy_cannabis > 0.05:
            raw_params["pattern_density"] = min(1.0, raw_params["pattern_density"] + synergy_cannabis * 0.30)
            raw_params["warp_amplitude"] = min(1.0, raw_params["warp_amplitude"] + synergy_cannabis * 0.25)
            raw_params["feedback_decay"] = min(1.0, raw_params["feedback_decay"] + synergy_cannabis * 0.20)
            raw_params["cubism"] = min(1.0, raw_params["cubism"] + synergy_cannabis * 0.12)
            raw_params["shatter"] = min(1.0, raw_params["shatter"] + synergy_cannabis * 0.10)

        if synergy_kor > 0.05:
            raw_params["cubism"] = min(1.0, raw_params["cubism"] + synergy_kor * 0.35)
            raw_params["shatter"] = min(1.0, raw_params["shatter"] + synergy_kor * 0.30)
            raw_params["vortex"] = min(1.0, raw_params["vortex"] + synergy_kor * 0.22)

        # KOR / 解离特异性的场景切片与复视重影
        scenery_slice = _clamp(load_kor * 0.90 + synergy_psy_diss * 0.35, 0.0, 1.0)
        diplopia_offset = _clamp(load_nmda * 0.65 + load_gaba * 0.70, 0.0, 1.0)

        # ---- 映射到 GLSL uniform 取值域 ----
        if raw_params["symmetry_order"] > 0.08:
            symmetry_order = int(round((2.0 + raw_params["symmetry_order"] * 14.0) / 2.0) * 2)
            symmetry_order = max(2, min(16, symmetry_order))
        else:
            symmetry_order = 1

        shader_uniforms: Dict[str, Any] = {
            "warp_amplitude": round(_clamp(raw_params["warp_amplitude"], 0.0, 1.0), 3),
            "warp_frequency": round(_clamp(1.0 + raw_params["warp_frequency"] * 6.0, 1.0, 8.0), 2),
            "symmetry_order": symmetry_order,
            "pattern_density": round(_clamp(raw_params["pattern_density"], 0.0, 1.0), 3),
            "rgb_displacement": round(_clamp(raw_params["rgb_displacement"], 0.0, 1.0), 3),
            "hue_shift": round(_clamp(raw_params["hue_shift"], 0.0, 1.0), 3),
            "feedback_decay": round(min(0.95, _clamp(raw_params["feedback_decay"], 0.0, 1.0) * 0.95), 3),
            "edge_reorg": round(_clamp(raw_params["edge_reorg"], 0.0, 1.0), 3),
            "analog_glitch": round(_clamp(raw_params["analog_glitch"], 0.0, 1.0), 3),
            "cubism": round(_clamp(raw_params["cubism"], 0.0, 1.0), 3),
            "vortex": round(_clamp(raw_params["vortex"], 0.0, 1.0), 3),
            "shatter": round(_clamp(raw_params["shatter"], 0.0, 1.0), 3),
            "scenery_slice": round(scenery_slice, 3),
            "diplopia_offset": round(diplopia_offset, 3),
            "synergy_index": total_synergy_score,
        }

        return {
            "time_minutes": round(t, 1),
            "substance_effects": substance_effects,
            "receptor_load": {key: round(max(0.0, value), 3) for key, value in receptor_load.items()},
            "synergy_index": total_synergy_score,
            "shader_uniforms": shader_uniforms,
        }

    # ------------------------------------------------------------------ #
    # 4. 时间轴采样
    # ------------------------------------------------------------------ #
    @classmethod
    def simulate_timeline_series(
        cls,
        ingestions: Sequence[IngestionEvent],
        duration_minutes: float = 600.0,
        step_minutes: float = 5.0,
    ) -> Dict[str, Any]:
        """生成整条时间轴的效应曲线，供前端绘制 Journal 风格图表。"""
        duration = _clamp(_safe_float(duration_minutes, 600.0), 60.0, 1440.0)
        step = _clamp(_safe_float(step_minutes, 5.0), 1.0, 60.0)
        count = int(duration // step)
        timestamps = [round(index * step, 6) for index in range(count + 1)]
        if timestamps[-1] < duration - 1e-6:
            timestamps.append(round(duration, 6))

        active_sub_ids = sorted({ing.substance_id for ing in ingestions})
        curves: Dict[str, List[float]] = {sub_id: [] for sub_id in active_sub_ids}
        synergy_curve: List[float] = []

        for timestamp in timestamps:
            result = cls.evaluate_at_time(ingestions, timestamp)
            effects = result["substance_effects"]
            for sub_id in active_sub_ids:
                curves[sub_id].append(float(effects.get(sub_id, 0.0)))
            synergy_curve.append(float(result["synergy_index"]))

        return {
            "timestamps": timestamps,
            "curves": curves,
            "synergy_curve": synergy_curve,
            "duration_minutes": duration,
            "step_minutes": step,
        }
