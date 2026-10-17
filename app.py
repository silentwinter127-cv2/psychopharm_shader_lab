# app.py
"""Psychopharmacological Art Shader Lab —— FastAPI 后端入口。

运行方式（任选其一）：
    python app.py                 # 127.0.0.1:8000
    python app.py --port 8010     # 自定义端口
    python app.py --reload        # 开发模式自动重载
    uvicorn app:app --reload      # 等价的标准 uvicorn 用法

静态资源使用相对本文件的绝对路径，因此从任意工作目录启动都可以正常工作。
"""
from __future__ import annotations

import argparse
import platform
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from archives import PHENOMENON_ARCHIVES, SUBSTANCE_DB
from pk_pd_engine import IngestionEvent, PKPDEngine
from reference_library import (
    REFERENCE_META,
    get_reference,
    get_taxonomy,
    list_reference_summaries,
    reference_available,
    reference_count,
)

APP_VERSION = "1.3.0"
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

if not STATIC_DIR.is_dir():
    raise RuntimeError(f"静态资源目录不存在: {STATIC_DIR}")

app = FastAPI(
    title="Psychopharmacological Art Shader Lab",
    version=APP_VERSION,
    description="以精神药理学为参数系统、以视觉心理学为表现语言的艺术着色器后端",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class SimulationRequest(BaseModel):
    """PK-PD 仿真请求。所有字段都有边界，避免异常请求拖垮时间轴采样。"""

    ingestions: List[IngestionEvent] = Field(default_factory=list, max_length=64)
    current_time_minutes: float = Field(default=120.0, ge=0.0, le=1440.0)
    timeline_duration_minutes: float = Field(default=600.0, ge=60.0, le=1440.0)


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    # 关闭缓存，保证改动 index.html 后刷新即可看到最新界面。
    return FileResponse(
        STATIC_DIR / "index.html",
        media_type="text/html",
        headers={"Cache-Control": "no-store, max-age=0"},
    )


@app.get("/api/health")
async def health() -> Dict[str, Any]:
    """用于冒烟测试 / 排障的健康检查。"""
    return {
        "status": "ok",
        "version": APP_VERSION,
        "python": platform.python_version(),
        "substances": len(SUBSTANCE_DB),
        "archives": len(PHENOMENON_ARCHIVES),
        "reference_substances": reference_count(),
        "static_dir": str(STATIC_DIR),
    }


@app.get("/api/metadata")
async def get_metadata() -> Dict[str, Any]:
    """获取所有物质药理数据库与视觉现象学研究档案。"""
    return {
        "version": APP_VERSION,
        "substances": SUBSTANCE_DB,
        "archives": PHENOMENON_ARCHIVES,
        "reference": {
            "available": reference_available(),
            "substance_count": reference_count(),
        },
    }


@app.get("/api/references")
async def get_references() -> Dict[str, Any]:
    """PsychonautWiki 物质 × 主观效应参考集（列表摘要）。"""
    if not reference_available():
        return {
            "available": False,
            "meta": REFERENCE_META,
            "substances": [],
            "taxonomy": {"effect_count": 0},
        }
    return {
        "available": True,
        "meta": REFERENCE_META,
        "substances": list_reference_summaries(),
        "taxonomy": {"effect_count": get_taxonomy().get("effect_count", 0)},
    }


@app.get("/api/references/{substance_id}")
async def get_reference_detail(substance_id: str) -> Dict[str, Any]:
    """单个物质的完整效应档案。"""
    item = get_reference(substance_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"参考档案中不存在物质: {substance_id}")
    return item


@app.get("/api/reference-taxonomy")
async def get_reference_taxonomy() -> Dict[str, Any]:
    """PsychonautWiki 主观效应分类树（SEI）。"""
    return get_taxonomy()


@app.post("/api/simulate")
async def simulate_pk_pd(req: SimulationRequest) -> Dict[str, Any]:
    """根据摄入记录计算时间轴曲线与当前时刻的 GLSL 着色器参数。"""
    current_state = PKPDEngine.evaluate_at_time(req.ingestions, req.current_time_minutes)
    timeline = PKPDEngine.simulate_timeline_series(
        req.ingestions,
        duration_minutes=req.timeline_duration_minutes,
        step_minutes=5.0,
    )
    return {
        "version": APP_VERSION,
        "current_state": current_state,
        "timeline": timeline,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Psychopharmacological Art Shader Lab")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址（默认 127.0.0.1）")
    parser.add_argument("--port", type=int, default=8000, help="监听端口（默认 8000）")
    parser.add_argument("--reload", action="store_true", help="开发模式：代码改动后自动重载")
    args = parser.parse_args()

    import uvicorn

    if args.reload:
        # --reload 需要 import string；app_dir 保证从任意工作目录都能找到 app.py。
        uvicorn.run(
            "app:app",
            host=args.host,
            port=args.port,
            reload=True,
            reload_dirs=[str(BASE_DIR)],
            app_dir=str(BASE_DIR),
            log_level="info",
        )
    else:
        uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
