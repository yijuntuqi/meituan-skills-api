"""
酒旅查询路由（异步任务模式，因查询耗时 1-2 分钟）
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..skills.travel import travel_skill
from ..task_store import task_store

router = APIRouter(prefix="/api/travel", tags=["酒旅"])


class TravelQueryRequest(BaseModel):
    query: str
    origin_query: Optional[str] = None
    city: Optional[str] = None
    raw_json: bool = False


async def _run_travel_query(task_id: str, req: TravelQueryRequest):
    """后台执行酒旅查询"""
    task_store.update_task(task_id, status="running")
    try:
        result = await travel_skill.query(
            query=req.query,
            origin_query=req.origin_query,
            city=req.city,
            raw_json=req.raw_json,
        )
        if result.ok:
            # 尝试解析 JSON，否则返回原始文本
            parsed = result.parse_json()
            task_store.update_task(
                task_id,
                status="success",
                result={"json": parsed, "raw": result.stdout},
            )
        else:
            task_store.update_task(
                task_id,
                status="failed",
                error=result.stderr or result.stdout or "查询失败",
            )
    except Exception as e:
        task_store.update_task(task_id, status="failed", error=str(e))


@router.post("/query", summary="提交酒旅查询（异步）")
async def submit_travel_query(req: TravelQueryRequest, background_tasks: BackgroundTasks):
    task_id = task_store.create_task()
    background_tasks.add_task(_run_travel_query, task_id, req)
    return {"task_id": task_id, "status": "pending", "message": "查询已提交，约 1-2 分钟后通过 /result/{task_id} 获取结果"}


@router.get("/result/{task_id}", summary="查询酒旅任务结果")
async def get_travel_result(task_id: str):
    task = task_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task
