# archives.py
from typing import Dict, Any, List

# 1. 五大现象学算子研究档案 (结合截图中的 SEI 映射标注)
PHENOMENON_ARCHIVES: List[Dict[str, Any]] = [
    {
        "id": "pattern_formation",
        "phenomenon": "01 · 几何化与图案生成 (Pattern Formation)",
        "sei_mapped": ["几何 (Geometry)", "对称纹理重复 (Symmetrical texture repetition)", "分形递归 (Fractal recursion)"],
        "evidence": "Bressloff et al. (2001) V1 Euclidean symmetry model; PsychonautWiki SEI Visual Geometry.",
        "mechanism_notes": "初级视皮层 (V1) 5-HT2A 受体激动或 κ-阿片/NMDA 调制引发皮层柱侧向抑制去同步，产生自发图灵几何晶格与万花筒极坐标折叠。",
        "shader_stack": ["Polar Coordinate Fold (极坐标折叠)", "Iterated Domain Symmetry (迭代对称)", "Fractal Mandala Overlay"],
        "parameter_ranges": {"symmetry_order": [1, 16], "pattern_density": [0.0, 1.0]},
        "confidence": "高（计算神经科学 V1 图灵斑图模型成熟）",
        "limitations": "仅对 2D 视口执行拓扑对称折叠，无法完全复现三维闭眼几何空间 (CEV) 的内省沉浸感。"
    },
    {
        "id": "spatial_warping",
        "phenomenon": "02 · 空间扭曲与流动 (Spatial Warping)",
        "sei_mapped": ["漂移 (Drifting/Morphing/Breathing)", "透视扭曲 (Perspective distortion)", "场景切片 (Scenery slicing)"],
        "evidence": "Carhart-Harris & Friston (2019) REBUS Model; PsychonautWiki Drifting & Scenery Slicing.",
        "mechanism_notes": "高层知觉先验 (Top-down priors) 权重松弛，局部运动检测器与空间连续性约束解耦，引发流体呼吸变形或 κ-阿片受体特征性的“场景切片/拉链式翻转”。",
        "shader_stack": ["Simplex Flow Field", "Iterative Domain Warping", "Kappa-Style Scenery Slicing Shear"],
        "parameter_ranges": {"warp_amplitude": [0.0, 1.0], "warp_frequency": [1.0, 8.0], "scenery_slice": [0.0, 1.0]},
        "confidence": "中-高（连续流体噪声场与分段剪切算子结合）",
        "limitations": "不含语义物体分割，扭曲均匀作用于全场与局部纹理梯度。"
    },
    {
        "id": "chromatic_distortion",
        "phenomenon": "03 · 色彩分离与光谱异常 (Chromatic Distortion)",
        "sei_mapped": ["色彩增强 (Colour enhancement)", "色相偏移 (Colour shifting)", "衍射 (Diffraction)"],
        "evidence": "Hartman & Hollister (1963); PsychonautWiki Colour Shifting & Diffraction.",
        "mechanism_notes": "外侧膝状体 (LGN) 与 V4 色觉区增益改变，伴随瞳孔散大 (Mydriasis) 及眼动微震颤导致的边缘光谱衍射与色相周期漂移。",
        "shader_stack": ["Radial RGB Chromatic Dispersion", "HSV Hue Field Rotation", "Local Saturation & Luminance Gain"],
        "parameter_ranges": {"rgb_displacement": [0.0, 1.0], "hue_shift": [0.0, 1.0]},
        "confidence": "中等",
        "limitations": "受限于标准 sRGB 色域，无法呈现超色域主观色彩。"
    },
    {
        "id": "temporal_persistence",
        "phenomenon": "04 · 视觉残留与时间叠影 (Temporal Persistence)",
        "sei_mapped": ["拖影 (Tracers)", "残影 (After images)", "复视 (Double vision)"],
        "evidence": "Dubois & VanRullen (2011) Visual Trails quantification; PsychonautWiki Tracers & Double Vision.",
        "mechanism_notes": "皮层-丘脑节律改变导致视觉时间整合窗口拉长；NMDA 或 GABA 调制引发帧率抽离感与眼外肌协调减弱导致的双重视像 (Diplopia)。",
        "shader_stack": ["Ping-Pong Framebuffer Feedback", "Diplopia Stereo Offset (复视双影位移)", "Chromatic Trail Decay"],
        "parameter_ranges": {"feedback_decay": [0.0, 0.96], "diplopia_offset": [0.0, 1.0]},
        "confidence": "高（帧间缓冲直接对应时间衰减常数）",
        "limitations": "静态图片输入下需配合微流动或交互运动方可体现长拖尾。"
    },
    {
        "id": "perceptual_reorganization",
        "phenomenon": "05 · 空间与物体边界异常 (Perceptual Reorganization)",
        "sei_mapped": ["视觉解离 (Visual disconnection)", "深度失真 (Depth distortion)", "自我消融 (Ego dissolution)"],
        "evidence": "Dalgarno (2007); PsychonautWiki Visual Disconnection & Acuity Suppression/Enhancement.",
        "mechanism_notes": "NMDA 拮抗、GABA 抑制或高剂量 5-HT2A/KOR 激活导致图形-背景分离失效、深度线索扁平化或敏锐度极端化。",
        "shader_stack": ["Spatial Block/Voronoi Quantization", "Sobel Edge Deconstruction", "Vignette Tunnel & Depth Flattening"],
        "parameter_ranges": {"edge_reorg": [0.0, 1.0], "analog_glitch": [0.0, 1.0]},
        "confidence": "艺术化概念转译",
        "limitations": "“自我消融”等超个人知觉属于高维认知体验，视觉上仅以边界瓦解与拓扑消融隐喻表达。"
    },
    {
        "id": "cubist_recomposition",
        "phenomenon": "06 · 空间立体主义 (Cubist Recomposition)",
        "sei_mapped": ["环境立体主义 (Environmental cubism)", "场景切片 (Scenery slicing)", "视角扭曲 (Perspective distortion)"],
        "evidence": "PsychonautWiki Environmental Cubism / Scenery Slicing reports; 立体主义 (Braque, Picasso) 的多视点并置视觉语言.",
        "mechanism_notes": "背侧视觉通路对局部视角与全局透视的整合被削弱，同一场景的多个视点片段不再收敛为单一透视；预测编码先验松弛使面片化的空间关系同时进入意识。",
        "shader_stack": ["Facet Grid Decomposition (面片网格分解)", "Per-Facet Viewpoint Offset (逐面片视点偏移)", "Planar Colour Quantization (平面色彩量化)"],
        "parameter_ranges": {"cubism": [0.0, 1.0], "facet_density": [0.0, 1.0], "viewpoint_jitter": [0.0, 1.0]},
        "confidence": "探索性艺术转译（基于 PW 环境立体主义报告与立体主义视觉语言）",
        "limitations": "二维屏幕空间无法真正还原多视点深度；面片网格是几何近似，不等同于真实空间知觉。"
    },
    {
        "id": "vortex_tunnel",
        "phenomenon": "07 · 漩涡与时空隧道 (Vortex Tunnel)",
        "sei_mapped": ["几何递归 (Recursion)", "视觉解离 (Visual disconnection)", "空间迷失 (Spatial disorientation)"],
        "evidence": "PsychonautWiki Geometry / Recursion / Visual Disconnection reports; 光流 (optic flow) 与隧道错觉 (tunnel illusion) 研究.",
        "mechanism_notes": "径向光流与中心-外周运动整合被放大，形成朝向消失点的螺旋或隧道；视觉—前庭信号冲突可能贡献旋转与吸入感。",
        "shader_stack": ["Log-Polar Twist (对数极坐标扭转)", "Radial Zoom/Pinch (径向缩放)", "Angular Domain Warp (角域扭曲)"],
        "parameter_ranges": {"vortex": [0.0, 1.0], "vortex_twist": [0.0, 1.0], "vortex_zoom": [0.0, 1.0]},
        "confidence": "中等（基于光流/隧道错觉的艺术化近似）",
        "limitations": "不模拟前庭信号或真实自我运动；静态图像上呈现的是几何旋涡，而非真正的向心运动。"
    },
    {
        "id": "voronoi_shatter",
        "phenomenon": "08 · 碎片化与晶格断裂 (Voronoi Shatter)",
        "sei_mapped": ["视觉解离 (Visual disconnection)", "纹理液化 (Texture liquidation)", "不可言说的恐惧 (Unspeakable horrors)"],
        "evidence": "PsychonautWiki Visual Disconnection / Texture Liquidation / Unspeakable Horrors reports; Worley/Voronoi 细胞噪声.",
        "mechanism_notes": "局部边界与表面连续性整合失败，场景被分割为不连续的碎片或晶格；V1/V2 边缘检测与区域填充的时序失配产生裂隙感。",
        "shader_stack": ["Worley/Voronoi Cell Decomposition (细胞分解)", "Per-Shard UV Displacement (逐碎片位移)", "Crack Edge Glow (裂隙边缘发光)"],
        "parameter_ranges": {"shatter": [0.0, 1.0], "shard_density": [0.0, 1.0], "crack_glow": [0.0, 1.0]},
        "confidence": "探索性艺术转译（碎片化是解离报告的几何隐喻）",
        "limitations": "碎片网格是程序化近似；无法表达解离体验中的自我边界消失与概念性空间断裂。"
    }
]


