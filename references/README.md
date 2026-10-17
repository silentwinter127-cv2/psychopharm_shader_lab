# PsychonautWiki 物质 × 主观效应参考集

本目录是 [PsychonautWiki](https://psychonautwiki.org/) 的结构化摘录，用于给
`psychopharm_shader_lab` 提供“物质 → 主观效应 → 现象学算子”的参考层。

- **25 种物质**：经典致幻剂、解离剂、共情剂 / 兴奋剂、大麻素、一梦剂与常见抑制 / 兴奋物质。
- **1,619 条物质-效应记录**：来自各物质页面的 `Subjective effects` 章节。
- **242 条效应分类条目**：来自 PsychonautWiki 的
  [Subjective Effect Index](https://psychonautwiki.org/wiki/Subjective_effect_index)。
- 每条记录保留页面修订号、抓取时间、来源 URL 与 CC BY-SA 4.0 许可信息。

> **这不是临床资料。** 主观效应索引由使用者报告与社区编辑整理而成，属于轶事性资料。
> 效应会随剂量、给药途径、心境、环境、耐受与药物相互作用显著变化。本参考集不包含剂量表，
> 也不构成任何用药、诊断或治疗建议。许多列出的物质在多数司法辖区属于管制物质。

---

## 文件

| 文件 | 内容 |
| --- | --- |
| `substance_effects.json` | 完整结构化数据：物质、分类效应、注释、来源、现象学标签 |
| `substance_effects.md` | 人读版参考集：总览表 + 每种物质的分类效应清单 |
| `effect_taxonomy.json` | SEI 效应分类树 + 构建期使用的名称索引 |
| `effect_taxonomy.md` | 人读版分类树 |
| `README.md` | 本文件：方法、许可、限制 |

---

## 收录范围

| 组别 | 物质 |
| --- | --- |
| psychedelic | LSD、Psilocybin mushrooms、Mescaline、2C-B、2C-E、DMT、4-AcO-DMT、AL-LAD、DOM、Ibogaine、Ayahuasca |
| dissociative | Ketamine、Methoxetamine (MXE)、PCP、Dextromethorphan (DXM)、Nitrous oxide |
| entactogen | MDMA、MDA |
| stimulant | Amphetamine、Caffeine、Nicotine |
| cannabinoid | Cannabis |
| oneirogen | Salvinorin A |
| depressant | GHB、Alcohol |

选择标准：PsychonautWiki 上具有较完整 `Subjective effects` 结构、且在视觉 / 知觉现象学上
有区分度的物质；同时加入少数常见对照物质（咖啡因、尼古丁、酒精、GHB），用于比较
“有视觉效应”和“以认知 / 身体效应为主”的差异。

---

## 数据是怎么生成的

脚本：[`../tools/build_effect_reference.py`](../tools/build_effect_reference.py)

1. 通过 MediaWiki API（`action=query` / `action=parse`）读取物质页与
   `List/effects` 的 wikitext。
2. 只解析 `== Subjective effects ==` 章节中的
   `{{effects/physical|...}}`、`{{effects/visual|...}}`、`{{effects/cognitive|...}}`、
   `{{effects/auditory|...}}`、`{{effects/multisensory|...}}`、
   `{{effects/transpersonal|...}}`、`{{effects/disconnective|...}}`、
   `{{effects/aftereffects|...}}` 等模板块。
3. 对每个条目只取“主效应”链接（`*'''[[Effect::X]]''' - 描述` 中 `-` 之前的部分），
   避免把描述里顺带提到的其他效应算进该物质的主清单。
4. 用 MediaWiki redirects 与人工别名表统一拼写差异（`Colour` / `Color`、
   单复数、`Ego death` / `Memory suppression` 等）。
5. 将效应名与 `List/effects` 分类树匹配，得到 `in_sei`、`sei_category`、
   `sei_subcategory`；未收录的效应保留并标记。
6. 为每个物质生成 5 类现象学标签：

   | 标签 | 对应项目中的算子 | 典型效应 |
   | --- | --- | --- |
   | `pattern_formation` | 几何化与图案生成 | Geometry、Symmetrical texture repetition、Environmental patterning |
   | `spatial_warping` | 空间扭曲与流动 | Drifting、Perspective distortion、Scenery slicing |
   | `chromatic_distortion` | 色彩分离与光谱异常 | Color enhancement、Color shifting、Diffraction |
   | `temporal_persistence` | 视觉残留与时间叠影 | Tracers、After images、Double vision |
   | `perceptual_reorganization` | 边界解构与空间重组 | Visual disconnection、Depth perception distortions、Ego dissolution |

   `strength` 是同一物质内部的相对命中数（不跨物质比较），并对“标志性效应”做加成；
   它只是艺术映射的启发式，不是药效强度、剂量或临床严重度。
7. 输出 JSON / Markdown，并把来源修订号写入每个物质条目。

重新生成：

```powershell
cd E:\psychopharm_shader_lab
.\.venv\Scripts\python.exe tools\build_effect_reference.py
```

生成后需要重启 `app.py`（参考集在进程启动时加载），或在 API 之外直接读取 JSON 文件。

只重新渲染（复用已有分类树，仍需联网抓物质页）：

```powershell
.\.venv\Scripts\python.exe tools\build_effect_reference.py --skip-taxonomy
```

---

## 数据结构

`substance_effects.json` 顶层：

```json
{
  "meta": {
    "title": "PsychonautWiki Substance × Subjective Effect Reference Set",
    "version": "1.0.0",
    "generated_at": "...",
    "source": "https://psychonautwiki.org/wiki/Subjective_effect_index",
    "license": "CC BY-SA 4.0",
    "disclaimer": "...",
    "substance_count": 25,
    "effect_count": 1619
  },
  "phenomenology_rules": { "...": { "needles": ["..."], "label": "..." } },
  "substances": [ ... ]
}
```

单个物质（节选）：

```json
{
  "id": "lsd",
  "title": "LSD",
  "name": "LSD",
  "aliases": ["Lysergide", "LSD-25", "L", "Lucy", "Acid"],
  "group": "psychedelic",
  "family": "lysergamide",
  "psychoactive_class": ["psychedelic"],
  "chemical_class": ["lysergamide"],
  "summary": "...",
  "effect_counts": { "visual": 23, "cognitive": 34, "physical": 27, "total": 91 },
  "phenomenology": {
    "tags": ["pattern_formation", "spatial_warping", "chromatic_distortion", "temporal_persistence", "perceptual_reorganization"],
    "primary_tags": ["pattern_formation", "temporal_persistence", "perceptual_reorganization"],
    "strength": { "pattern_formation": 1.0, "...": 0.83 },
    "evidence": { "pattern_formation": ["Environmental patterning", "..."], "...": [] }
  },
  "effects": [
    {
      "name": "Geometry",
      "display_name": "Geometry",
      "target": "Geometry",
      "anchor": null,
      "category": "visual",
      "subcategory": "geometry",
      "depth": 1,
      "note": "...",
      "in_sei": true,
      "sei_category": "visual",
      "sei_subcategory": "geometry"
    }
  ],
  "source": {
    "url": "https://psychonautwiki.org/wiki/LSD",
    "pageid": 7289,
    "revid": 169966,
    "timestamp": "2025-12-11T08:07:17Z",
    "license": "CC BY-SA 4.0"
  }
}
```

`category` 取值：`visual`、`cognitive`、`physical`、`auditory`、`multisensory`、
`transpersonal`、`disconnective`、`tactile`、`smell_taste`、`aftereffects`、`other`。

---

## 在项目里怎么用

加载层：[`../reference_library.py`](../reference_library.py)

```python
from reference_library import get_reference, list_reference_summaries

lsd = get_reference("lsd")
print(lsd["phenomenology"]["primary_tags"])
print([e["name"] for e in lsd["effects"] if e["category"] == "visual"])
```

HTTP API：

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/references` | 25 个物质的摘要 + 元数据 |
| GET | `/api/references/{id}` | 单个物质的完整效应档案 |
| GET | `/api/reference-taxonomy` | SEI 效应分类树 |

前端页面顶部新增“效应参考集”按钮，按物质浏览分类效应；效应名悬停可查看 PW 的简短描述，
虚线标签表示该效应未收录于 SEI 分类树。参考集不参与 PK-PD 数值计算，只是独立的检索 / 对照层。

> 项目后来新增了 06–08 三个几何算子（`cubism` / `vortex` / `shatter`），由 `archives.py`
> 与着色器独立定义；本参考集仍使用 5 类核心标签，不强行改写已有 SEI 分类与主标签排序。

---

## 许可与署名

PsychonautWiki 的内容采用
[Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/)
许可。本目录中的效应名称、简短描述与分类树均改编自 PsychonautWiki 贡献者整理的内容。

- 来源首页：<https://psychonautwiki.org/wiki/Subjective_effect_index>
- 物质页面：见每个条目 `source.url`
- 修订号：见每个条目 `source.revid`
- 本参考集的整理代码：与本项目其余代码相同，供艺术 / 研究演示使用

再分发本目录内容时，请保留署名、许可链接与修订号，并以相同许可共享。

---

## 已知限制

- 效应为**主观报告**，不是临床终点；不同剂量、途径、个体与场景下差异很大。
- 某些页面把同一效应同时列在急性效应与后效应中；本参考集保留分类差异，因此总记录数
  大于“唯一效应名”数量。
- 解析依赖页面模板结构；PsychonautWiki 页面改版后需要重新运行构建脚本。
- 少量效应名未收录于 SEI 分类树（如 `Neurogenesis`、`Neurotoxicity`），以 `in_sei: false` 保留。
- `strength` 为启发式标签强度，不能用于比较不同物质之间的药效强弱。
- 本参考集有意不包含剂量、给药操作、合成或获取信息。
