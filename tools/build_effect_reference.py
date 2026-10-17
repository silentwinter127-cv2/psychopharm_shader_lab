# tools/build_effect_reference.py
import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from archives import SUBSTANCE_DB, DEFAULT_SEI_TAXONOMY
from reference_library import OPERATOR_SEI_MAPPING


def build_references():
    ref_dir = ROOT_DIR / "references"
    ref_dir.mkdir(exist_ok=True)

    # 1. 生成 substance_effects.json
    substances_payload = {
        "version": "2026.10",
        "license": "CC BY-SA 4.0",
        "substance_count": len(SUBSTANCE_DB),
        "substances": list(SUBSTANCE_DB.values())
    }
    (ref_dir / "substance_effects.json").write_text(
        json.dumps(substances_payload, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    # 2. 生成 effect_taxonomy.json
    (ref_dir / "effect_taxonomy.json").write_text(
        json.dumps(DEFAULT_SEI_TAXONOMY, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    # 3. 生成人读版总览 substance_effects.md
    md_lines = [
        "# 精神活性物质主观效应参考集 (PsychonautWiki SEI Reference)",
        "",
        "- **25 种代表物质**",
        "- **1,619 条物质-效应关联记录**",
        "- **242 条 SEI 效应分类条目**",
        "- **开源许可**：CC BY-SA 4.0",
        "",
        "## 五大现象学算子自动映射规则",
        ""
    ]
    for op_id, spec in OPERATOR_SEI_MAPPING.items():
        md_lines.append(f"- `{op_id}` (**{spec['name']}**)：{spec['summary']}")

    md_lines.extend(["", "## 25 种物质分类效应档案", ""])
    for sub in SUBSTANCE_DB.values():
        meta = sub.get("metadata", {})
        md_lines.append(f"### {sub['name']} (`{sub['id']}`)")
        md_lines.append(f"- **组别**：{sub['group']} | **药理分类**：{sub['class']}")
        md_lines.append(f"- **标准剂量**：{sub['standard_dose']} {sub['unit']} | **PW 修订号**：`#{meta.get('pw_revision_id')}` | **来源**：{meta.get('source_url')}")
        for eff in sub.get("effects", []):
            op_tag = f" → `{eff['operator']}`" if eff.get("operator") else ""
            md_lines.append(f"  - **[{eff['category']}] {eff['zh_name']} ({eff['name']})**{op_tag}：{eff['description']}")
        md_lines.append("")

    (ref_dir / "substance_effects.md").write_text("\n".join(md_lines), encoding="utf-8")
    print(f"[OK] 已生成参考集文件至: {ref_dir}")


if __name__ == "__main__":
    build_references()