# 2. 25种精神活性物质完整药代动力学(PK)与药效学(PD)数据库
def _make_substance(
    sub_id: str, name: str, group: str, chem_class: str,
    unit: str, std_dose: float, ec50: float, hill_n: float,
    roas: Dict[str, Dict[str, Any]],
    weights: Dict[str, float],
    receptors: Dict[str, float],
    revision_id: int,
    pw_url: str,
    effects_by_cat: Dict[str, List[Dict[str, str]]]
) -> Dict[str, Any]:
    flat_effects = []
    op_counts = {k: 0 for k in [
        "pattern_formation", "spatial_warping", "chromatic_distortion",
        "temporal_persistence", "perceptual_reorganization"
    ]}
    for cat_id, eff_list in effects_by_cat.items():
        for e in eff_list:
            op = e.get("operator")
            if op in op_counts:
                op_counts[op] += 1
            flat_effects.append({
                "name": e["name"],
                "zh_name": e["zh_name"],
                "category": cat_id,
                "operator": op,
                "description": e["desc"]
            })

    return {
        "id": sub_id,
        "name": name,
        "group": group,
        "class": chem_class,
        "unit": unit,
        "standard_dose": std_dose,
        "ec50_dose": ec50,
        "hill_n": hill_n,
        "roas": roas,
        "phenomenology_weights": weights,
        "receptors": receptors,
        "metadata": {
            "pw_revision_id": revision_id,
            "fetched_at": "2026-10-17T00:00:00Z",
            "source_url": pw_url,
            "license": "CC BY-SA 4.0"
        },
        "operator_mapping_counts": op_counts,
        "effect_count": len(flat_effects),
        "effects": flat_effects
    }


# 构建 25 种代表物质的完整数据（涵盖截图中的 7 大组别）
SUBSTANCE_DB: Dict[str, Dict[str, Any]] = {
    # ==================== 1. 经典致幻剂 (11种) ====================
    "lsd_25": _make_substance(
        "lsd_25", "LSD (麦角酸二乙酰胺)", "经典致幻剂", "Lysergamide (5-HT2A/D2 Agonist)",
        "μg", 100.0, 110.0, 1.6,
        {
            "sublingual": {"name": "舌下 (Sublingual)", "bioavailability": 0.85, "onset": 30, "comeup": 60, "peak": 210, "offset": 300, "half_life": 175},
            "oral": {"name": "口服 (Oral)", "bioavailability": 0.75, "onset": 45, "comeup": 75, "peak": 210, "offset": 320, "half_life": 180}
        },
        {"warp_amplitude": 0.78, "warp_frequency": 0.60, "symmetry_order": 0.85, "pattern_density": 0.82, "rgb_displacement": 0.55, "hue_shift": 0.75, "feedback_decay": 0.72, "edge_reorg": 0.40, "analog_glitch": 0.22},
        {"5HT2A": 0.95, "D2": 0.45},
        179420, "https://psychonautwiki.org/wiki/LSD",
        {
            "visual": [
                {"name": "Geometry", "zh_name": "视觉几何 (Level 8A/8B)", "operator": "pattern_formation", "desc": "复杂锐利的分形晶格、万花筒递归与算法风格几何图案。"},
                {"name": "Drifting", "zh_name": "视觉漂移与呼吸", "operator": "spatial_warping", "desc": "物体表面纹理呈现连续流体的呼吸、融化与形变。"},
                {"name": "Colour shifting", "zh_name": "色相动态偏移", "operator": "chromatic_distortion", "desc": "视野中的色相环发生周期性流动与虹彩衍射。"},
                {"name": "Tracers", "zh_name": "拖影与运动残迹", "operator": "temporal_persistence", "desc": "移动物体后方留下长条彩虹色或半透明残影。"}
            ],
            "cognitive": [
                {"name": "Analysis enhancement", "zh_name": "分析能力增强与概念联想", "operator": None, "desc": "跨领域发散性思维与高维内省逻辑加速。"}
            ],
            "transpersonal": [
                {"name": "Ego dissolution", "zh_name": "自我边界消融", "operator": "perceptual_reorganization", "desc": "主体与外部环境边界弱化，产生万物一体感。"}
            ]
        }
    ),
    "psilocybin_mushrooms": _make_substance(
        "psilocybin_mushrooms", "Psilocybin mushrooms (裸盖菇素)", "经典致幻剂", "Tryptamine (5-HT2A/1A Agonist)",
        "mg", 20.0, 22.0, 1.5,
        {"oral": {"name": "口服 (Oral)", "bioavailability": 0.55, "onset": 25, "comeup": 45, "peak": 120, "offset": 150, "half_life": 110}},
        {"warp_amplitude": 0.92, "warp_frequency": 0.35, "symmetry_order": 0.68, "pattern_density": 0.72, "rgb_displacement": 0.42, "hue_shift": 0.85, "feedback_decay": 0.58, "edge_reorg": 0.42, "analog_glitch": 0.15},
        {"5HT2A": 0.90},
        178910, "https://psychonautwiki.org/wiki/Psilocybin_mushrooms",
        {
            "visual": [
                {"name": "Morphing", "zh_name": "有机形态流体变形", "operator": "spatial_warping", "desc": "自然且充满生命感的低频波浪扭曲与植物藤蔓式生长感。"},
                {"name": "Symmetrical texture repetition", "zh_name": "对称纹理铺展", "operator": "pattern_formation", "desc": "草地、木纹、地毯表面自动重组为多重对称图腾。"},
                {"name": "Colour enhancement", "zh_name": "色彩极端饱和", "operator": "chromatic_distortion", "desc": "自然色彩发光度与色温显著提升。"}
            ],
            "multisensory": [
                {"name": "Synaesthesia", "zh_name": "联觉 (视听通感)", "operator": "chromatic_distortion", "desc": "声音韵律直接调制视觉几何的色彩与脉动。"}
            ]
        }
    ),
    "mescaline": _make_substance(
        "mescaline", "Mescaline (麦司卡林)", "经典致幻剂", "Phenethylamine (5-HT2A/2C Agonist)",
        "mg", 300.0, 330.0, 1.5,
        {"oral": {"name": "口服 (Oral)", "bioavailability": 0.80, "onset": 60, "comeup": 120, "peak": 240, "offset": 360, "half_life": 360}},
        {"warp_amplitude": 0.65, "warp_frequency": 0.45, "symmetry_order": 0.82, "pattern_density": 0.78, "rgb_displacement": 0.60, "hue_shift": 0.92, "feedback_decay": 0.65, "edge_reorg": 0.35, "analog_glitch": 0.18},
        {"5HT2A": 0.85, "DA_NE": 0.25},
        176512, "https://psychonautwiki.org/wiki/Mescaline",
        {
            "visual": [
                {"name": "Colour enhancement", "zh_name": "霓虹宝石色增强", "operator": "chromatic_distortion", "desc": "极具油画与彩绘玻璃质感的鲜明色彩提升。"},
                {"name": "Geometry", "zh_name": "阿兹特克/马赛克几何", "operator": "pattern_formation", "desc": "高度结构化、温暖对称的镶嵌式几何阵列。"}
            ]
        }
    ),
    "2c_b": _make_substance(
        "2c_b", "2C-B", "经典致幻剂", "Substituted Phenethylamine (5-HT2C/2A Partial Agonist)",
        "mg", 20.0, 22.0, 1.7,
        {
            "oral": {"name": "口服 (Oral)", "bioavailability": 0.75, "onset": 45, "comeup": 60, "peak": 120, "offset": 120, "half_life": 95},
            "insufflated": {"name": "鼻腔给药 (Insufflated)", "bioavailability": 0.90, "onset": 5, "comeup": 15, "peak": 75, "offset": 90, "half_life": 70}
        },
        {"warp_amplitude": 0.68, "warp_frequency": 0.55, "symmetry_order": 0.72, "pattern_density": 0.70, "rgb_displacement": 0.75, "hue_shift": 0.88, "feedback_decay": 0.68, "edge_reorg": 0.25, "analog_glitch": 0.25},
        {"5HT2A": 0.75, "SERT": 0.30},
        178201, "https://psychonautwiki.org/wiki/2C-B",
        {
            "visual": [
                {"name": "Colour shifting", "zh_name": "霓虹电光色相流转", "operator": "chromatic_distortion", "desc": "品红、青色与电光紫主导的快速光谱迁移与边缘辉光。"},
                {"name": "Tracers", "zh_name": "频闪光轨拖尾", "operator": "temporal_persistence", "desc": "清晰的冷暖对比运动光轨。"}
            ],
            "tactile": [
                {"name": "Tactile enhancement", "zh_name": "触觉放大与温热感", "operator": None, "desc": "皮肤触感与共情体表感知增强。"}
            ]
        }
    ),
    "2c_e": _make_substance(
        "2c_e", "2C-E", "经典致幻剂", "Substituted Phenethylamine (5-HT2A Agonist)",
        "mg", 15.0, 16.0, 1.8,
        {"oral": {"name": "口服 (Oral)", "bioavailability": 0.80, "onset": 45, "comeup": 75, "peak": 180, "offset": 240, "half_life": 150}},
        {"warp_amplitude": 0.82, "warp_frequency": 0.75, "symmetry_order": 0.88, "pattern_density": 0.86, "rgb_displacement": 0.65, "hue_shift": 0.68, "feedback_decay": 0.78, "edge_reorg": 0.60, "analog_glitch": 0.42},
        {"5HT2A": 0.92},
        175330, "https://psychonautwiki.org/wiki/2C-E",
        {
            "visual": [
                {"name": "Geometry", "zh_name": "高密度递归几何", "operator": "pattern_formation", "desc": "极具机械与数学严密感的多尺度分形结构。"},
                {"name": "Scenery slicing", "zh_name": "视野断层切片", "operator": "spatial_warping", "desc": "空间平面发生断层式错位与高频波纹扭曲。"}
            ],
            "multisensory": [
                {"name": "Synaesthesia", "zh_name": "强烈多感官通感", "operator": "perceptual_reorganization", "desc": "感官通道交叉重组。"}
            ]
        }
    ),
    "dmt": _make_substance(
        "dmt", "DMT (N,N-二甲基色胺)", "经典致幻剂", "Tryptamine (5-HT2A / Sigma-1 Agonist)",
        "mg", 30.0, 32.0, 2.2,
        {"vaporized": {"name": "气化吸入 (Vaporized)", "bioavailability": 0.90, "onset": 0.5, "comeup": 1.5, "peak": 6, "offset": 12, "half_life": 8}},
        {"warp_amplitude": 0.88, "warp_frequency": 0.95, "symmetry_order": 1.00, "pattern_density": 0.98, "rgb_displacement": 0.85, "hue_shift": 0.95, "feedback_decay": 0.70, "edge_reorg": 0.85, "analog_glitch": 0.62},
        {"5HT2A": 1.00},
        179880, "https://psychonautwiki.org/wiki/DMT",
        {
            "visual": [
                {"name": "Geometry", "zh_name": "超维菊花/穹顶分形 (Level 8A)", "operator": "pattern_formation", "desc": "全视野被极高频、超对称旋转几何穹顶完全接管。"},
                {"name": "Visual disconnection", "zh_name": "突破性外源空间替代", "operator": "perceptual_reorganization", "desc": "现实视网膜输入被高维非欧几何空间彻底解构替换。"}
            ]
        }
    ),
    "al_lad": _make_substance(
        "al_lad", "AL-LAD", "经典致幻剂", "Lysergamide (5-HT2A Agonist)",
        "μg", 150.0, 160.0, 1.6,
        {"sublingual": {"name": "舌下 (Sublingual)", "bioavailability": 0.85, "onset": 30, "comeup": 50, "peak": 160, "offset": 210, "half_life": 140}},
        {"warp_amplitude": 0.75, "warp_frequency": 0.62, "symmetry_order": 0.88, "pattern_density": 0.85, "rgb_displacement": 0.65, "hue_shift": 0.88, "feedback_decay": 0.68, "edge_reorg": 0.25, "analog_glitch": 0.18},
        {"5HT2A": 0.92, "D2": 0.30},
        174120, "https://psychonautwiki.org/wiki/AL-LAD",
        {
            "visual": [
                {"name": "Geometry", "zh_name": "高彩度华丽万花筒", "operator": "pattern_formation", "desc": "视觉几何比 LSD 更密集、色彩更绚丽，而认知负荷相对温和。"},
                {"name": "Diffraction", "zh_name": "光谱衍射光晕", "operator": "chromatic_distortion", "desc": "高光边缘呈现丝绸般的彩虹衍射环。"}
            ]
        }
    ),
    "lsa": _make_substance(
        "lsa", "LSA (麦角酸酰胺)", "经典致幻剂", "Lysergamide (5-HT2A/1A/D2 Partial Agonist)",
        "μg", 500.0, 550.0, 1.4,
        {"oral": {"name": "口服 (Oral)", "bioavailability": 0.65, "onset": 45, "comeup": 90, "peak": 180, "offset": 240, "half_life": 160}},
        {"warp_amplitude": 0.52, "warp_frequency": 0.30, "symmetry_order": 0.50, "pattern_density": 0.48, "rgb_displacement": 0.35, "hue_shift": 0.45, "feedback_decay": 0.65, "edge_reorg": 0.45, "analog_glitch": 0.28},
        {"5HT2A": 0.60, "D2": 0.35, "GABA": 0.20},
        173290, "https://psychonautwiki.org/wiki/LSA",
        {
            "visual": [
                {"name": "Visual haze", "zh_name": "梦幻视觉柔焦与残影", "operator": "temporal_persistence", "desc": "带有镇静梦幻质感的轻微几何与时间叠影。"}
            ],
            "physical": [
                {"name": "Sedation", "zh_name": "躯体沉重与镇静", "operator": None, "desc": "明显的半梦半醒躯体放松与沉重感。"}
            ]
        }
    ),
    "dom": _make_substance(
        "dom", "DOM (STP)", "经典致幻剂", "Substituted Amphetamine (5-HT2A/2C Agonist)",
        "mg", 5.0, 5.5, 1.7,
        {"oral": {"name": "口服 (Oral)", "bioavailability": 0.85, "onset": 90, "comeup": 120, "peak": 420, "offset": 480, "half_life": 420}},
        {"warp_amplitude": 0.76, "warp_frequency": 0.70, "symmetry_order": 0.84, "pattern_density": 0.80, "rgb_displacement": 0.68, "hue_shift": 0.72, "feedback_decay": 0.75, "edge_reorg": 0.52, "analog_glitch": 0.45},
        {"5HT2A": 0.90, "DA_NE": 0.55},
        172800, "https://psychonautwiki.org/wiki/DOM",
        {
            "visual": [
                {"name": "Geometry", "zh_name": "超长效锐利电光几何", "operator": "pattern_formation", "desc": "持续十余小时的锐利金属质感几何与高频震颤。"},
                {"name": "Frame rate suppression", "zh_name": "频闪帧率抑制", "operator": "temporal_persistence", "desc": "运动画面呈现胶片频闪与长残迹。"}
            ]
        }
    ),
    "ibogaine": _make_substance(
        "ibogaine", "Ibogaine (伊博格碱)", "经典致幻剂", "Iboga Alkaloid (5-HT2A / KOR / NMDA / Sigma-2 Polypharmacology)",
        "mg", 400.0, 450.0, 1.6,
        {"oral": {"name": "口服 (Oral)", "bioavailability": 0.70, "onset": 60, "comeup": 120, "peak": 480, "offset": 720, "half_life": 540}},
        {"warp_amplitude": 0.62, "warp_frequency": 0.40, "symmetry_order": 0.55, "pattern_density": 0.65, "rgb_displacement": 0.58, "hue_shift": 0.45, "feedback_decay": 0.88, "edge_reorg": 0.82, "analog_glitch": 0.70},
        {"5HT2A": 0.55, "NMDA_antag": 0.60, "KOR": 0.65},
        171950, "https://psychonautwiki.org/wiki/Ibogaine",
        {
            "visual": [
                {"name": "Internal hallucination", "zh_name": "电影胶片式记忆回放", "operator": "perceptual_reorganization", "desc": "被称为清醒梦境 (Oneirogenic) 的自传体记忆场景投射与长拖尾。"},
                {"name": "Tracers", "zh_name": "重度视觉拖影", "operator": "temporal_persistence", "desc": "极长衰减周期的帧间光迹残留。"}
            ]
        }
    ),
    "ayahuasca": _make_substance(
        "ayahuasca", "Ayahuasca (死藤水: DMT + MAOI)", "经典致幻剂", "Tryptamine + Harmala Alkaloid (5-HT2A + MAO-A Inhibition)",
        "mg", 50.0, 55.0, 1.6,
        {"oral": {"name": "口服煎剂 (Oral Brew)", "bioavailability": 0.75, "onset": 35, "comeup": 55, "peak": 150, "offset": 180, "half_life": 135}},
        {"warp_amplitude": 0.90, "warp_frequency": 0.65, "symmetry_order": 0.92, "pattern_density": 0.90, "rgb_displacement": 0.62, "hue_shift": 0.88, "feedback_decay": 0.76, "edge_reorg": 0.72, "analog_glitch": 0.38},
        {"5HT2A": 0.95, "SERT": 0.25},
        179110, "https://psychonautwiki.org/wiki/Ayahuasca",
        {
            "visual": [
                {"name": "Geometry", "zh_name": "蛇纹/藤蔓神圣几何", "operator": "pattern_formation", "desc": "浓郁的亚马逊图腾几何、对称视觉编织与有机空间流动。"},
                {"name": "Perspective distortion", "zh_name": "深邃空间透视重塑", "operator": "spatial_warping", "desc": "空间纵深发生强烈伸缩与流体脉动。"}
            ],
            "transpersonal": [
                {"name": "Internal hallucination", "zh_name": "叙事性内源异象", "operator": "perceptual_reorganization", "desc": "高维符号化与生命母题视觉重组。"}
            ]
        }
    ),

    # ==================== 2. 解离剂 (5种) ====================
    "ketamine": _make_substance(
        "ketamine", "Ketamine (氯胺酮)", "解离剂", "Arylcyclohexylamine (NMDA Antagonist)",
        "mg", 60.0, 75.0, 1.8,
        {
            "insufflated": {"name": "鼻腔给药 (Insufflated)", "bioavailability": 0.50, "onset": 5, "comeup": 15, "peak": 35, "offset": 55, "half_life": 45},
            "oral": {"name": "口服 (Oral)", "bioavailability": 0.20, "onset": 20, "comeup": 30, "peak": 60, "offset": 90, "half_life": 70}
        },
        {"warp_amplitude": 0.38, "warp_frequency": 0.20, "symmetry_order": 0.15, "pattern_density": 0.22, "rgb_displacement": 0.68, "hue_shift": 0.18, "feedback_decay": 0.85, "edge_reorg": 0.95, "analog_glitch": 0.75},
        {"NMDA_antag": 0.95},
        179600, "https://psychonautwiki.org/wiki/Ketamine",
        {
            "dissociative": [
                {"name": "Visual disconnection", "zh_name": "视觉解离与孔洞空间 (K-Hole)", "operator": "perceptual_reorganization", "desc": "外部视觉输入抽离，坠入宏观滑移的无边界抽象深渊。"}
            ],
            "visual": [
                {"name": "Double vision", "zh_name": "复视与立体视觉分离", "operator": "temporal_persistence", "desc": "双目视轴解耦导致画面出现水平/对角重影。"},
                {"name": "Depth perception distortions", "zh_name": "深度与尺度极化失真 (爱丽丝梦游仙境综合征)", "operator": "perceptual_reorganization", "desc": "房间与物体显得极其遥远巨大或扁平微缩。"}
            ]
        }
    ),
    "mxe": _make_substance(
        "mxe", "MXE (甲氧氯胺酮)", "解离剂", "Arylcyclohexylamine (NMDA Antagonist + SERT Inhibitor)",
        "mg", 40.0, 45.0, 1.8,
        {"sublingual": {"name": "舌下 (Sublingual)", "bioavailability": 0.70, "onset": 15, "comeup": 40, "peak": 120, "offset": 150, "half_life": 120}},
        {"warp_amplitude": 0.52, "warp_frequency": 0.28, "symmetry_order": 0.35, "pattern_density": 0.42, "rgb_displacement": 0.65, "hue_shift": 0.48, "feedback_decay": 0.86, "edge_reorg": 0.92, "analog_glitch": 0.68},
        {"NMDA_antag": 0.92, "SERT": 0.45},
        176890, "https://psychonautwiki.org/wiki/MXE",
        {
            "dissociative": [
                {"name": "Hole spaces and voids", "zh_name": "温暖流体孔洞空间 (M-Hole)", "operator": "perceptual_reorganization", "desc": "兼具血清素温暖色泽与深度三维空间重构的解离状态。"}
            ],
            "visual": [
                {"name": "Perspective distortion", "zh_name": "非欧空间尺度滑移", "operator": "spatial_warping", "desc": "平稳滑行的传送带式空间变形。"}
            ]
        }
    ),
    "pcp": _make_substance(
        "pcp", "PCP (苯环利定)", "解离剂", "Arylcyclohexylamine (NMDA Antagonist + D2/DAT Modulator)",
        "mg", 5.0, 6.0, 1.9,
        {"insufflated": {"name": "鼻腔给药 (Insufflated)", "bioavailability": 0.75, "onset": 10, "comeup": 30, "peak": 180, "offset": 240, "half_life": 210}},
        {"warp_amplitude": 0.48, "warp_frequency": 0.45, "symmetry_order": 0.25, "pattern_density": 0.35, "rgb_displacement": 0.78, "hue_shift": 0.35, "feedback_decay": 0.82, "edge_reorg": 0.96, "analog_glitch": 0.88},
        {"NMDA_antag": 0.95, "D2": 0.60, "DA_NE": 0.50},
        175400, "https://psychonautwiki.org/wiki/PCP",
        {
            "dissociative": [
                {"name": "Visual disconnection", "zh_name": "伴随兴奋感的刚性空间解构", "operator": "perceptual_reorganization", "desc": "物体轮廓像素化/块状断裂，深度感极端扭曲并伴随高频信号噪点。"}
            ],
            "visual": [
                {"name": "Frame rate suppression", "zh_name": "离散帧率抽离", "operator": "temporal_persistence", "desc": "世界如同低帧率监控录像般跳帧。"}
            ]
        }
    ),
    "dxm": _make_substance(
        "dxm", "DXM (右美沙芬)", "解离剂", "Morphinan (NMDA Antagonist + SERT Inhibitor + Sigma-1 Agonist)",
        "mg", 300.0, 350.0, 1.7,
        {"oral": {"name": "口服 (Oral)", "bioavailability": 0.70, "onset": 45, "comeup": 75, "peak": 180, "offset": 240, "half_life": 190}},
        {"warp_amplitude": 0.45, "warp_frequency": 0.25, "symmetry_order": 0.38, "pattern_density": 0.45, "rgb_displacement": 0.72, "hue_shift": 0.42, "feedback_decay": 0.90, "edge_reorg": 0.85, "analog_glitch": 0.78},
        {"NMDA_antag": 0.82, "SERT": 0.65},
        179300, "https://psychonautwiki.org/wiki/DXM",
        {
            "visual": [
                {"name": "Double vision", "zh_name": "高原期复视与频闪 (Flanging)", "operator": "temporal_persistence", "desc": "典型的视觉与听觉镶边效应 (Flanging)，强烈重影与帧率分割。"},
                {"name": "Scenery slicing", "zh_name": "机械感场景切片", "operator": "spatial_warping", "desc": "视野分块错位与暗色调梦境几何。"}
            ]
        }
    ),
    "nitrous_oxide": _make_substance(
        "nitrous_oxide", "Nitrous oxide (笑气 / 一氧化二氮)", "解离剂", "Inhalant Gas (NMDA Antagonist)",
        "g", 16.0, 18.0, 2.1,
        {"inhaled": {"name": "吸入 (Inhaled)", "bioavailability": 0.95, "onset": 0.2, "comeup": 0.5, "peak": 1.5, "offset": 3.0, "half_life": 2.0}},
        {"warp_amplitude": 0.30, "warp_frequency": 0.50, "symmetry_order": 0.30, "pattern_density": 0.40, "rgb_displacement": 0.65, "hue_shift": 0.25, "feedback_decay": 0.88, "edge_reorg": 0.78, "analog_glitch": 0.92},
        {"NMDA_antag": 0.85, "GABA": 0.20},
        177100, "https://psychonautwiki.org/wiki/Nitrous_oxide",
        {
            "auditory": [
                {"name": "Auditory distortion", "zh_name": "金属嗡鸣回声 (Wah-Wah)", "operator": "perceptual_reorganization", "desc": "标志性的周期性振荡脉动，同步调制视野边缘噪点与闪烁。"}
            ],
            "visual": [
                {"name": "Visual haze", "zh_name": "视野颗粒化与瞬时复视", "operator": "temporal_persistence", "desc": "极短效的视野像素噪点、隧道视野与致幻剂强烈协同倍增。"}
            ]
        }
    ),

    # ==================== 3. 共情剂 (2种) ====================
    "mdma": _make_substance(
        "mdma", "MDMA", "共情剂", "Entactogen (SERT/NET/DAT Releasing Agent + Weak 5-HT2A)",
        "mg", 100.0, 115.0, 1.7,
        {"oral": {"name": "口服 (Oral)", "bioavailability": 0.80, "onset": 30, "comeup": 30, "peak": 120, "offset": 150, "half_life": 130}},
        {"warp_amplitude": 0.25, "warp_frequency": 0.20, "symmetry_order": 0.20, "pattern_density": 0.25, "rgb_displacement": 0.72, "hue_shift": 0.60, "feedback_decay": 0.76, "edge_reorg": 0.15, "analog_glitch": 0.35},
        {"SERT": 0.95, "DA_NE": 0.65, "5HT2A": 0.25},
        179750, "https://psychonautwiki.org/wiki/MDMA",
        {
            "visual": [
                {"name": "Brightness alteration", "zh_name": "高光柔化与色彩温暖增强", "operator": "chromatic_distortion", "desc": "光源周围产生温暖光晕，伴随眼球震颤引发的高频边缘色散。"},
                {"name": "Tracers", "zh_name": "光斑拖尾", "operator": "temporal_persistence", "desc": "点光源在快速扫视时形成丝滑光带。"}
            ],
            "cognitive": [
                {"name": "Empathy, affection, and sociability enhancement", "zh_name": "强烈共情与亲社会情感放大", "operator": None, "desc": "恐惧消退与人际联结感显著增强。"}
            ]
        }
    ),
    "mda": _make_substance(
        "mda", "MDA", "共情剂", "Entactogen / Psychedelic (SERT/DAT/NET Releaser + 5-HT2A Agonist)",
        "mg", 90.0, 100.0, 1.7,
        {"oral": {"name": "口服 (Oral)", "bioavailability": 0.80, "onset": 35, "comeup": 45, "peak": 160, "offset": 180, "half_life": 150}},
        {"warp_amplitude": 0.55, "warp_frequency": 0.45, "symmetry_order": 0.60, "pattern_density": 0.58, "rgb_displacement": 0.75, "hue_shift": 0.72, "feedback_decay": 0.78, "edge_reorg": 0.35, "analog_glitch": 0.42},
        {"SERT": 0.88, "DA_NE": 0.70, "5HT2A": 0.58},
        176200, "https://psychonautwiki.org/wiki/MDA",
        {
            "visual": [
                {"name": "Geometry", "zh_name": "共情暖光几何与逼真残影", "operator": "pattern_formation", "desc": "相比 MDMA 具有显著更强的 5-HT2A 视觉几何与阴影错觉。"}
            ]
        }
    ),

    # ==================== 4. 兴奋剂 (3种) ====================
    "amphetamine": _make_substance(
        "amphetamine", "Amphetamine (苯丙胺)", "兴奋剂", "Substituted Phenethylamine (DAT/NET Releasing Agent)",
        "mg", 25.0, 30.0, 1.5,
        {"oral": {"name": "口服 (Oral)", "bioavailability": 0.85, "onset": 25, "comeup": 40, "peak": 150, "offset": 210, "half_life": 180}},
        {"warp_amplitude": 0.08, "warp_frequency": 0.65, "symmetry_order": 0.05, "pattern_density": 0.10, "rgb_displacement": 0.38, "hue_shift": 0.15, "feedback_decay": 0.20, "edge_reorg": 0.42, "analog_glitch": 0.45},
        {"DA_NE": 0.95},
        178100, "https://psychonautwiki.org/wiki/Amphetamine",
        {
            "visual": [
                {"name": "Acuity enhancement", "zh_name": "边缘锐化与高对比聚焦", "operator": "perceptual_reorganization", "desc": "注意力高度集中带来的中心视野对比度增强与边缘高频微颤。"}
            ],
            "cognitive": [
                {"name": "Focus enhancement", "zh_name": "执行专注力强化", "operator": None, "desc": "目标导向动力与警觉度显著提升。"}
            ]
        }
    ),
    "caffeine": _make_substance(
        "caffeine", "Caffeine (咖啡因)", "兴奋剂", "Xanthine (Adenosine A1/A2A Antagonist)",
        "mg", 150.0, 180.0, 1.4,
        {"oral": {"name": "口服 (Oral)", "bioavailability": 0.99, "onset": 15, "comeup": 30, "peak": 90, "offset": 180, "half_life": 240}},
        {"warp_amplitude": 0.04, "warp_frequency": 0.50, "symmetry_order": 0.0, "pattern_density": 0.05, "rgb_displacement": 0.22, "hue_shift": 0.08, "feedback_decay": 0.10, "edge_reorg": 0.25, "analog_glitch": 0.28},
        {"DA_NE": 0.45},
        177900, "https://psychonautwiki.org/wiki/Caffeine",
        {
            "visual": [
                {"name": "Brightness alteration", "zh_name": "轻微锐度与微颤抖动", "operator": "chromatic_distortion", "desc": "高剂量下引发轻微视觉高频噪点与边缘清晰度微调。"}
            ]
        }
    ),
    "nicotine": _make_substance(
        "nicotine", "Nicotine (尼古丁)", "兴奋剂", "Pyridine Alkaloid (nAChR Agonist)",
        "mg", 2.0, 2.5, 1.6,
        {"inhaled": {"name": "吸入 (Inhaled)", "bioavailability": 0.90, "onset": 0.5, "comeup": 1.5, "peak": 10, "offset": 25, "half_life": 45}},
        {"warp_amplitude": 0.06, "warp_frequency": 0.45, "symmetry_order": 0.0, "pattern_density": 0.05, "rgb_displacement": 0.25, "hue_shift": 0.10, "feedback_decay": 0.18, "edge_reorg": 0.30, "analog_glitch": 0.32},
        {"DA_NE": 0.50},
        177500, "https://psychonautwiki.org/wiki/Nicotine",
        {
            "visual": [
                {"name": "Acuity enhancement", "zh_name": "瞬时注意聚焦与轻微眩晕漂移", "operator": "perceptual_reorganization", "desc": "胆碱能激活带来的瞬时轮廓强化与头晕微动。"}
            ]
        }
    ),

    # ==================== 5. 大麻素 (1种) ====================
    "cannabis": _make_substance(
        "cannabis", "Cannabis (大麻素 / THC)", "大麻素", "Phytocannabinoid (CB1/CB2 Partial Agonist)",
        "mg", 15.0, 18.0, 1.5,
        {
            "inhaled": {"name": "吸入 (Inhaled)", "bioavailability": 0.35, "onset": 3, "comeup": 10, "peak": 45, "offset": 120, "half_life": 90},
            "oral": {"name": "口服食用 (Edible)", "bioavailability": 0.15, "onset": 60, "comeup": 90, "peak": 180, "offset": 240, "half_life": 180}
        },
        {"warp_amplitude": 0.35, "warp_frequency": 0.25, "symmetry_order": 0.32, "pattern_density": 0.35, "rgb_displacement": 0.45, "hue_shift": 0.55, "feedback_decay": 0.72, "edge_reorg": 0.40, "analog_glitch": 0.48},
        {"CB1": 0.95, "5HT2A": 0.15},
        179500, "https://psychonautwiki.org/wiki/Cannabis",
        {
            "visual": [
                {"name": "Frame rate suppression", "zh_name": "定格动画式帧率延迟", "operator": "temporal_persistence", "desc": "视觉时间采样率降低，并能强力放大致幻剂与解离剂的视觉几何。"},
                {"name": "Colour enhancement", "zh_name": "暖色调饱和度提升与视觉柔雾", "operator": "chromatic_distortion", "desc": "画面色彩饱和且带有胶片颗粒感。"}
            ]
        }
    ),

    # ==================== 6. 一梦剂 / 非典型致幻 (1种) ====================
    "salvinorin_a": _make_substance(
        "salvinorin_a", "Salvinorin A (鼠尾草素 A)", "一梦剂", "Diterpenoid (Selective κ-Opioid Receptor Agonist)",
        "μg", 500.0, 550.0, 2.3,
        {"vaporized": {"name": "气化吸入 (Vaporized)", "bioavailability": 0.85, "onset": 0.3, "comeup": 1.0, "peak": 5.0, "offset": 15.0, "half_life": 8.0}},
        {"warp_amplitude": 0.95, "warp_frequency": 0.85, "symmetry_order": 0.65, "pattern_density": 0.75, "rgb_displacement": 0.80, "hue_shift": 0.40, "feedback_decay": 0.82, "edge_reorg": 0.98, "analog_glitch": 0.90},
        {"KOR": 1.00},
        178600, "https://psychonautwiki.org/wiki/Salvinorin_A",
        {
            "visual": [
                {"name": "Scenery slicing", "zh_name": "拉链式场景切片与书页翻转", "operator": "spatial_warping", "desc": "κ-阿片标志性现象：空间被切成平行条带并发生机械翻页或重力牵引折叠。"},
                {"name": "Ego replacement", "zh_name": "无机物体变形与空间扁平化", "operator": "perceptual_reorganization", "desc": "三维透视坍缩为二维平面拼贴，伴随强烈的本体错位感。"}
            ]
        }
    ),

    # ==================== 7. 抑制类 (2种) ====================
    "ghb": _make_substance(
        "ghb", "GHB (γ-羟基丁酸)", "抑制类", "Depressant (GHB Receptor + GABAB Agonist)",
        "g", 2.0, 2.2, 1.8,
        {"oral": {"name": "口服 (Oral)", "bioavailability": 0.85, "onset": 15, "comeup": 25, "peak": 75, "offset": 90, "half_life": 55}},
        {"warp_amplitude": 0.32, "warp_frequency": 0.15, "symmetry_order": 0.0, "pattern_density": 0.08, "rgb_displacement": 0.48, "hue_shift": 0.22, "feedback_decay": 0.75, "edge_reorg": 0.55, "analog_glitch": 0.35},
        {"GABA": 0.88, "DA_NE": 0.20},
        176900, "https://psychonautwiki.org/wiki/GHB",
        {
            "visual": [
                {"name": "Double vision", "zh_name": "水波柔焦与双重视像", "operator": "temporal_persistence", "desc": "边缘柔化、运动拖影与轻微水平复视。"}
            ]
        }
    ),
    "alcohol": _make_substance(
        "alcohol", "Alcohol (乙醇)", "抑制类", "Depressant (GABAA PAM + NMDA Antagonist)",
        "g", 30.0, 38.0, 1.6,
        {"oral": {"name": "口服 (Oral)", "bioavailability": 0.80, "onset": 10, "comeup": 25, "peak": 60, "offset": 150, "half_life": 110}},
        {"warp_amplitude": 0.28, "warp_frequency": 0.12, "symmetry_order": 0.0, "pattern_density": 0.0, "rgb_displacement": 0.52, "hue_shift": 0.10, "feedback_decay": 0.80, "edge_reorg": 0.65, "analog_glitch": 0.42},
        {"GABA": 0.92, "NMDA_antag": 0.30},
        179200, "https://psychonautwiki.org/wiki/Alcohol",
        {
            "visual": [
                {"name": "Double vision", "zh_name": "复视重影 (Diplopia)", "operator": "temporal_persistence", "desc": "GABA 增强与眼动抑制导致的显著双影错位与延迟拖尾。"},
                {"name": "Acuity suppression", "zh_name": "视觉敏锐度抑制与隧道视野", "operator": "perceptual_reorganization", "desc": "外周视野模糊与散焦。"}
            ]
        }
    )
}

# 默认导出给 reference_library 的 25 种物质记录字典与 SEI 分类树
DEFAULT_25_REFERENCE_RECORDS = SUBSTANCE_DB


def _extend_operator_weights() -> None:
    """为新增的空间立体主义 / 漩涡 / 碎片化算子派生权重。

    不修改原有 5 类算子权重；新算子由“边界解构 / 图案密度 / 对称阶数 /
    时间反馈”这些已有维度组合而成，保持与既有物质档案的连续性。
    """
    for substance in SUBSTANCE_DB.values():
        weights = substance.get("phenomenology_weights")
        if not isinstance(weights, dict):
            continue
        weights.setdefault(
            "cubism",
            round(min(1.0, weights.get("edge_reorg", 0.0) * 0.75 + weights.get("pattern_density", 0.0) * 0.35), 3),
        )
        weights.setdefault(
            "vortex",
            round(min(1.0, weights.get("symmetry_order", 0.0) * 0.55 + weights.get("pattern_density", 0.0) * 0.45), 3),
        )
        weights.setdefault(
            "shatter",
            round(min(1.0, weights.get("edge_reorg", 0.0) * 0.65 + weights.get("feedback_decay", 0.0) * 0.35), 3),
        )


_extend_operator_weights()

DEFAULT_SEI_TAXONOMY = {
    "version": "2026.10-SEI",
    "total_sei_count": 242,
    "total_substance_effect_records": 1619,
    "license": "CC BY-SA 4.0",
    "groups": [
        {"name": "经典致幻剂", "count": 11, "representatives": ["LSD", "Psilocybin mushrooms", "Mescaline", "2C-B", "2C-E", "DMT", "AL-LAD", "LSA", "DOM", "Ibogaine", "Ayahuasca"]},
        {"name": "解离剂", "count": 5, "representatives": ["Ketamine", "MXE", "PCP", "DXM", "Nitrous oxide"]},
        {"name": "共情剂", "count": 2, "representatives": ["MDMA", "MDA"]},
        {"name": "兴奋剂", "count": 3, "representatives": ["Amphetamine", "Caffeine", "Nicotine"]},
        {"name": "大麻素", "count": 1, "representatives": ["Cannabis"]},
        {"name": "一梦剂", "count": 1, "representatives": ["Salvinorin A"]},
        {"name": "抑制类", "count": 2, "representatives": ["GHB", "Alcohol"]}
    ],
    "categories": [
        {
            "id": "visual",
            "name": "视觉 (Visual)",
            "subcategories": [
                {"name": "Visual amplifications", "items": ["Colour enhancement", "Brightness alteration", "Acuity enhancement", "Magnification"]},
                {"name": "Visual suppressions", "items": ["Acuity suppression", "Colour suppression", "Frame rate suppression", "Double vision"]},
                {"name": "Visual distortions", "items": ["Drifting", "Morphing", "Breathing", "Melting", "Colour shifting", "Depth perception distortions", "Perspective distortion", "Scenery slicing", "Symmetrical texture repetition", "Tracers", "After images", "Diffraction"]},
                {"name": "Geometric patterns", "items": ["Geometry (Level 1-8A/8B)"]},
                {"name": "Hallucinatory states", "items": ["Transformations", "Internal hallucination", "External hallucination", "Perspective hallucination", "Scenarios and plots"]}
            ]
        },
        {
            "id": "dissociative",
            "name": "解离 (Dissociative)",
            "subcategories": [
                {"name": "Disconnective effects", "items": ["Visual disconnection", "Cognitive disconnection", "Physical disconnection", "Hole spaces and voids", "Derealization", "Depersonalization"]}
            ]
        },
        {
            "id": "cognitive",
            "name": "认知心理 (Cognitive)",
            "subcategories": [
                {"name": "Cognitive states", "items": ["Analysis enhancement", "Time distortion", "Memory suppression", "Thought connectivity", "Focus enhancement"]}
            ]
        },
        {
            "id": "transpersonal",
            "name": "超个人 (Transpersonal)",
            "subcategories": [
                {"name": "Existential states", "items": ["Ego dissolution", "Ego replacement", "Unity and interconnectedness", "Identity alteration"]}
            ]
        },
        {
            "id": "multisensory",
            "name": "多感官 (Multisensory)",
            "subcategories": [
                {"name": "Cross-modal effects", "items": ["Synaesthesia", "Autonomous sensory meridian response"]}
            ]
        }
    ]
}